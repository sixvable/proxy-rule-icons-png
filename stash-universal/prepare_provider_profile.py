#!/usr/bin/env python3
"""Prepare a private Stash provider profile locally. Never upload its outputs."""
import argparse
import hashlib
import json
import re
import subprocess
from pathlib import Path
from urllib.parse import urlsplit


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
    urls = re.findall(r'^#SUBSCRIBED\s+(https?://\S+)', text, re.M)
    if not urls or len(set(urls)) != 1:
        raise ValueError('Expected one unambiguous original subscription URL')
    if urlsplit(urls[0]).scheme not in {'http', 'https'}:
        raise ValueError('Unsupported subscription scheme')
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
    # node sources are supplied by the shared override and the original URL.
    replaced = {'proxies', 'proxy-providers', 'proxy-groups', 'rule-providers', 'rules'}
    kept = ''.join(value for key, value in blocks.items() if key not in replaced)
    profile = (
        '# Local provider adapter; enable the shared provider-mode override.\n'
        '# Nodes update from the original URL. Regenerate this file to refresh airport DNS/settings.\n'
        + kept.rstrip() + '\n\n'
        + 'proxy-providers:\n  Airport:\n    url: ' + json.dumps(urls[0], ensure_ascii=False)
        + '\n    path: ./proxy-providers/' + cache_name
        + '\n    interval: 3600\n'
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
    profile_path = profiles / (args.source.stem + '_节点池.yaml')
    profile_path.write_text(profile)
    (caches / cache_name).write_text(cache)
    print(json.dumps({'profile': profile_path.name, 'cached_nodes': count,
                      'base_settings_preserved': True, 'private_outputs': True}, ensure_ascii=False))


if __name__ == '__main__':
    main()
