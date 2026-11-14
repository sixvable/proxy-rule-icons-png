#!/usr/bin/env python3
"""Build a Stash override from public routing data; never read subscriptions."""
import argparse
import copy
import hashlib
import json
import re
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent
BUILTINS = {"DIRECT", "REJECT", "REJECT-DROP"}
REPLACE_ROOT = {"hosts", "proxy-hosts", "proxy-groups", "rule-providers", "rules"}
REPLACE_DNS = {
    "default-nameserver", "nameserver", "nameserver-policy", "fallback",
    "fallback-filter", "fake-ip-filter",
}
ALI = ["https://223.5.5.5/dns-query", "https://223.6.6.6/dns-query"]


def load_source():
    return json.loads((ROOT / "inputs/routing.json").read_text())


def split_rule(rule):
    fields = rule.split(",")
    options = []
    while fields[-1] in {"no-resolve", "no-track"}:
        options.insert(0, fields.pop())
    return ",".join(fields[:-1]), fields[-1], options


def normalize_regex(value):
    return "(?i)" + value.replace("(?i)", "")


def make_groups(source):
    originals = source["groups"]
    names = {g["name"] for g in originals}
    regions = [g for g in originals if g.get("include-all") and g["type"] == "select"
               and any(n.endswith("-Auto") for n in g.get("proxies", []))]
    workers = {g["name"]: [n for n in g.get("proxies", [])
                           if n in names and n.endswith(("-Auto", "-FallBack"))]
               for g in regions}
    dynamic_names = set(workers) | {n for values in workers.values() for n in values}
    all_filter = normalize_regex(next(g for g in regions if g["name"] == "AllServer")["filter"])
    result = []
    for original in originals:
        group = {k: copy.deepcopy(v) for k, v in original.items()
                 if k in {"name", "type", "icon", "interval", "lazy", "tolerance"}}
        if original["name"] in dynamic_names:
            group["include-all"] = True
            raw = normalize_regex(original["filter"])
            if original["name"] in {"AllServer", "All-Auto", "All-FallBack"}:
                # AllServer remains a manual escape hatch for any naming convention.
                if original["name"] != "AllServer":
                    group["filter"] = raw
            else:
                group["filter"] = "(?i)^(?=(?:" + all_filter[4:] + "))(?=[\\s\\S]*(?:" + raw[4:] + "))[\\s\\S]+$"
            group["lazy"] = True
            group["interval"] = 300
            if group["type"] in {"url-test", "fallback"}:
                group["hidden"] = False
            # Never mix explicit proxies with include-all in Stash.
        else:
            choices = []
            for choice in original.get("proxies", []):
                if choice not in names | BUILTINS:
                    continue
                choices.append(choice)
                choices.extend(workers.get(choice, []))
            if original["name"] == "DNS-Global":
                # Preserve the source default, then offer every available region.
                for region in regions:
                    choices.append(region["name"])
                    choices.extend(workers[region["name"]])
            group["proxies"] = list(dict.fromkeys(choices))
            group["interval"] = -1
        result.append(group)
    return result


def build_config(source):
    providers = copy.deepcopy(source["rule-providers"])
    for name, provider in providers.items():
        provider["url"] = provider["url"].replace("/stash-release/", "/" + source["public_rules_commit"] + "/")
        provider["path"] = "./ruleset/stash-native-slim-20261114/" + name + ".mrs"
    return {
        "name": "通用分流｜原生订阅",
        "desc": "继承原订阅节点和 proxy-server-nameserver；其余 DNS、策略组与分流采用本覆写。地区组手动选节点，Auto/Fallback 独立选择。无需节点池或订阅转换。",
        "category": "自用分流",
        "version": source["version"],
        "mode": "rule",
        "log-level": "info",
        "ipv6": True,
        "hosts": {"+.clash.dev": "127.0.0.1", "+.stash.dev": "127.0.0.1"},
        "proxy-hosts": {},
        "dns": {
            # Deliberately no proxy-server-nameserver: dictionary merge inherits it.
            "ipv6": True,
            "skip-cert-verify": False,
            "follow-rule": True,
            "default-nameserver": ALI.copy(),
            "nameserver": ["https://8.8.8.8/dns-query", "https://1.1.1.1/dns-query"],
            "nameserver-policy": {
                "geosite:private": ["system"],
                "rule-set:GeositeCN_Domain": ALI.copy(),
            },
            "fallback": [],
            "fallback-filter": {},
            "fake-ip-range": "198.18.0.1/16",
            "fake-ip-filter": ["*"],
        },
        "proxy-groups": make_groups(source),
        "rule-providers": providers,
        "rules": source["rules"].copy(),
    }


HEADER = """# Stash 通用覆写 — {version}
# 导入到 Stash 的「覆写」，配合原生机场配置使用；不作为完整配置导入。
# 唯一继承的机场路由输入：proxies / proxy-providers / dns.proxy-server-nameserver。
# 不写入、不请求机场订阅地址；一次性链接不能刷新，更新需另行导入新链接。
# DNS 字典必须保留递归合并；不要在 dns: 后加 #!replace，否则会删除机场节点 DNS。
# 各 DNS 数组与 policy 独立替换，避免旧机场 nameserver/policy/fallback 混入。
# 地区手动组只收录原生节点；Auto/Fallback 是独立策略组，可从业务组或 Proxy 选择。
# DNS-Global 也可直接选择地区组。DNS-China 默认 DIRECT。
# Stash 使用 follow-rule 转发 DNS；不支持照搬 Mihomo 的 #DNS-Global / direct-nameserver。
# 因此网站选 DIRECT 不会自动切换阿里 DNS；阿里由国内域名 policy 选择。
# 本版只精简分流规则；DNS、Fake-IP 例外、测速和策略组菜单恢复为 .8 的设置。
# 公共规则固定到已经校验的版本；本文件没有自动更新入口，不会跳回旧覆写。
# 完整文件已做离线检查；此版本尚未在手机上正式启用或完成运行时验收。
"""


def render(cfg):
    text = yaml.safe_dump(cfg, allow_unicode=True, sort_keys=False, width=120)
    def replace_line(match):
        indent, key, value = match.group(1), match.group(2), match.group(3)
        if value.strip() in {"[]", "{}"}:
            return indent + key + ": #!replace\n" + indent + "  " + value.strip()
        return indent + key + ":" + value + " #!replace"
    for key in REPLACE_ROOT:
        text = re.sub(r"^()(" + re.escape(key) + r"):(.*)$", replace_line, text, flags=re.M)
    for key in REPLACE_DNS:
        text = re.sub(r"^(  )(" + re.escape(key) + r"):(.*)$", replace_line, text, flags=re.M)
    assert yaml.safe_load(text) == cfg
    return HEADER.format(version=cfg["version"]) + text


def simulate_merge(base, override):
    """Mirror only the merge directives deliberately emitted by this builder."""
    def merge(old, new, path):
        if (len(path) == 1 and path[0] in REPLACE_ROOT) or (len(path) == 2 and path[0] == "dns" and path[1] in REPLACE_DNS):
            return copy.deepcopy(new)
        if isinstance(old, dict) and isinstance(new, dict):
            out = copy.deepcopy(old)
            for k, v in new.items():
                out[k] = merge(out.get(k), v, path + (k,))
            return out
        if isinstance(old, list) and isinstance(new, list):
            return copy.deepcopy(new + old)
        return copy.deepcopy(new)
    metadata = {"name", "desc", "category", "version"}
    return merge(base, {k: v for k, v in override.items() if k not in metadata}, ())


def validate(cfg):
    assert not {"proxies", "proxy-providers", "listeners", "mixed-port", "http", "script"} & cfg.keys()
    assert "proxy-server-nameserver" not in cfg["dns"]
    groups = cfg["proxy-groups"]
    names = {g["name"] for g in groups}
    assert len(names) == len(groups)
    assert [g["name"] for g in groups[:2]] == ["Proxy", "Final"]
    edges = {}
    for g in groups:
        assert not (g.get("include-all") and "proxies" in g), g["name"]
        assert not g.get("use"), g["name"]
        refs = set(g.get("proxies", []))
        assert refs <= names | BUILTINS, (g["name"], refs - names - BUILTINS)
        edges[g["name"]] = refs & names
        if "filter" in g:
            re.compile(g["filter"])
    visited = set()
    def visit(name, stack):
        assert name not in stack, "Cyclic strategy group: " + name
        if name in visited:
            return
        for child in edges[name]:
            visit(child, stack | {name})
        visited.add(name)
    for name in names:
        visit(name, set())
    for rule in cfg["rules"]:
        pred, target, _ = split_rule(rule)
        assert target in names | BUILTINS, target
        if pred.startswith("RULE-SET,"):
            assert pred.split(",")[1] in cfg["rule-providers"]
        assert "GEOSITE," not in pred.upper(), "Use the compiled MRS rules"
    for ref in list(cfg["dns"]["nameserver-policy"]) + cfg["dns"]["fake-ip-filter"]:
        if ref.startswith("rule-set:"):
            for name in ref.removeprefix("rule-set:").split(","):
                assert cfg["rule-providers"][name]["behavior"] == "domain", name
    assert all(p["format"] == "mrs" and p["behavior"] in {"domain", "ipcidr"}
               for p in cfg["rule-providers"].values())
    assert cfg["rules"][-1] == "MATCH,Final"
    assert not any(g["name"].startswith("U-") for g in groups)
    return {"groups": len(groups), "rules": len(cfg["rules"]), "rule_providers": len(cfg["rule-providers"])}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", type=Path, default=ROOT / "dist")
    args = parser.parse_args()
    source = load_source()
    cfg = build_config(source)
    report = validate(cfg)
    text = render(cfg)
    args.out.mkdir(parents=True, exist_ok=True)
    file = args.out / "Stash-Universal.stoverride"
    file.write_text(text)
    report.update(version=source["version"], sha256=hashlib.sha256(file.read_bytes()).hexdigest(),
                  node_source="native subscription unchanged", proxy_server_nameserver="inherited unchanged when present; not invented when absent",
                  public_rules_commit=source["public_rules_commit"], source_clash_sha256=source["clash_source_sha256"],
                  ios_full_runtime_tested=False, subscription_requests=0, active_device_configuration_modified=False)
    report["rule_optimization"] = source.get("rule_optimization", {})
    (args.out / "validation.json").write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n")
    print(json.dumps(report, ensure_ascii=False))


if __name__ == "__main__":
    main()
