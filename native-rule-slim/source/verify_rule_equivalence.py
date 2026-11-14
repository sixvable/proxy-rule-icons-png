"""Offline differential checks; this is not a Stash runtime or memory test."""
import argparse
import ipaddress
import json
import re
from pathlib import Path

from build_native import split_rule


class DomainIndex:
    def __init__(self, values):
        self.exact, self.suffix, self.wildcards = set(), set(), []
        for value in values:
            value = value.lower()
            suffix = value.startswith('+.')
            raw = value[2:] if suffix else value
            if '*' in raw or '?' in raw:
                pattern = re.escape(raw).replace(r'\*', '[^.]+').replace(r'\?', '[^.]')
                self.wildcards.append(re.compile(('(?:[^.]+\\.)*' if suffix else '') + pattern + '$'))
            else:
                (self.suffix if suffix else self.exact).add(raw)

    def matches(self, host):
        labels = host.split('.')
        return host in self.exact or any('.'.join(labels[i:]) in self.suffix for i in range(len(labels))) or any(p.fullmatch(host) for p in self.wildcards)


class Model:
    def __init__(self, config, payloads):
        self.rules = []
        providers = config['rule-providers']
        domain = {n: DomainIndex(v) for n, v in payloads.items() if providers[n]['behavior'] == 'domain'}
        ips = {n: [ipaddress.ip_network(x, strict=False) for x in v] for n, v in payloads.items() if providers[n]['behavior'] == 'ipcidr'}
        for rule in config['rules']:
            pred, target, opts = split_rule(rule)
            typ, _, val = pred.partition(',')
            if typ == 'RULE-SET':
                arg = domain.get(val) if val in domain else ips[val]
                typ = 'domain-set' if val in domain else 'ip-set'
            elif typ == 'DOMAIN-REGEX':
                arg = re.compile(val)
            elif typ in {'IP-CIDR', 'IP-CIDR6'}:
                arg = [ipaddress.ip_network(val, strict=False)]
                typ = 'ip-set'
            else:
                arg = val.lower()
            self.rules.append((typ, arg, (target, 'no-track' in opts)))

    def match(self, host='', address=None):
        for typ, arg, result in self.rules:
            if (typ == 'MATCH'
                or typ == 'domain-set' and host and arg.matches(host)
                or typ == 'DOMAIN' and host == arg
                or typ == 'DOMAIN-SUFFIX' and (host == arg or host.endswith('.' + arg))
                or typ == 'DOMAIN-KEYWORD' and arg in host
                or typ == 'DOMAIN-REGEX' and host and arg.search(host)
                or typ == 'ip-set' and address is not None and any(address.version == n.version and address in n for n in arg)):
                return result
        return None


def verify(before, after, old_payloads, new_payloads):
    hosts = {'linear.tv.apple.com', 'hls-svod.itunes.apple.com', 'events.data.microsoft.com', 'ecs.office.com', 'onedrive.live.com', 'tv.g.apple.com', 'youtube.com', 'unlisted-example.invalid'}
    addresses = set()
    for name, values in old_payloads.items():
        if before['rule-providers'][name]['behavior'] == 'domain':
            for entry in values:
                raw = entry.removeprefix('+.').replace('*', 'probe').replace('?', 'a').lower()
                hosts.update((raw, 'probe.' + raw, 'deep.probe.' + raw, 'not-' + raw))
        else:
            for entry in values:
                net = ipaddress.ip_network(entry, strict=False)
                for x in [int(net.network_address) - 1, int(net.network_address), int(net.broadcast_address), int(net.broadcast_address) + 1]:
                    if 0 <= x < 2 ** net.max_prefixlen:
                        addresses.add((net.version, x))
    for rule in before['rules']:
        pred, _, _ = split_rule(rule)
        if pred.startswith('DOMAIN-KEYWORD,'):
            hosts.add('probe-' + pred.split(',', 1)[1] + '-sample.invalid')
    left, right = Model(before, old_payloads), Model(after, new_payloads)
    for host in sorted(hosts):
        assert left.match(host) == right.match(host), ('hostname mismatch', host, left.match(host), right.match(host))
    for family, value in sorted(addresses):
        address = (ipaddress.IPv4Address if family == 4 else ipaddress.IPv6Address)(value)
        assert left.match(address=address) == right.match(address=address), ('IP mismatch', str(address))
    # Unsupported conditions are unchanged and are not presented as simulated.
    opaque = lambda cfg: [r for r in cfg['rules'] if r.split(',')[0] in {'GEOIP', 'IP-ASN', 'AND', 'OR', 'NOT', 'NETWORK', 'DST-PORT'}]
    assert opaque(before) == opaque(after)
    for name in ['GeositeCN_Domain']:
        assert old_payloads[name] == new_payloads[name]
    return {'hostname_cases': len(hosts), 'cidr_boundary_cases': len(addresses),
            'differential_results_equal': True, 'unchanged_opaque_rule_sequence': True,
            'dns_policy_payload_unchanged': True, 'is_stash_runtime_test': False}


def main():
    p = argparse.ArgumentParser()
    for name in ['before', 'after', 'old-payloads', 'new-payloads', 'report']:
        p.add_argument('--' + name, type=Path, required=True)
    args = p.parse_args()
    result = verify(json.loads(args.before.read_text()), json.loads(args.after.read_text()),
                    json.loads(args.old_payloads.read_text()), json.loads(args.new_payloads.read_text()))
    args.report.write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps(result))


if __name__ == '__main__':
    main()
