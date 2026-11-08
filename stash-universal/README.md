# 通用 Stash 分流覆写

直接使用机场提供的原始配置或订阅，额外启用一份通用分流覆写。覆写不包含机场节点、密码、UUID、订阅地址或机场专用 DNS。

## 安装

适用于 iOS Stash 3.6 及更新版本。

1. 直接在 Stash 导入或选择机场原始订阅。
2. 从以下地址导入覆写并启用：
   `https://raw.githubusercontent.com/sixvable/proxy-rule-icons-png/stash-release/universal.stoverride`
3. 关闭其它会完整替换 DNS、策略组或分流的旧覆写。然后重新连接。
4. 普通 Apple TV 媒体策略 `Video-AppleTV` 默认直连；若有历史选择，请确认选择 `DIRECT`。

两个覆写均在首行写入 `#SUBSCRIBED`，记录各自的 GitHub 更新来源；本地 iCloud 副本也可以保留这一来源标记。标记不是普通 YAML 更新间隔字段。

[一键导入通用覆写](https://link.stash.ws/install-override/raw.githubusercontent.com/sixvable/proxy-rule-icons-png/stash-release/universal.stoverride) · [一键导入可选 IPv6 覆写](https://link.stash.ws/install-override/raw.githubusercontent.com/sixvable/proxy-rule-icons-png/stash-release/ipv6.stoverride)

本覆写对 `proxy-groups`、`rule-providers`、`rules` 使用 `#!replace`，不累加旧机场的大型分流列表。节点由 `include-all: true` 从当前主配置动态获取，机场原有的订阅更新机制继续工作。

`dns`、`hosts`、`proxies`、`proxy-providers` 完全由主配置保留。机场 DNS 若原本关闭 IPv6，这一状态也会保留。需要时可另行导入同目录的 `可选_开启IPv6.stoverride`；它仅开启 IPv6，不更换 DNS 服务器。Stash 的双栈连接不等于每次强制选择 IPv6。

一次性订阅仍应仅按机场方式导入一次。本覆写不读取、不转换、不自动重试任何机场订阅。

## 减少规则负担的方法

- 将公开的混合规则拆成 `domain` 和 `ipcidr` 集合，并编译为 MRS；不再在手机加载大型 `classical` 集合。
- 将原有 GEOSITE 分流展开为可检查的公开规则，与相邻同策略规则合并；精确域名、后缀与网段去重，CIDR 按地址族合并。
- 国内 IP 兜底排在具体应用之后，避免国内 DNS 给出的地址让 YouTube、AI 等明确的应用规则失去优先权。国内域名列表仍单独保留。
- 少量关键词、正则和 ASN 匹配继续保留为普通规则。不能编码为 MRS 的嵌入式通配符转换为原生正则，避免静默丢弃规则。
- 移除 iOS 不生效的进程规则、Mac 应用更新专用菜单、字幕工具策略与专用端口。保留普通 Apple TV、视频、AI、社交、游戏和工具分流。
- 保留当前三机场都有节点的地区菜单。其它地区节点仍在 `AllServer`，避免选择当前机场没有节点、在 Stash 中可能按 DIRECT 处理的空策略组。
- DNS 池不按 RLT 名称排除节点。覆写不改变任何节点协议参数，也不能为客户端添加原本不支持的协议。

主分流行数与全部匹配条目数不同；MRS 并不是把所有条目变成零。优化来自索引结构、去重和减少顺序匹配，不能仅凭文件大小推算 iPhone 内存，更不能保证所有设备的启动问题已经消失。

## 更新与验证

`main/stash-universal` 保存通用配置生成器；`stash-release` 保存已校验的覆写和规则。GitHub Actions 按计划每日北京时间 06:17 重新读取公开上游，编译并检查后再发布；GitHub 调度可能延迟。下载或校验失败时，保留上一次成功发布的规则。只有公开规则会进入仓库和工作流，不需要机场订阅凭据或额外账户密钥。

Stash 中的规则集合配置为每 24 小时更新，实际执行时机取决于客户端运行状态。覆写本身通过首行的 GitHub 来源更新，更新检查时机由 Stash 的覆写设置与运行状态控制。不要将规则集合的 `interval: 86400` 理解成覆写自身的更新间隔；iCloud 本身只负责同步文件。同步后可在覆写页手动更新一次，确认版本及来源已被识别；若旧条目仍显示为本地，使用上面的官方一键远程导入链接替换同名条目。离线缓存可以复制到 Stash 的 `resources/ruleset/universal-stash-v1/` 目录。

本地和自动检查包括规则覆盖、引用关系、循环、规则文件格式和 MRS 实际解析。MRS 由 Mihomo 工具编译与检查，仅用于验证文件，不接入用户流量；这不等于 iPhone 上的 Stash 已完成加载或连接实测。

完整数据量与生成来源见 `stash-release/build-report.json`。源规则列表见 `recipe.json`，文本规则与 MRS 同时发布，便于检查。

## 来源与说明

公开规则来源：[Accademia/Additional_Rule_For_Clash](https://github.com/Accademia/Additional_Rule_For_Clash)、[blackmatrix7/ios_rule_script](https://github.com/blackmatrix7/ios_rule_script)、[MetaCubeX/meta-rules-dat](https://github.com/MetaCubeX/meta-rules-dat) 及 [Cloudflare 官方 IP 列表](https://www.cloudflare.com/ips/)。上游规则遵循各自的许可；本仓库列明来源，转换不表示这些站点或服务提供商背书。

Stash 官方文档：[覆写及替换语法](https://stash.wiki/configuration/override)、[规则集合与 MRS](https://stash.wiki/rules/rule-set)、[高效配置](https://stash.wiki/faq/effective-stash)、[动态引用节点](https://stash.wiki/proxy-protocols/proxy-groups)、[DNS](https://stash.wiki/features/dns-server)。

注意：Stash 文档中的覆写参数和 `pre-matching` 目前标注为 3.7 Beta 功能，本配置不依赖这些功能。普通 YAML 覆写也不会自动识别机场后执行三套条件分支；跨机场通用的办法是保留原始 DNS，而非在覆写里硬编码三套 DNS。

更新机制依据：[Stash 托管来源标记](https://stash.wiki/features/service-provider-subscription)、[官方远程覆写导入方式](https://stash.wiki/faq/url-schema)。当前环境已观察到已有远程 `.stoverride` 使用同样的 `#SUBSCRIBED` 首行。手机端是否已经识别，以及自动刷新是否实际执行，需要在 Stash 中确认；这里不把主配置文档的默认 12 小时间隔直接套用到覆写。
