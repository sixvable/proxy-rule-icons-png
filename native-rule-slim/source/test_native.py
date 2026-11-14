import copy
import hashlib
import ipaddress
import json
import re
import unittest

import yaml

from build_native import ALI, ROOT, build_config, load_source, render, simulate_merge, validate


class NativeOverrideTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.source = load_source()
        cls.cfg = build_config(cls.source)
        cls.groups = {g['name']: g for g in cls.cfg['proxy-groups']}

    def test_complete_graph_and_original_order(self):
        validate(self.cfg)
        self.assertEqual([g['name'] for g in self.cfg['proxy-groups']],
                         [g['name'] for g in self.source['groups']])
        self.assertEqual(len(self.groups), 139)
        self.assertEqual(self.cfg['rules'], self.source['rules'])
        self.assertNotIn('AppleTV-Media-IPv6', self.groups)
        self.assertNotIn('Global-CDN', self.groups)

    def test_no_include_all_explicit_union_or_airport_provider(self):
        for g in self.groups.values():
            if g.get('include-all'):
                self.assertNotIn('proxies', g)
            self.assertNotIn('use', g)
        self.assertNotIn('proxies', self.cfg)
        self.assertNotIn('proxy-providers', self.cfg)

    def test_all_native_names_remain_available(self):
        manual = self.groups['AllServer']
        self.assertTrue(manual['include-all'])
        self.assertNotIn('filter', manual)
        self.assertNotIn('proxies', manual)

    def test_regions_handle_multiple_airport_naming_styles(self):
        samples = {
            'HongKong': ['香港 01', 'hk 2', '🇭🇰 Node', 'Hong Kong AnyTLS'],
            'America': ['美国 01', 'us 1', '🇺🇸 Test', 'Los Angeles LAX'],
            'TaiWan': ['台湾 1', '台灣 2', 'Taiwan 3', 'TW 4'],
            'Japan': ['日本 1', 'JP 2', 'Tokyo 3'],
            'Singapore': ['新加坡 1', 'SG 2', 'Singapore 3'],
        }
        for name, nodes in samples.items():
            pattern = re.compile(self.groups[name]['filter'])
            for node in nodes:
                self.assertRegex(node, pattern, name)
            self.assertIsNone(pattern.search('官网 ' + nodes[0]))

    def test_auto_and_fallback_are_visible_and_selectable_from_business(self):
        for name in ['HK-Auto', 'HK-FallBack', 'US-Auto', 'US-FallBack']:
            self.assertFalse(self.groups[name]['hidden'])
            self.assertIn(name, self.groups['Proxy']['proxies'])
            self.assertIn(name, self.groups['Video-AppleTV']['proxies'])
            self.assertIn(name, self.groups['DNS-Global']['proxies'])

    def test_dns_global_offers_every_region_without_include_all(self):
        dns = self.groups['DNS-Global']
        for group in self.groups.values():
            if group.get('include-all') and group['type'] == 'select':
                self.assertIn(group['name'], dns['proxies'])
        self.assertNotIn('include-all', dns)
        self.assertNotIn('filter', dns)
        self.assertEqual(dns['proxies'][0], 'HongKong')

    def test_direct_defaults_and_rule_priority_preserved(self):
        for name in ['Video-AppleTV', 'DNS-China', 'Country-China']:
            self.assertEqual(self.groups[name]['proxies'][0], 'DIRECT')
        rules = self.cfg['rules']
        apple = next(i for i, r in enumerate(rules) if ',Video-AppleTV' in r)
        protection = next(i for i, r in enumerate(rules) if ',Protection-HTTPDNS' in r)
        youtube = next(i for i, r in enumerate(rules) if ',Video-YouTube' in r)
        self.assertLess(protection, apple)
        self.assertGreater(rules.index('GEOIP,CN,Country-China'), youtube)
        self.assertFalse(any('DST-PORT,53' in r or 'DST-PORT,853' in r for r in rules))

    def test_dns_only_inherits_node_resolvers(self):
        for proxy_dns in [None, ['udp://192.0.2.53', 'https://dns.private.invalid/dns-query']]:
            original_dns = {
                'nameserver': ['192.0.2.54'],
                'default-nameserver': ['192.0.2.55'],
                'nameserver-policy': {'+.private.invalid': '192.0.2.56'},
                'fallback': ['192.0.2.57'],
                'fallback-filter': {'geoip': True, 'domain': ['+.example.invalid']},
                'fake-ip-filter': ['+.old.invalid'],
                'follow-rule': False,
                'skip-cert-verify': True,
                'ipv6': False,
            }
            if proxy_dns is not None:
                original_dns['proxy-server-nameserver'] = proxy_dns
            original = {'dns': original_dns}
            snapshot = copy.deepcopy(original)
            merged = simulate_merge(original, self.cfg)
            expected = copy.deepcopy(self.cfg['dns'])
            if proxy_dns is not None:
                expected['proxy-server-nameserver'] = proxy_dns
            self.assertEqual(merged['dns'], expected)
            self.assertEqual(original, snapshot)

    def test_original_nodes_and_providers_unchanged_across_shapes(self):
        fixtures = [
            {'proxies': [{'name': 'renamed-A', 'type': 'ss', 'server': 'a.invalid'}]},
            {'proxy-providers': {'unrelated-source': {'url': 'https://never-fetch.invalid/once', 'path': 'saved.yaml'}}},
            {'proxies': [{'name': 'fourth-airport-01', 'server': '198.51.100.1'}],
             'proxy-providers': {'another': {'path': 'cache.yaml'}}},
        ]
        for base in fixtures:
            base.update({'proxy-groups': [{'name': 'Proxy', 'type': 'select', 'proxies': ['DIRECT']}],
                         'rules': ['MATCH,DIRECT'], 'hosts': {'old.invalid': '192.0.2.1'},
                         'rule-providers': {'old-rule': {'url': 'https://never-fetch.invalid/rule'}}})
            merged = simulate_merge(base, self.cfg)
            for key in ['proxies', 'proxy-providers']:
                self.assertEqual(merged.get(key), base.get(key))
            self.assertEqual(merged['proxy-groups'], self.cfg['proxy-groups'])
            self.assertEqual(merged['rule-providers'], self.cfg['rule-providers'])
            self.assertEqual(merged['hosts'], self.cfg['hosts'])
            self.assertEqual(merged['rules'], self.cfg['rules'])

    def test_rendered_merge_directives_match_declared_behavior(self):
        text = render(self.cfg)
        self.assertEqual(yaml.safe_load(text), self.cfg)
        self.assertRegex(text, r'(?m)^dns:\s*$')
        self.assertNotRegex(text, r'(?m)^dns:.*#!replace')
        for key in ['proxy-groups', 'rule-providers', 'rules', 'hosts', 'proxy-hosts']:
            self.assertRegex(text, rf'(?m)^{key}:.*#!replace$')
        for key in ['nameserver', 'default-nameserver', 'nameserver-policy', 'fallback', 'fallback-filter', 'fake-ip-filter']:
            self.assertRegex(text, rf'(?m)^  {key}:.*#!replace$')
        self.assertNotIn('#SUBSCRIBED', text)

    def test_dns_servers_route_to_the_expected_public_ip_lists(self):
        china = [ipaddress.ip_network(s) for s in (ROOT / 'inputs/dns-china-ip.txt').read_text().splitlines() if s and not s.startswith('#')]
        global_ = [ipaddress.ip_network(s) for s in (ROOT / 'inputs/dns-global-ip.txt').read_text().splitlines() if s and not s.startswith('#')]
        for ip in ['223.5.5.5', '223.6.6.6']:
            self.assertTrue(any(ipaddress.ip_address(ip) in n for n in china))
        for ip in ['8.8.8.8', '1.1.1.1']:
            self.assertFalse(any(ipaddress.ip_address(ip) in n for n in china))
            self.assertTrue(any(ipaddress.ip_address(ip) in n for n in global_))
        self.assertEqual(self.cfg['dns']['default-nameserver'], ALI)
        self.assertTrue(self.cfg['dns']['follow-rule'])

    def test_no_mihomo_only_resolver_routing_syntax(self):
        dns = self.cfg['dns']
        self.assertFalse({'respect-rules', 'direct-nameserver', 'direct-nameserver-follow-policy', 'proxy-server-nameserver'} & dns.keys())
        for key in ['nameserver', 'default-nameserver']:
            for server in dns[key]:
                self.assertNotIn('#', server)

    def test_rule_changes_preserve_dns_and_group_settings_from_v8(self):
        baseline = json.loads((ROOT / 'inputs/baseline-settings.json').read_text())
        self.assertEqual(self.cfg['dns'], baseline['dns'])
        digest = hashlib.sha256(json.dumps(self.cfg['proxy-groups'], sort_keys=True, ensure_ascii=False).encode()).hexdigest()
        self.assertEqual(digest, baseline['proxy_groups_sha256'])

    def test_routing_still_uses_indexed_mrs_without_classical_sets(self):
        self.assertFalse(any('GEOSITE,' in r.upper() for r in self.cfg['rules']))
        for p in self.cfg['rule-providers'].values():
            self.assertEqual(p['format'], 'mrs')
            self.assertIn(p['behavior'], ['domain', 'ipcidr'])


if __name__ == '__main__':
    unittest.main()
