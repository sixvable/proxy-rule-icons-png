import copy
import json
import re
import unittest
from pathlib import Path
from unittest.mock import patch

import yaml
from prepare_local_airport import prepare, load
from build import graph_check, provider_variant

RECIPE = json.loads((Path(__file__).parent / 'recipe.json').read_text())
OVERRIDE = provider_variant({'proxy-groups': RECIPE['groups']})
GROUPS = {g['name']: g for g in OVERRIDE['proxy-groups']}


def node(name):
    return {'name': name, 'type': 'http', 'server': '192.0.2.1', 'port': 443}


class GenericAirportTests(unittest.TestCase):
    def adapt(self, nodes, dns=None):
        source = {'proxies': nodes, 'dns': dns or {'nameserver': ['192.0.2.53']}}
        with patch('socket.socket', side_effect=AssertionError('Network is forbidden')):
            profile, cache, count = prepare(yaml.safe_dump(source), 'Airport-example.yaml', reserved_names=GROUPS)
        self.assertEqual(load(cache)['proxies'], nodes)
        self.assertEqual(load(profile)['dns'], source['dns'])
        graph_check(OVERRIDE['proxy-groups'])
        self.assertEqual(set(load(profile)['proxy-providers']), {'Airport'})
        return count

    def test_unrelated_fourth_airport(self):
        self.assertEqual(self.adapt([node('ExampleAir 香港 A'), node('ExampleAir USA B')]), 2)

    def test_renamed_added_deleted_nodes_do_not_change_shared_override(self):
        original = copy.deepcopy(OVERRIDE)
        for names in [['NewCo Hong Kong One'], ['NewCo Hong Kong Renamed', 'NewCo Japan Two'], ['NewCo Japan Two']]:
            self.adapt([node(n) for n in names])
        self.assertEqual(OVERRIDE, original)

    def test_missing_regions_do_not_create_dangling_references(self):
        self.adapt([node('ExampleAir Japan Only')])
        self.assertFalse(re.search(GROUPS['HongKong']['filter'], 'ExampleAir Japan Only'))
        self.assertIn('DIRECT', GROUPS['HongKong']['proxies'])

    def test_unknown_region_still_available_in_allserver(self):
        self.adapt([node('Unclassified Endpoint A')])
        self.assertTrue(re.search(GROUPS['AllServer']['filter'], 'Unclassified Endpoint A'))

    def test_same_provider_alias_has_distinct_cache_paths(self):
        text = yaml.safe_dump({'proxies': [node('Generic HK')]})
        paths = [load(prepare(text, 'Airport-' + str(i) + '.yaml')[0])['proxy-providers']['Airport']['path'] for i in range(4)]
        self.assertEqual(len(set(paths)), 4)

    def test_quoted_keys_and_yaml_anchors_preserve_settings(self):
        text = "'dns': &settings {nameserver: [192.0.2.53]}\nhosts: {test.invalid: 192.0.2.2}\n'proxies': [{name: Generic-HK, type: http, server: 192.0.2.3, port: 443}]\n"
        profile, _, _ = prepare(text, 'Airport-example.yaml')
        for key in ['dns', 'hosts']:
            self.assertEqual(load(profile)[key], load(text)[key])

    def test_subscription_directives_never_survive(self):
        text = '#SUBSCRIBED https://example.invalid/consumed-token\n' + yaml.safe_dump({'proxies': [node('Generic HK')]})
        profile, cache, _ = prepare(text, 'Airport-example.yaml')
        self.assertNotIn('consumed-token', profile + cache)
        self.assertNotIn('#SUBSCRIBED', profile + cache)

    def test_external_provider_requires_explicit_local_cache(self):
        text = yaml.safe_dump({'proxy-providers': {'Original': {'url': 'https://example.invalid/consumed-token'}}})
        with self.assertRaisesRegex(ValueError, 'existing provider caches'):
            prepare(text, 'Airport-example.yaml')
        profile, cache, count = prepare(text, 'Airport-example.yaml', [yaml.safe_dump({'proxies': [node('NewCo HK')]})])
        self.assertEqual(count, 1)
        self.assertNotIn('consumed-token', profile + cache)
        self.assertEqual(set(load(profile)['proxy-providers']['Airport']), {'path'})

    def test_empty_and_conflicting_nodes_fail_without_download(self):
        with self.assertRaisesRegex(ValueError, 'No cached nodes'):
            prepare('proxies: []', 'Airport-example.yaml')
        first = node('Duplicate')
        second = dict(first, port=8443)
        with self.assertRaisesRegex(ValueError, 'Conflicting duplicate'):
            prepare(yaml.safe_dump({'proxies': [first, second]}), 'Airport-example.yaml')

    def test_group_collisions_and_removed_dialer_groups_fail(self):
        with self.assertRaisesRegex(ValueError, 'collides'):
            self.adapt([node('HongKong')])
        with self.assertRaisesRegex(ValueError, 'original policy group'):
            self.adapt([dict(node('NewCo HK'), **{'dialer-proxy': 'Removed-Group'})])

    def test_all_explicit_members_are_groups_or_builtins(self):
        for group in GROUPS.values():
            self.assertLessEqual(set(group.get('proxies', [])), set(GROUPS) | {'DIRECT', 'REJECT', 'REJECT-DROP'})
            self.assertLessEqual(set(group.get('use', [])), {'Airport'})


if __name__ == '__main__':
    unittest.main()
