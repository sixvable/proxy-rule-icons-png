# 通用 Stash 分流覆写

## 节点池版修复（待完成原生菜单验收）

2026-11-14 已在 iPhone 的 Stash 中确认：`include-all` 开启后，显式 `proxies` 中的 HK-Auto、HK-FallBack、DIRECT 没有出现在地区菜单；关闭它后，三个选项正常出现。单独保留 `filter` 不会导致这个问题。

节点池版改为 `proxies` 引用子组、`use: [Airport]` 引用当前机场的节点池。全部地区、AllServer、Auto、Fallback 共用当前入口的一个 Airport，不混用不同机场。没有独立的 Manual 组。

| 文件 | 对主配置的要求 |
| --- | --- |
| universal-provider.stoverride | 提供名为 Airport 的 proxy-provider |
| universal.stoverride | 兼容原生机场配置；include-all 菜单仅保证具体节点 |

旧订阅地址继续可用，避免尚未迁移的设备因缺少 Airport 而无法加载。不要同时启用两份完整分流。

## 私人入口与启动缓存

在本机运行：

```bash
python3 prepare_provider_profile.py '/path/to/机场.yaml' --out '/private/output'
```

输出：

- `profiles/机场_节点池.yaml`：保留 DNS、hosts、IPv6 和其它非分流基础设置，Airport 使用原订阅 URL。
- `resources/proxy-providers/Airport-*.yaml`：从当前原生配置提取的启动缓存。

将入口放入 Stash 的配置目录，将缓存按相同相对路径放入 Stash 的 resources 目录。保留原生机场配置，选择节点池入口，停用旧通用分流，再启用节点池版。节点池每 3600 秒尝试更新。

**输出含私人订阅链接或节点凭据，不可上传公共仓库。公共构建仅生成公开覆写与规则，不读取私人配置。**

缓存能帮助订阅暂不可用时启动，但不代表订阅更新成功。入口不会被机场的完整配置自动覆盖；机场修改 DNS 等基础设置时，需要先更新原生配置，再重新生成入口。

## 分流与 DNS

- 保持当前 Proxy、Final、地区、Video-AppleTV 与业务组顺序。
- 保持局域网、HTTPDNS、防劫持优先，以及已精简的 Apple TV、OneDrive、DNS 规则。
- DNS-Global 可选 HongKong、America、Japan、Singapore、AllServer、DIRECT。
- 主覆写不写入 DNS、hosts、IPv6、机场节点或订阅 URL。
- DNS-Global 只控制匹配它的连接，内部 DNS 是否按规则转发仍取决于入口的 dns.follow-rule 等设置。
- 不包含 Mac 字幕桥接端口、AppleTV-Media-IPv6 或单独的 IPv6 覆写。

## 构建与验证边界

GitHub Actions 编译公开 MRS 规则并生成两种覆写，共用 rules-v2 和现有缓存命名空间。节点池版使用独立订阅地址：

`https://raw.githubusercontent.com/sixvable/proxy-rule-icons-png/stash-release/universal-provider.stoverride`

配置、节点池转换和 MRS 检查不能代替 Stash 实机菜单检查。本分支的节点池版仍待完成原生验收，不作为已验证版本发布。

公开规则来源：[Accademia](https://github.com/Accademia/Additional_Rule_For_Clash)、[blackmatrix7](https://github.com/blackmatrix7/ios_rule_script)、[MetaCubeX](https://github.com/MetaCubeX/meta-rules-dat)。完整来源与统计见 recipe.json、build-report.json。

官方说明：[策略组](https://stash.wiki/proxy-protocols/proxy-groups)、[代理集](https://stash.wiki/proxy-protocols/proxy-providers)、[覆写](https://stash.wiki/configuration/override)。
