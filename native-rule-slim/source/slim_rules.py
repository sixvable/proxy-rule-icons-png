"""Order-preserving rule reduction. Only accepts already cached public rule data."""
import argparse
import copy
import hashlib
import ipaddress
import json
import re
import subprocess
from pathlib import Path

from build_native import split_rule


def literal_domain(entry):
    name = entry[2:] if entry.startswith('+.') else entry
    return None if any(c in name for c in '*?') else name.lower()


class DomainCoverage:
    def __init__(self):
        self.patterns = set()
        self.exact = set()
        self.suffix = set()
        self.keywords = set()

    def add(self, entry):
        self.patterns.add(entry.lower())
        value = literal_domain(entry)
        if value is not None:
            (self.suffix if entry.startswith('+.') else self.exact).add(value)

    def reason(self, entry):
        if entry.lower() in self.patterns:
            return 'identical earlier domain pattern'
        value = literal_domain(entry)
        if value is None:
            return None  # Do not infer containment between arbitrary wildcards.
        labels = value.split('.')
        if any('.'.join(labels[i:]) in self.suffix for i in range(len(labels))):
            return 'earlier domain suffix'
        if not entry.startswith('+.') and value in self.exact:
            return 'earlier exact domain'
        if any(word in value for word in self.keywords):
            return 'earlier domain keyword'
        return None


def tracking_options(opts):
    # no-resolve only affects IP rules, never a domain/keyword matcher.
    return tuple(x for x in opts if x != 'no-resolve')


def optimize(rules, providers, payloads, protected=('GeositeCN_Domain',)):
    """Remove only entries proved unreachable or redundant within one action block.

    Earlier domain coverage wins regardless of its action. Later keywords are
    used only inside a contiguous block with the same action/tracking options.
    CIDRs are removed only when wholly covered by earlier CIDRs with identical
    resolution/tracking options. DNS policy sets are never modified.
    """
    parsed = [split_rule(r) for r in rules]
    def pure_domain(predicate):
        kind, _, value = predicate.partition(',')
        return kind in {'DOMAIN', 'DOMAIN-SUFFIX', 'DOMAIN-KEYWORD', 'DOMAIN-REGEX'} or (kind == 'RULE-SET' and providers[value]['behavior'] == 'domain')
    block_keywords = [set() for _ in rules]
    begin = 0
    while begin < len(rules):
        end = begin + 1
        _, target, opts = parsed[begin]
        while (end < len(rules) and pure_domain(parsed[begin][0]) and pure_domain(parsed[end][0])
               and parsed[end][1] == target and tracking_options(parsed[end][2]) == tracking_options(opts)):
            end += 1
        words = {p.split(',', 1)[1].lower() for p, _, _ in parsed[begin:end] if p.startswith('DOMAIN-KEYWORD,')}
        for i in range(begin, end):
            block_keywords[i] = words
        begin = end

    used = {}
    for pred, _, _ in parsed:
        if pred.startswith('RULE-SET,'):
            name = pred.split(',')[1]
            used[name] = used.get(name, 0) + 1
    protected = set(protected) | {n for n, count in used.items() if count != 1}
    coverage = DomainCoverage()
    previous_cidrs = {}
    previous_domain_predicates = set()
    result_rules = []
    result_payloads = copy.deepcopy(payloads)
    drops = []
    singleton = []

    for index, (pred, target, opts) in enumerate(parsed):
        kind, _, value = pred.partition(',')
        if kind == 'RULE-SET':
            name = value
            behavior = providers[name]['behavior']
            original = payloads[name]
            kept = []
            for entry in original:
                reason = None
                if behavior == 'domain':
                    reason = coverage.reason(entry)
                    literal = literal_domain(entry)
                    if not reason and literal is not None and any(word in literal for word in block_keywords[index]):
                        reason = 'keyword in the same contiguous action block'
                elif behavior == 'ipcidr':
                    net = ipaddress.ip_network(entry, strict=False)
                    if any(net.version == old.version and net.subnet_of(old)
                           for old in previous_cidrs.get(tuple(opts), [])):
                        reason = 'earlier CIDR with identical options'
                else:
                    raise ValueError('Only indexed domain/ipcidr providers are accepted')
                if reason and name not in protected:
                    drops.append({'provider': name, 'entry': entry, 'reason': reason})
                else:
                    kept.append(entry)
            result_payloads[name] = kept
            # Original patterns also covered by earlier rules or a keyword in
            # this same action block remain valid witnesses for later entries.
            if behavior == 'domain':
                for entry in original:
                    coverage.add(entry)
            else:
                previous_cidrs.setdefault(tuple(opts), []).extend(ipaddress.ip_network(x, strict=False) for x in original)
            if not kept:
                drops.append({'rule': rules[index], 'reason': 'provider has no remaining reachable entries'})
                continue
            if len(kept) == 1 and name not in protected:
                entry = kept[0]
                if behavior == 'ipcidr':
                    kind = 'IP-CIDR6' if ':' in entry else 'IP-CIDR'
                    direct = kind + ',' + entry
                elif literal_domain(entry) is not None:
                    direct = ('DOMAIN-SUFFIX,' + entry[2:] if entry.startswith('+.') else 'DOMAIN,' + entry)
                else:
                    direct = None
                if direct:
                    result_rules.append(direct + ',' + target + (',' + ','.join(opts) if opts else ''))
                    singleton.append(name)
                    continue
        elif kind in {'DOMAIN-KEYWORD', 'DOMAIN-REGEX', 'DOMAIN', 'DOMAIN-SUFFIX'}:
            signature = pred.lower() if kind != 'DOMAIN-REGEX' else pred
            if signature in previous_domain_predicates:
                drops.append({'rule': rules[index], 'reason': 'identical earlier domain predicate'})
                continue
            previous_domain_predicates.add(signature)
            if kind == 'DOMAIN-KEYWORD':
                coverage.keywords.add(value.lower())
            elif kind in {'DOMAIN', 'DOMAIN-SUFFIX'}:
                coverage.add(('+.' if kind == 'DOMAIN-SUFFIX' else '') + value)
        result_rules.append(rules[index])

    used_after = {split_rule(r)[0].split(',')[1] for r in result_rules if r.startswith('RULE-SET,')} | set(protected)
    result_providers = {n: copy.deepcopy(v) for n, v in providers.items() if n in used_after}
    result_payloads = {n: v for n, v in result_payloads.items() if n in used_after}
    assert all(result_payloads.values())
    for name in protected:
        assert result_payloads[name] == payloads[name]
    report = {
        'routing_rows_before': len(rules), 'routing_rows_after': len(result_rules),
        'providers_before': len(providers), 'providers_after': len(result_providers),
        'entries_before': sum(map(len, payloads.values())),
        'entries_after': sum(map(len, result_payloads.values())),
        'single_entry_providers_inlined': singleton,
        'protected_dns_sets': sorted(protected),
        'removed_entries': sum('entry' in x for x in drops),
        'removals': drops,
    }
    return result_rules, result_providers, result_payloads, report


def compile_mrs(providers, payloads, out, mihomo):
    folder = out / 'rules'
    folder.mkdir(parents=True, exist_ok=True)
    manifest = []
    for name, provider in providers.items():
        text = folder / (name + '.txt')
        text.write_text('\n'.join(payloads[name]) + '\n')
        mrs = text.with_suffix('.mrs')
        result = subprocess.run([str(mihomo), 'convert-ruleset', provider['behavior'], 'text', str(text), str(mrs)], capture_output=True, text=True, timeout=20)
        assert result.returncode == 0 and not re.search(r'level=(warning|error|fatal)', result.stdout + result.stderr, re.I), name
        manifest.append({'name': name, 'behavior': provider['behavior'], 'entries': len(payloads[name]),
                         'text_bytes': text.stat().st_size, 'mrs_bytes': mrs.stat().st_size,
                         'sha256': hashlib.sha256(mrs.read_bytes()).hexdigest()})
    return manifest


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--source', type=Path, required=True)
    p.add_argument('--payloads', type=Path, required=True)
    p.add_argument('--out', type=Path, required=True)
    p.add_argument('--mihomo', type=Path, required=True)
    args = p.parse_args()
    source = json.loads(args.source.read_text())
    payloads = json.loads(args.payloads.read_text())
    rules, providers, payloads, report = optimize(source['rules'], source['rule-providers'], payloads)
    args.out.mkdir(parents=True, exist_ok=True)
    manifest = compile_mrs(providers, payloads, args.out, args.mihomo)
    report['mrs_bytes_after'] = sum(x['mrs_bytes'] for x in manifest)
    (args.out / 'optimization.json').write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n')
    (args.out / 'payloads.json').write_text(json.dumps(payloads, ensure_ascii=False, indent=2) + '\n')
    (args.out / 'manifest.json').write_text(json.dumps({'providers': manifest}, ensure_ascii=False, indent=2) + '\n')
    source.update(rules=rules, **{'rule-providers': providers})
    (args.out / 'routing.json').write_text(json.dumps(source, ensure_ascii=False, indent=2) + '\n')
    print(json.dumps({k: v for k, v in report.items() if k != 'removals'}, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
