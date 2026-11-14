import unittest

from slim_rules import optimize


def fixture(rows, payloads, behaviors=None, protected=()):
    providers = {name: {'behavior': (behaviors or {}).get(name, 'domain')}
                 for name in payloads}
    return optimize(rows, providers, payloads, protected)


class RuleReductionTests(unittest.TestCase):
    def test_earlier_exact_is_not_a_suffix(self):
        _, _, payloads, _ = fixture(
            ['RULE-SET,first,A', 'RULE-SET,later,B', 'MATCH,C'],
            {'first': ['example.com'], 'later': ['+.example.com', 'api.example.com']})
        self.assertEqual(payloads['later'], ['+.example.com', 'api.example.com'])

    def test_earlier_suffix_wins_across_policy_boundaries(self):
        rules, _, payloads, report = fixture(
            ['RULE-SET,first,A', 'RULE-SET,later,B', 'MATCH,C'],
            {'first': ['+.example.com'], 'later': ['example.com', '+.api.example.com', 'keep.invalid', 'keep2.invalid']})
        self.assertEqual(payloads['later'], ['keep.invalid', 'keep2.invalid'])
        self.assertEqual(report['removed_entries'], 2)
        self.assertEqual(rules[0], 'DOMAIN-SUFFIX,example.com,A')

    def test_later_keyword_only_covers_same_contiguous_action_block(self):
        rows = ['RULE-SET,a,A', 'DOMAIN-KEYWORD,service,A', 'MATCH,C']
        rules, _, _, report = fixture(rows, {'a': ['+.service.example', 'unrelated.invalid']})
        self.assertEqual(rules, ['DOMAIN,unrelated.invalid,A', 'DOMAIN-KEYWORD,service,A', 'MATCH,C'])
        self.assertEqual(report['removed_entries'], 1)
        for barrier in ['DOMAIN,priority.invalid,B', 'IP-CIDR,192.0.2.0/24,A']:
            _, _, _, blocked = fixture([rows[0], barrier] + rows[1:], {'a': ['+.service.example', 'unrelated.invalid']})
            self.assertEqual(blocked['removed_entries'], 0)

    def test_do_not_change_tracking_or_infer_wildcard_containment(self):
        rows = ['RULE-SET,a,A,no-track', 'DOMAIN-KEYWORD,service,A', 'RULE-SET,b,B', 'MATCH,C']
        _, _, payloads, report = fixture(rows, {'a': ['+.service.example', '*.example.org'], 'b': ['+.example.org', 'api.example.org']})
        self.assertEqual(report['removed_entries'], 0)
        self.assertEqual(len(payloads['a']), 2)
        self.assertEqual(len(payloads['b']), 2)

    def test_dns_policy_set_preserves_even_unreachable_routing_entries(self):
        data = {'earlier': ['+.example.com'], 'dns': ['+.example.com', 'keep.invalid']}
        _, _, payloads, report = fixture(['RULE-SET,earlier,A', 'RULE-SET,dns,B', 'MATCH,C'], data, protected=['dns'])
        self.assertEqual(payloads['dns'], data['dns'])
        self.assertEqual(report['protected_dns_sets'], ['dns'])

    def test_ip_ranges_keep_holes_families_and_resolution_options(self):
        rows = ['RULE-SET,a,A,no-resolve', 'RULE-SET,b,B,no-resolve', 'RULE-SET,c,C', 'MATCH,D']
        data = {'a': ['192.0.2.0/25'], 'b': ['192.0.2.0/26', '192.0.2.128/25', '2001:db8::/64'], 'c': ['192.0.2.0/26', '198.51.100.0/24']}
        _, _, payloads, report = fixture(rows, data, {n: 'ipcidr' for n in data})
        self.assertEqual(payloads['b'], ['192.0.2.128/25', '2001:db8::/64'])
        self.assertEqual(payloads['c'], data['c'])
        self.assertEqual(report['removed_entries'], 1)

    def test_duplicate_regex_drops_only_the_later_identical_predicate(self):
        rows = [r'DOMAIN-REGEX,^api\d+\.example$,A', r'DOMAIN-REGEX,^api\d+\.example$,B', r'DOMAIN-REGEX,^api\w+\.example$,B', 'MATCH,C']
        rules, _, _, _ = fixture(rows, {})
        self.assertEqual(rules, [rows[0], rows[2], rows[3]])

    def test_repeated_provider_is_not_pruned_based_on_one_use(self):
        rows = ['RULE-SET,a,A', 'RULE-SET,a,B', 'MATCH,C']
        _, providers, payloads, _ = fixture(rows, {'a': ['+.example.com']})
        self.assertIn('a', providers)
        self.assertEqual(payloads['a'], ['+.example.com'])


if __name__ == '__main__':
    unittest.main()
