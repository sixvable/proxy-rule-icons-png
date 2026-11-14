import unittest
from prepare_provider_profile import prepare, parse_yaml


class ProviderProfileTests(unittest.TestCase):
    def test_preserves_airport_settings_and_node_credentials(self):
        original = '''#SUBSCRIBED https://example.invalid/subscription?token=PRIVATE_EXAMPLE
ipv6: true
dns:
  nameserver: [192.0.2.53]
  nameserver-policy:
    '*.internal.example': 192.0.2.54
hosts:
  private.example: 192.0.2.1
proxies:
  - {name: HK-1, type: ss, server: example.invalid, port: 443, cipher: aes-128-gcm, password: test-only}
proxy-groups:
  - {name: Old, type: select, proxies: [HK-1]}
rules:
  - MATCH,Old
'''
        profile, cache, count = prepare(original, 'Airport-test.yaml')
        source, result = parse_yaml(original), parse_yaml(profile)
        for key in ['dns', 'hosts', 'ipv6']:
            self.assertEqual(source[key], result[key])
        self.assertEqual(parse_yaml(cache)['proxies'], source['proxies'])
        self.assertEqual(count, 1)
        self.assertEqual(set(result['proxy-providers']['Airport']), {'path'})
        self.assertNotIn('PRIVATE_EXAMPLE', profile + cache)
        self.assertEqual(result['proxy-providers']['Airport']['path'], './proxy-providers/Airport-test.yaml')
        self.assertNotIn('#SUBSCRIBED', profile)
        self.assertNotIn('proxies', result)
        self.assertEqual(result['proxy-groups'][0]['use'], ['Airport'])

    def test_local_nodes_work_without_any_subscription_link(self):
        original = 'dns: {nameserver: [192.0.2.53]}\nproxies:\n  - {name: HK-1, type: http, server: example.invalid, port: 443}\n'
        profile, cache, count = prepare(original, 'Airport-test.yaml')
        self.assertEqual(count, 1)
        self.assertEqual(parse_yaml(profile)['proxy-providers']['Airport'],
                         {'path': './proxy-providers/Airport-test.yaml'})
        self.assertEqual(parse_yaml(cache)['proxies'], parse_yaml(original)['proxies'])

    def test_duplicate_expired_directives_never_survive_in_profile_or_cache(self):
        original = ('#SUBSCRIBED https://example.invalid/consumed-token-1\n'
                    'dns: {nameserver: [192.0.2.53]}\n'
                    '#SUBSCRIBED https://example.invalid/consumed-token-2\n'
                    'proxies:\n  - {name: HK-1, type: http, server: example.invalid, port: 443}\n'
                    ' #subscribed https://example.invalid/consumed-token-3\n')
        profile, cache, count = prepare(original, 'Airport-test.yaml')
        self.assertEqual(count, 1)
        self.assertNotIn('consumed-token', profile + cache)
        self.assertNotIn('#subscribed', (profile + cache).lower())
        self.assertEqual(set(parse_yaml(profile)['proxy-providers']['Airport']), {'path'})

    def test_empty_cache_fails_without_remote_fallback(self):
        for original in ['proxies: []\n', '#SUBSCRIBED https://example.invalid/single-use\nproxies: []\n']:
            with self.assertRaisesRegex(ValueError, 'no usable node'):
                prepare(original, 'Airport-test.yaml')

    def test_rejects_cache_path_escape(self):
        with self.assertRaises(ValueError):
            prepare('', '../other.yaml')


if __name__ == '__main__':
    unittest.main()
