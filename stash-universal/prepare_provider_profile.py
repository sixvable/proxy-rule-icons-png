#!/usr/bin/env python3
"""Prepare a private, cache-only Stash provider. Never request subscription URLs."""
import argparse
import hashlib
import json
import re
import subprocess
from pathlib import Path


def parse_yaml(text):
    try:
        import yaml
    except ImportError:
        result = subprocess.run(
            ['ruby', '-ryaml', '-rjson', '-e', 'puts JSON.generate(YAML.load(STDIN.read))'],
            input=text, text=True, capture_output=True,
        )
        if result.returncode:
            raise ValueError('YAML validation failed; private input was not logged')
        return json.loads(result.stdout)
    return yaml.safe_load(text)


def prepare(text, cache_name):
    if not re.fullmatch(r'[A-Za-z0-9_-]+\.yaml', cache_name):
        raise ValueError('Cache name must be a simple .yaml filename')
    # A subscription URL may be single-use. Remove all managed-subscription
    # directives before splitting blocks; never copy, resolve or request them.
    text = re.sub(r'(?im)^[ \t]*#SUBSCRIBED\b[^\r\n]*(?:\r?\n|$)', '', text)
    matches = list(re.finditer(r'^([A-Za-z][A-Za-z0-9_-]*):[^\n]*(?:\n|$)', text, re.M))
    keys = [m.group(1) for m in matches]
    if len(keys) != len(set(keys)):
        raise ValueError('Duplicate top-level keys require manual review')
    blocks = {
        m.group(1): text[m.start():matches[i+1].start() if i+1 < len(matches) else len(text)]
        for i, m in enumerate(matches)
    }
    if 'proxies' not in blocks:
        raise ValueError('This adapter expects inline proxies in the original subscription')
    cache = blocks['proxies']
    nodes = parse_yaml(cache).get('proxies')
    if not isinstance(nodes, list) or not nodes:
        raise ValueError('Original subscription has no usable node definitions')
    # Preserve DNS, hosts, IPv6 and all unrelated settings verbatim. Routing and
    # node sources are supplied by the shared override and a local static file.
    replaced = {'proxies', 'proxy-providers', 'proxy-groups', 'rule-providers', 'rules'}
    kept = ''.join(value for key, value in blocks.items() if key not in replaced)
    profile = (
        '# Local static provider; enable the shared provider-mode override.\n'
        '# No subscription URL, automatic refresh or remote fallback. Preserve the local node file.\n'
        + kept.rstrip() + '\n\n'
        + 'proxy-providers:\n  Airport:\n    path: ./proxy-providers/' + cache_name + '\n'
        + '\nproxy-groups:\n  - name: Airport-Default\n    type: select\n    use: [Airport]\n'
        + '\nrules:\n  - MATCH,Airport-Default\n'
    )
    parsed = parse_yaml(profile)
    for key, value in blocks.items():
        if key not in replaced:
            if parsed.get(key) != parse_yaml(value).get(key):
                raise ValueError('An unrelated airport setting changed')
    return profile, cache, len(nodes)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('source', type=Path)
    parser.add_argument('--out', type=Path, required=True)
    parser.add_argument('--cache-name')
    args = parser.parse_args()
    cache_name = args.cache_name or ('Airport-' + hashlib.sha256(args.source.name.encode()).hexdigest()[:12] + '.yaml')
    profile, cache, count = prepare(args.source.read_text(), cache_name)
    profiles = args.out / 'profiles'
    caches = args.out / 'resources' / 'proxy-providers'
    profiles.mkdir(parents=True, exist_ok=True)
    caches.mkdir(parents=True, exist_ok=True)
    profile_path = profiles / (args.source.stem + '_本地节点池.yaml')
    profile_path.write_text(profile)
    cache_path = caches / cache_name
    cache_path.write_text(cache)
    profile_path.chmod(0o600)
    cache_path.chmod(0o600)
    print(json.dumps({'profile': profile_path.name, 'cached_nodes': count,
                      'base_settings_preserved': True, 'private_outputs': True,
                      'remote_subscription_requests': 0, 'automatic_node_updates': False}, ensure_ascii=False))


if __name__ == '__main__':
    main()
