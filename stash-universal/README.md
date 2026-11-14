# Stash 共用分流覆写：本地节点池

地区组同时提供 Auto、Fallback、DIRECT 和当前机场的具体节点；DNS-Global 提供 HongKong、America、Japan、Singapore、AllServer 和 DIRECT。没有 Manual 中间组，也不需要为不同机场维护不同分流覆写。

**使用条件：主配置必须提供名为 `Airport` 的本地节点池。原生机场配置需先离线适配，不能直接叠加节点池覆写。**

## 已验证的行为

2026-11-14，版本 `2026.11.14.7` 在同一台 iPhone 的 Stash 中依次加载了三份不同机场的本地配置：

| 本地样本 | 保留节点 | 香港节点 | 美国节点 | 核心启动 | 香港 Auto / Fallback / 具体节点选择 | DNS-Global 地区菜单 |
| --- | ---: | ---: | ---: | --- | --- | --- |
| A | 66 | 4 | 8 | 通过 | 通过 | 通过 |
| B | 31 | 6 | 4 | 通过 | 通过 | 通过 |
| C | 21 | 4 | 2 | 通过 | 通过 | 通过 |

三个样本始终使用同一份覆写。完成后已恢复原来的机场及业务策略。实测覆盖核心加载、菜单和选择状态，不代表所有节点都可用，也不代表已经测量吞吐量或直播画质。离线回归检查另覆盖任意第四家机场、节点改名和增删、空地区、未知地区、YAML 锚点及外部 provider 的本地缓存。

此前两种失败的原因不同：`include-all` 在所测 iOS 运行时没有保留手写的子组选项；把原始节点名写进 `proxies` 虽能修复单个机场的菜单，却会在换机场后产生不存在的引用。本版使用 `proxies` 引用公共策略组、`use: [Airport]` 引用实际节点，避免绑定任何机场的节点名称。

## 为任意机场准备入口

只读取已有的本地 YAML，不获取订阅链接。需要 Python 3 和 PyYAML：

```sh
python3 -m pip install PyYAML==6.0.2
python3 prepare_local_airport.py '/path/to/local-airport.yaml' \
  --override '/path/to/universal-provider.stoverride' \
  --out '/path/to/new-private-output'
```

若原配置使用 `proxy-providers`，必须额外用 `--nodes-local '/path/to/existing-cache.yaml'` 指定已有的节点缓存，可重复提供。程序不会访问配置中的 URL，也不会自动跟随其中的缓存路径。没有缓存时明确停止，不联网补齐。

生成两类私有文件：

| 文件 | 放入 Stash iCloud 目录的位置 |
| --- | --- |
| `profiles/机场_本地节点池.yaml` | Stash 根目录，与原配置同级 |
| `resources/proxy-providers/Airport-*.yaml` | 保留该目录结构，放入 Stash 的 `resources/proxy-providers/` |

在 `override/` 放入公共 `universal-provider.stoverride`，停用之前的完整分流覆写，启用本版，再选择对应的本地节点池入口。切换机场只切换入口，覆写保持不变。不要同时启用蓝通专用旧版、原生兼容旧版和本版。

生成的入口形如：

```yaml
proxy-providers:
  Airport:
    path: ./proxy-providers/Airport-example.yaml
```

同一 `Airport` 名称在不同入口中指向各自的文件。覆写及其规则不存放机场节点、凭据或机场订阅地址。

## 一次性订阅与更新

机场链接可能是阅后即焚链接。不要刷新、重试、HEAD 探测或把旧链接交给 provider。入口不含 `#SUBSCRIBED`；`Airport` 只有 `path`，没有 `url`、`interval` 或远程回退。

节点是本地快照，不会自动更新。以后需更新时，由用户导入新的有效链接取得新本地配置，再离线生成新的入口和节点文件。程序不会获取或消耗新链接。缺失文件应从本地备份恢复，不能重试旧链接。

原机场文件仍可能保留自己的更新关联；转换工具不修改原文件。一次性订阅的原文件应另外解除更新关联，保留离线备份。地区组的自动延迟检查、公共规则更新与机场订阅下载是三件不同的事。

**输出入口、节点文件及设备截图均为私有数据，不能放入 GitHub、公开下载包或公共日志。** 公共发布流程只打包生成器、合成测试和公共规则。

## 兼容范围与 DNS

- 适配器支持内联 `proxies`，以及显式提供的本地 provider 缓存；保留 DNS、hosts、IPv6 和其它非分流基础设置的 YAML 含义。
- 空节点、冲突的重复节点名、与策略组同名的节点、依赖已移除原策略组的 `dialer-proxy` 会明确报错，需先处理原配置。特殊协议仍须由设备上的 Stash 版本支持。
- 地区分类依赖节点名称。没有该地区节点时不能凭空生成出口；未知地区可从 AllServer 查找。信息类节点仍按既有过滤规则隐藏。
- DNS-Global 控制命中它的连接；Stash 内部 DNS 是否跟随分流，取决于入口自身的 `dns.follow-rule` 等设置。本覆写不统一或改写机场 DNS。
- 保留 112 个策略组的顺序、已精简的 Apple TV / OneDrive / DNS 分流，以及局域网、防 HTTPDNS、防劫持优先顺序。
- 不包含 Mac 字幕桥接端口、`AppleTV-Media-IPv6` 或独立 IPv6 覆写。

## 公共构建与兼容旧地址

`universal-provider.stoverride` 是本版节点池覆写。`universal.stoverride` 继续保留旧原生配置兼容方式，不自动把尚未适配的用户迁移到节点池版。

`build.py` 只编译公共规则；GitHub Actions 测试通过后更新 `stash-release`。构建日志中的离线检查不自动宣称任意新设备通过真机验收；上面的实测记录只对应本次已验收版本。

```sh
python3 -m unittest test_build test_provider_profile test_generic_airport
```

官方依据：[代理集和本地路径](https://stash.wiki/proxy-protocols/proxy-providers)、[策略组](https://stash.wiki/proxy-protocols/proxy-groups)、[组合 use 与 proxies 的示例](https://stash.wiki/configuration/example-config)、[覆写与替换规则](https://stash.wiki/configuration/override)。
