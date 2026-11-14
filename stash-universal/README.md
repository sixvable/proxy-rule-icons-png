# Stash 本地静态节点池修复草稿

## 当前验收状态

旧版在 iPhone Stash 中使用 include-all 时，HongKong 菜单未显示手写 proxies 中的 HK-Auto、HK-FallBack、DIRECT。关闭 include-all 时，这些子组选项可见。

候选方案用 proxies 引用 Auto/Fallback，用 use: [Airport] 引用具体节点。没有 Manual 中间组。新方案尚未完成原生手机菜单验收，不能称为已经修好；本分支不自动发布到正式覆写地址。

## 一次性订阅：只使用已有本地文件

机场链接可能是一次性／阅后即焚链接。不要刷新、重试、HEAD 探测或把旧链接交给 provider。转换器只接受本地 YAML，不接受远程 URL，也不调用网络。

```sh
python3 prepare_provider_profile.py '/path/to/已有机场缓存.yaml' --out '/private/new-output'
```

生成的入口使用：

```yaml
proxy-providers:
  Airport:
    path: ./proxy-providers/Airport-example.yaml
```

Airport 没有 url、interval 或远程回退。转换器移除所有 #SUBSCRIBED 指令；缺少该指令也可以转换，节点为空则报错，不尝试联网补齐。DNS、hosts、IPv6 和其它基础设置从本地文件保留。

输出 profiles/机场_本地节点池.yaml，以及 resources/proxy-providers 下的节点文件。两者仍含私人配置或节点凭据，只能本地保存，不得提交 GitHub 或公共发布包。公共构建只读取公开规则，不读取这些私人输出。

旧版远程 provider 预览包已经废弃，不能继续导入。原始机场文件如仍带 #SUBSCRIBED，也可能保留客户端更新关联；应先保存离线备份，再由用户明确授权解除关联。不能仅把刷新间隔设为 0 来保证不请求旧链接。不要为验证链接是否失效再次访问它。

## 节点更新和加载

节点只来自本地静态文件。缓存缺失时先找回本地备份，不回退到旧订阅 URL。以后需要更新，由用户明确提供新的本地配置文件，再在独立目录重新转换；本工具不获取或消耗新链接。

选择候选入口、停用旧覆写、启用节点池覆写、切换节点或启动连通性测试都会改变实际运行状态，需要单独授权。现阶段只完成离线转换与结构测试，Stash 路径加载、Auto/Fallback 同层菜单和节点可用性仍待真机验证。

地区组的自动测速间隔与机场订阅下载不同；本轮不启动实际测速。公共 rule-provider 可以有自己的公开规则更新时间，不会请求机场一次性 URL。

## 文件与分流

- universal-provider.stoverride 需要主配置提供本地 Airport。
- universal.stoverride 是旧原生配置兼容入口，include-all 仅保证显示具体节点；不能解决本次子组缺失。
- 不同时启用两份完整分流；DNS、hosts、IPv6 由入口保留。
- DNS-Global 保留 HongKong、America、Japan、Singapore、AllServer、DIRECT；是否用于内部 DNS 取决于入口设置。
- 不加入 Mac 字幕桥接、AppleTV-Media-IPv6 或独立 IPv6 覆写。

官方说明：[本地静态 provider](https://stash.wiki/proxy-protocols/proxy-providers)、[策略组](https://stash.wiki/proxy-protocols/proxy-groups)。
