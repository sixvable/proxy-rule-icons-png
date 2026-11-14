#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Adapt any supported local airport cache to the common Airport interface.

Offline only. Inline nodes or explicitly supplied local provider caches are
required. Never follow subscription directives, provider URLs, or paths from
an imported configuration. Output contains private credentials.
"""
import argparse
import copy
import hashlib
import json
import os
import re
from pathlib import Path

import yaml

ROUTING_KEYS = {'proxies', 'proxy-providers', 'proxy-groups', 'rule-providers', 'rules'}
BUILTINS = {'DIRECT', 'REJECT', 'REJECT-DROP'}


def load(text):
    try:
        value = yaml.safe_load(text)
    except yaml.YAMLError:
        raise ValueError('Invalid local YAML; private contents omitted') from None
    if not isinstance(value, dict):
        raise ValueError('A local YAML mapping is required')
    return value


def prepare(text, cache_name, local_node_texts=(), reserved_names=()):
    if not re.fullmatch(r'[A-Za-z0-9_-]+\.yaml', cache_name):
        raise ValueError('Use a simple local cache filename')
    source = load(text)
    raw_nodes = source.get('proxies') or []
    if not isinstance(raw_nodes, list):
        raise ValueError('Inline proxies must be a list')
    nodes = copy.deepcopy(raw_nodes)
    for node_text in local_node_texts:
        additional = load(node_text).get('proxies')
        if not isinstance(additional, list):
            raise ValueError('Each explicitly supplied local cache needs a proxies list')
        nodes.extend(copy.deepcopy(additional))
    if source.get('proxy-providers') and not local_node_texts:
        raise ValueError('Provide existing provider caches explicitly with --nodes-local; no download will be attempted')
    if not nodes:
        raise ValueError('No cached nodes available; no download will be attempted')
    seen = {}
    for node in nodes:
        if not isinstance(node, dict) or not isinstance(node.get('name'), str) or not node['name'].strip():
            raise ValueError('Every cached node needs a nonempty name')
        name = node['name']
        if name in seen and seen[name] != node:
            raise ValueError('Conflicting duplicate node names; private name omitted')
        seen[name] = node
    names = set(seen)
    if names & (set(reserved_names) | BUILTINS | {'Airport-Default'}):
        raise ValueError('A node name collides with a policy group; rename it locally before adapting')
    for node in seen.values():
        if node.get('dialer-proxy') and node['dialer-proxy'] not in names | BUILTINS:
            raise ValueError('A node depends on an original policy group; manual adaptation is required')
    base = {k: copy.deepcopy(v) for k, v in source.items() if k not in ROUTING_KEYS}
    entry = copy.deepcopy(base)
    entry.update({
        'proxy-providers': {'Airport': {'path': './proxy-providers/' + cache_name}},
        'proxy-groups': [{'name': 'Airport-Default', 'type': 'select', 'use': ['Airport']}],
        'rules': ['MATCH,Airport-Default'],
    })
    dump = lambda obj: yaml.safe_dump(obj, allow_unicode=True, sort_keys=False, width=120)
    profile = '# Local cache only; enable the common Airport override.\n' + dump(entry)
    cache = dump({'proxies': list(seen.values())})
    assert {k: v for k, v in load(profile).items() if k not in ROUTING_KEYS} == base
    assert load(cache)['proxies'] == list(seen.values())
    return profile, cache, len(seen)


def local_path(value):
    if re.match(r'^[a-z][a-z0-9+.-]*://', value, re.I):
        raise argparse.ArgumentTypeError('Only existing local files are accepted')
    path = Path(value)
    if not path.is_file():
        raise argparse.ArgumentTypeError('Local file does not exist; no download will be attempted')
    return path


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('source', type=local_path)
    parser.add_argument('--nodes-local', type=local_path, action='append', default=[])
    parser.add_argument('--override', type=local_path, required=True)
    parser.add_argument('--out', type=Path, required=True)
    args = parser.parse_args()
    override = load(args.override.read_text(encoding='utf-8-sig'))
    reserved = [g['name'] for g in override.get('proxy-groups', [])]
    identity = hashlib.sha256(str(args.source.resolve()).encode()).hexdigest()[:16]
    cache_name = 'Airport-' + identity + '.yaml'
    entry, cache, count = prepare(
        args.source.read_text(encoding='utf-8-sig'), cache_name,
        [p.read_text(encoding='utf-8-sig') for p in args.nodes_local], reserved,
    )
    os.umask(0o077)
    args.out.mkdir(parents=True, exist_ok=False, mode=0o700)
    files = {
        'profiles/' + args.source.stem + '_本地节点池.yaml': entry,
        'resources/proxy-providers/' + cache_name: cache,
    }
    for relative, contents in files.items():
        path = args.out / relative
        path.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
        with path.open('x', encoding='utf-8') as f:
            f.write(contents)
    print(json.dumps({'cached_nodes': count, 'offline_only': True,
                      'original_source_unchanged': True, 'private_outputs': True,
                      'automatic_node_updates': False}))


if __name__ == '__main__':
    main()
