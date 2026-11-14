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
        self.assertEqual(result['proxy-providers']['Airport']['url'],
                         'https://example.invalid/subscription?token=PRIVATE_EXAMPLE')
        self.assertEqual(result['proxy-providers']['Airport']['path'], './proxy-providers/Airport-test.yaml')
        self.assertNotIn('#SUBSCRIBED', profile)
        self.assertNotIn('proxies', result)
        self.assertEqual(result['proxy-groups'][0]['use'], ['Airport'])

    def test_does_not_invent_missing_subscription(self):
        with self.assertRaises(ValueError):
            prepare('proxies: []\n', 'Airport-test.yaml')

    def test_rejects_cache_path_escape(self):
        with self.assertRaises(ValueError):
            prepare('', '../other.yaml')


if __name__ == '__main__':
    unittest.main()
