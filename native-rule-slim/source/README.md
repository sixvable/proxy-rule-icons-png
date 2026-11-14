# Stash 原生订阅通用覆写

当前修订：`Stash-Universal.stoverride`，版本 `2026.11.14.10`。

只继承原机场的 `proxies`、`proxy-providers` 和 `dns.proxy-server-nameserver`；普通 DNS、hosts、策略组及分流规则由覆写提供。节点 DNS 原来缺省则保持缺省。直接叠加原生订阅，不建立 Airport 节点池，不转换订阅，不请求机场链接。

## 本次按规则精简

`.9` 版改动 DNS、Fake-IP 及测速参数的处理方向已撤回。本版恢复 `.8` 的这些设置，并完整保留 139 个策略组的菜单、顺序和选择方式。不能在没有实测的情况下，把某项参数认定为内存告警的唯一原因。

延续此前「域名/IP 拆分、同策略合并、去重、MRS 压缩」方式，进一步删除跨规则集的重复覆盖：

| 项目 | `.8` / `.9` | `.10` |
| --- | ---: | ---: |
| 分流入口 | 206 | 200 |
| MRS 规则集 | 104 | 93 |
| 集合条目 | 11,440 | 9,672 |
| MRS 文件总字节数 | 100,674 | 82,936 |

1,759 条集合条目已被更早的域名后缀、关键词或同条件 IP 网段覆盖，或与同一连续策略区间的关键词重复。9 个只有单条规则的集合改为直接规则，免去独立 provider。两个空集合及四条重复的域名匹配入口移除。

例如：后面的通用 AI 规则不再重复前面 OpenAI 的相同正则；Amazon 不再重复前面 Country-China 的相同正则及 PrimeVideo 的相同关键词。保留原有「先匹配者优先」结果，没有把后面的策略提前。

`GeositeCN_Domain` 同时供 DNS policy 使用，内容完全保留。仅凭路由中某条域名不再可达，不能删除它在 DNS policy 中的用途。IP 优化保留 `no-resolve` 条件，不跨不同解析条件合并；域名优化也不跨会触发解析的 IP 规则移动匹配。

规则仍使用 `domain` / `ipcidr` MRS；未新增大型 classical 集合。缓存使用 `./ruleset/stash-native-slim-20261114/`，避免继续读取同名旧规则缓存。公共 URL 固定到提交版本，覆写无 `#SUBSCRIBED` 更新入口。

## 导入和使用

1. 保留并选用已导入的原生机场配置。
2. 将本文件导入 Stash「覆写」，替换旧的同名主覆写；不要当作完整配置导入，也不要叠加两份完整分流覆写。
3. 地区手动组直接列出原生节点；Auto/Fallback 是独立组，可从 Proxy、业务组及 DNS-Global 选择。没有 `HK-Manual` 中间组。
4. 普通 Apple TV 的 `Video-AppleTV` 默认 DIRECT；F1 可选择美国出口，DNS-Global 同时选择对应出口。

139 个组保留最新 Clash 的相对顺序，去除 Mac 专用字幕桥接和 MacAppUpdate。空地区按 Stash 的行为可能退为 DIRECT；未知地区节点仍可在 AllServer 手动选择。原节点若与固定策略组重名，或节点本身依赖被替换的机场策略组，需要先解决该结构冲突，不能承诺支持任何特殊 YAML。

## DNS 设置保持 `.8`

| 参数 | 行为 |
| --- | --- |
| `dns.proxy-server-nameserver` | 不声明，通过字典合并原样继承 |
| `dns.default-nameserver` | 阿里两个 IP 地址形式的 DoH |
| `dns.nameserver` | Google 与 Cloudflare 的 IP 地址形式 DoH |
| `dns.nameserver-policy` | `geosite:private` 使用系统 DNS；GeositeCN_Domain 使用阿里 |
| `dns.follow-rule` | 开启；境外 DNS 请求进入 DNS-Global，阿里进入 DNS-China |
| `dns.fallback` | 清空，避免混入原机场其它解析器 |
| `dns.fake-ip-filter` | 恢复 `.8` 的 `['*']` |
| 地区组测速 | 恢复 `.8` 的 300 秒及 lazy；业务菜单仍为原有 `interval: -1` |

Stash 文档没有提供等同于 Mihomo `direct-nameserver` 的选项。不能承诺业务组选 DIRECT 就自动改用阿里，也不能把 DNS-Global 当成每个业务组出口的自动镜像。上述局限不在本轮规则精简中通过改 DNS 参数绕开。

DNS 字典保持递归合并；nameserver、policy、fallback、fake-ip-filter 各自 `#!replace`。策略组、规则集、rules、hosts 整体替换。仅其它客户端使用的原始字段可能还存在于合并文本中。

## 验证范围

- 规则优化测试覆盖域名后缀、精确域名、通配符、同策略关键词、匹配顺序、IP 网段边界、解析选项和 DNS 共享集合。
- 离线模型比较 40,715 个域名样例、2,431 个 IP 边界样例，策略结果一致。GeoIP / ASN / 网络组合条件的规则顺序逐项保持，未伪称模型模拟了这些外部数据库和网络条件。
- 93 个 MRS 通过隔离的 Mihomo 文件解析检查，不启动监听器，不连接节点。
- 节点、节点 DNS 和三份现有本地订阅通过离线合并检查；不获取任何机场 URL。
- 与 `.8` 对比，DNS 以及所有策略组的完整内容相同；普通 DNS 与节点 DNS 的职责没有更改。

以上均非手机内存实测。文件体积缩小不等于运行内存按相同比例下降，不能据此宣称告警已消失。本轮没有启用、切换或重启设备网络配置。

## 维护及隐私

`build_native.py` 生成覆写；`slim_rules.py` 只读取已有的公共规则输入；`verify_rule_equivalence.py` 做离线对比；`audit_local.py` 仅读取明确指定的本地机场文件，报告数量和完整性，不输出凭据。使用 Python 3、PyYAML 和 Mihomo 的规则转换命令。

```sh
python3 -m unittest -v test_native test_slim_rules
python3 build_native.py --out dist
```

蓝通一次性旧链接不得刷新、重试或 HEAD 探测。更新需要由用户导入新链接。公共规则下载与机场订阅下载是不同用途；节点凭据、私人配置和手机截图不得加入公共发布包。

官方依据：
- https://stash.wiki/configuration/override
- https://stash.wiki/rules/rule-set
- https://stash.wiki/faq/effective-stash
- https://stash.wiki/features/dns-server
- https://stash.wiki/proxy-protocols/proxy-groups
