# 通用 Stash 分流覆写

直接使用机场原始订阅，再启用一份通用分流覆写。当前版本按最新 Clash Verge 分流同步，同时保留原有 iOS 适配：不写入机场节点、凭据、订阅地址或 DNS，不接入 Mac 本机字幕工具。

## 安装与升级

适用于 iOS / tvOS Stash 3.6+。只需一份主覆写：

`https://raw.githubusercontent.com/sixvable/proxy-rule-icons-png/stash-release/universal.stoverride`

[一键导入通用覆写](https://link.stash.ws/install-override/raw.githubusercontent.com/sixvable/proxy-rule-icons-png/stash-release/universal.stoverride)

1. 选择机场原始订阅，启用“通用分流｜保留机场 DNS”。
2. 更新已有同名主覆写，避免同时启用新旧两份完整分流。
3. **停用并移除旧的“可选｜保留原 DNS 并开启 IPv6”覆写。** 本次停止提供独立 IPv6 覆写，主覆写也不设置 `ipv6` 或 `dns.ipv6`。实际 IPv6 行为由机场原配置、Stash 及当前网络决定；移除强制开启不表示强制关闭 IPv6。
4. 关闭其它完整分流覆写，重新连接，核对 `Video-AppleTV`、`DNS-Global` 与 `Proxy` 的选择。客户端可能保留此前选择。

主覆写保留原 GitHub 更新地址和首行 `#SUBSCRIBED`。iCloud 本地副本沿用 `通用分流_保留机场DNS.stoverride`，不必另外添加一个主覆写条目。远端移除 IPv6 文件不会替用户删除手机或 iCloud 中已经保存的副本，需要在设备上停用或移除。

## 本次同步

- `DNS-Global-Auto` 改为手动选择组 `DNS-Global`；移除 `Global-CDN` 及其宽泛 CDN 分流。
- `Proxy`、`Final`、地区及自动测速/回退组放在最上方，`Video-AppleTV` 紧接其后；业务组按最新版相对顺序排列。
- 局域网、HTTPDNS、防劫持规则提前；同步 Apple TV、OneDrive、DNS 的精简规则。
- DNS 服务分流采用域名在前、IP 在后，IP 规则使用 `no-resolve`；移除按 53/853 端口与 GEOIP 宽泛分类的旧规则。
- Apple TV 播放接口、清单与媒体进入 `Video-AppleTV`。不含 Mac 字幕拦截、18767/18768 端口、`AppleTV-Media-IPv6` 或地址族优先设置。
- 修正公开规则中重复的 REJECT-DROP 动作，避免生成带两个动作字段的规则；修正地区筛选正则中的重复转义。

保留原先适用于三家机场的地区菜单，其它地区节点可在 `AllServer` 中选择。Stash 将空策略组当作 DIRECT，因此没有照搬全部桌面地区组。Mac 应用更新与字幕工具的菜单仍不加入。

## 策略组菜单修复（2026.11.14.2）

之前的 11 个组同时使用 `include-all: true` 和显式 `proxies`。虽然 YAML 中写有子组选项，用户在 Stash 中实际看不到地区组的 Auto / Fallback，也看不到 DNS-Global 的地区选项。本版将显式菜单与节点收集拆开，避免依赖两者在不同客户端中的合并行为。

| 菜单 | 可选项 |
| --- | --- |
| HongKong | HK-Auto、HK-FallBack、HK-Manual、DIRECT |
| America | US-Auto、US-FallBack、US-Manual、DIRECT |
| 其它地区组 / AllServer | 对应的 Auto、FallBack、Manual、DIRECT |
| DNS-Global | HongKong、America、Japan、Singapore、All-Manual、DIRECT |

Auto 自动选低延迟节点；FallBack 按节点顺序选择可用节点；Manual 是手动选择具体节点的列表。若要固定香港的某个节点，先在 `HK-Manual` 选择节点，再将 `HongKong` 选择为 `HK-Manual`。该操作会被所有引用 HongKong 的业务组共同使用。

地区菜单与 DNS-Global 只写 `proxies`，不带 `include-all` 或 `filter`；Manual、Auto、FallBack 只负责按原地区正则收集机场节点。机场订阅更新后，这些节点列表继续自动更新。为保留跨机场通用性，具体节点不硬编码在覆写中。

Manual 组放在地区菜单之后、自动测速组之前，保持可见便于选节点；Auto / FallBack 延续隐藏顶层列表的设置，仍通过地区菜单引用。相比 Clash Verge，手动固定节点多一层 Manual 选择，这是本版明确保留的 Stash 适配差异。

本次不改分流规则或 DNS 设置。已检查所有 11 处混合写法、组间循环引用及各地区节点筛选；未连接 iPhone，不能把结构验证等同于 Stash 界面实测。

## DNS 保留逻辑

**整个 `dns`、`hosts`、`proxies`、`proxy-providers` 都由机场主配置保留。**

- 机场提供专用 `proxy-server-nameserver`，继续使用原值。
- 机场没有这一项，继续按原有 DNS 配置与 Stash 行为处理；本覆写不会改普通 `nameserver`，也不会自动补入阿里 DNS。
- 普通 Stash YAML 覆写不执行 Clash Verge 的 `main(config)` 条件脚本。
- `DNS-Global` 控制命中对应分流的 DNS 服务连接；本覆写不改变 `dns.follow-rule`，不承诺 Stash 内部 DNS 查询会随这个组切换。
- Stash 内部 DNS 默认直接出站；主配置开启 `follow-rule` 后，常规 DNS 查询才按代理规则转发。`proxy-server-nameserver` 使用独立解析链路。

普通 Apple TV 视频可选择 DIRECT；F1 可选择 America。**仅切换 DNS-Global 不等于改变 Stash 内部解析出口。** 本次沿用原 Stash 版本“保留机场 DNS”的约定，不复制 Mihomo 的 `#DNS-Global` 写法。

## 规则、缓存与更新

公开混合规则按域名和 IP 拆分、去重并编译为 MRS；关键词、正则等保留为普通规则，不在手机加载大型 classical 集合。GEOSITE 数据展开成可检查的公开规则并验证覆盖。

保留 Stash 适配：`GEOIP,CN` 兜底放在具体应用之后，避免过早真实解析而抢先匹配应用分流。

新版规则发布在 `rules-v2/`，本地缓存位于 `./ruleset/universal-stash-v2/`。旧 `rules/` 保留，供尚未更新主覆写的设备过渡；新版不会读取同编号旧缓存。

`proxy-groups`、`rule-providers`、`rules` 使用 `#!replace` 整体替换。节点由 `include-all` 从机场原始配置动态获取，机场订阅更新继续工作。

`main/stash-universal` 保存生成器与公开来源，`stash-release` 保存验证通过的发布文件。原 GitHub Actions 每日北京时间 06:17 获取公开上游，编译和检查成功后发布；调度可能延迟，失败保留上次发布。独立 IPv6 覆写不再生成或发布。

规则集合的 `interval: 86400` 不是主覆写更新间隔。主覆写更新时机由 Stash 决定，iCloud 只负责同步文件。

## 验证范围

检查包含策略组引用和循环、规则顺序、地区正则、域名及网段覆盖、无 DNS/IPv6 覆盖、重复拒绝动作及 MRS 实际解析。MRS 使用 Mihomo 在隔离配置中验证，不接入用户流量；不能替代 iPhone 上的 Stash 加载、DNS 或播放测速。未声称完成手机实测。

## 来源

公开规则来自 [Accademia/Additional_Rule_For_Clash](https://github.com/Accademia/Additional_Rule_For_Clash)、[blackmatrix7/ios_rule_script](https://github.com/blackmatrix7/ios_rule_script)、[MetaCubeX/meta-rules-dat](https://github.com/MetaCubeX/meta-rules-dat)，遵循各自许可。完整来源和生成统计见 `recipe.json`、`build-report.json`。

官方文档：[覆写合并](https://stash.wiki/configuration/override)、[规则集合与 MRS](https://stash.wiki/rules/rule-set)、[策略组](https://stash.wiki/proxy-protocols/proxy-groups)、[DNS](https://stash.wiki/features/dns-server)、[高效配置](https://stash.wiki/faq/effective-stash)。
