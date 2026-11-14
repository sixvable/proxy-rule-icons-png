"""Read existing local profiles and public rule caches; never request their URLs."""
import argparse
import hashlib
import json
import re
import shutil
import subprocess
from pathlib import Path

import yaml

from build_native import ROOT, BUILTINS, simulate_merge, validate


def audit_profiles(cfg, paths):
    results = []
    new_names = {g['name'] for g in cfg['proxy-groups']}
    for index, path in enumerate(paths, 1):
        before = path.read_bytes()
        base = yaml.safe_load(before)
        merged = simulate_merge(base, cfg)
        for field in ('proxies', 'proxy-providers'):
            assert merged.get(field) == base.get(field)
        old_dns = base.get('dns') or {}
        marker = object()
        assert merged['dns'].get('proxy-server-nameserver', marker) == old_dns.get('proxy-server-nameserver', marker)
        for key, value in cfg['dns'].items():
            assert merged['dns'][key] == value, key
        nodes = {n['name'] for n in merged.get('proxies', [])}
        assert not nodes & new_names, 'Native node names conflict with override groups'
        # Do not export node names or private endpoints in validation reports.
        for node in merged.get('proxies', []):
            if 'dialer-proxy' in node:
                assert node['dialer-proxy'] in nodes | new_names | BUILTINS, 'Native dialer-proxy needs a removed original group'
        for provider in merged.get('proxy-providers', {}).values():
            if 'proxy' in provider:
                assert provider['proxy'] in nodes | new_names | BUILTINS, 'Provider download proxy needs a removed original group'
        assert merged['proxy-groups'] == cfg['proxy-groups']
        assert merged['rule-providers'] == cfg['rule-providers']
        assert merged['rules'] == cfg['rules']
        assert path.read_bytes() == before
        results.append({'sample': index, 'inline_nodes': len(nodes),
                        'proxy_providers': len(base.get('proxy-providers', {})),
                        'node_dns_present': 'proxy-server-nameserver' in old_dns,
                        'node_dns_preserved': True, 'original_file_unchanged': True,
                        'merge_and_dependency_check': 'passed'})
    return results


def audit_public_rules(cfg, cache, work, mihomo):
    manifest = json.loads((ROOT / 'inputs/public-rule-manifest.json').read_text())
    work.mkdir(parents=True, exist_ok=True)
    providers = {}
    for item in manifest['providers']:
        name = item['name']
        source = cache / (name + '.mrs')
        data = source.read_bytes()
        assert hashlib.sha256(data).hexdigest() == item['sha256'], name
        dest = work / 'rules' / source.name
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_bytes(data)
        providers[name] = {'type': 'file', 'behavior': cfg['rule-providers'][name]['behavior'],
                           'format': 'mrs', 'path': './rules/' + source.name}
    assert set(providers) == set(cfg['rule-providers'])
    probe = {'mode': 'rule', 'log-level': 'info', 'dns': {'enable': False},
             'rule-providers': providers,
             'rules': ['RULE-SET,' + name + ',DIRECT' for name in providers] + ['MATCH,DIRECT']}
    config = work / 'public-mrs-validation.yaml'
    config.write_text(yaml.safe_dump(probe, sort_keys=False))
    process = subprocess.run([str(mihomo), '-t', '-d', str(work.resolve()), '-f', str(config.resolve())],
                             capture_output=True, text=True, timeout=60)
    log = process.stdout + process.stderr
    (work / 'public-mrs-validation.log').write_text(log)
    assert process.returncode == 0, log[-1000:]
    assert not re.search(r'level=(error|fatal|warning)', log, re.I), log[-1000:]
    return {'verified_public_mrs_files': len(providers), 'published_hashes_match': True,
            'isolated_mrs_parse': 'passed', 'validation_engine': 'mihomo file-only ruleset parser',
            'is_stash_runtime_test': False}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--override', type=Path, required=True)
    parser.add_argument('--profiles', type=Path, nargs='+', required=True)
    parser.add_argument('--public-cache', type=Path, required=True)
    parser.add_argument('--work', type=Path, required=True)
    parser.add_argument('--mihomo', type=Path, required=True)
    args = parser.parse_args()
    cfg = yaml.safe_load(args.override.read_text())
    validate(cfg)
    results = {'profiles': audit_profiles(cfg, args.profiles),
               'public_rules': audit_public_rules(cfg, args.public_cache, args.work, args.mihomo),
               'subscription_requests': 0, 'device_configuration_changed': False,
               'full_stash_runtime_tested': False}
    report = args.override.with_name('validation.json')
    current = json.loads(report.read_text())
    current['local_audit'] = results
    report.write_text(json.dumps(current, ensure_ascii=False, indent=2) + '\n')
    print(json.dumps(results, ensure_ascii=False))


if __name__ == '__main__':
    main()
