# Proxy Rule Icons PNG

PNG icon assets converted from SVG sources for Clash Verge Rev and Stash proxy rule configurations.

## 桌面 Clash 全局覆写

[下载 Clash_rules_desktop.js](https://raw.githubusercontent.com/sixvable/proxy-rule-icons-png/main/Clash_rules_desktop.js) · [查看源码](Clash_rules_desktop.js)

2026-11-15 桌面版：保留原机场节点、provider 和节点 DNS，使用统一 DNS、地区策略组及分流。仅当节点 DNS 缺失时补齐阿里 DoH；必要的机场依赖会保留为隐藏组。

1. 保留原机场订阅，将 JS 全文粘贴到 Clash Verge Rev 的“全局扩展脚本”。
2. 将“全局扩展配置”设为 `{}`，清理会再次覆盖它的旧订阅扩展，不叠加旧完整覆写。
3. 保存并重新加载本地配置，核对运行配置与联网。无需重新获取机场节点；一次性订阅不能刷新或重复拉取。

这是公开覆写文件，不包含机场链接或节点凭据。粘贴的脚本不会自行更新，后续使用上面的固定地址获取新版。字幕专用端口 `18767` 固定 DIRECT；字幕桥接需另外启动字幕工具及完成本机证书设置。普通 `DNS-Global` 不会自动跟随每个业务策略组，应按需要自行选择。

本次只更新桌面 JS。手机配置未随此次发布调整；自动测试不代表实机播放、速度或内存表现。

## jsDelivr

```text
https://cdn.jsdelivr.net/gh/sixvable/proxy-rule-icons-png@main/icons/<name>.png
```

## Icons

| Name | PNG | Source |
| --- | --- | --- |
| region-asean | [png](https://cdn.jsdelivr.net/gh/sixvable/proxy-rule-icons-png@main/icons/region-asean.png) | [source](https://cdn.jsdelivr.net/gh/lipis/flag-icons@main/flags/1x1/asean.svg) |
| region-north-america | [png](https://cdn.jsdelivr.net/gh/sixvable/proxy-rule-icons-png@main/icons/region-north-america.png) | [source](https://commons.wikimedia.org/wiki/Special:FilePath/North_America_(orthographic_projection).svg) |
| region-east-asia | [png](https://cdn.jsdelivr.net/gh/sixvable/proxy-rule-icons-png@main/icons/region-east-asia.png) | [source](https://commons.wikimedia.org/wiki/Special:FilePath/East_Asia_(orthographic_projection).svg) |
| region-west-asia | [png](https://cdn.jsdelivr.net/gh/sixvable/proxy-rule-icons-png@main/icons/region-west-asia.png) | [source](https://commons.wikimedia.org/wiki/Special:FilePath/Western_Asia_(orthographic_projection).svg) |
| app-synology | [png](https://cdn.jsdelivr.net/gh/sixvable/proxy-rule-icons-png@main/icons/app-synology.png) | [source](https://cdn.jsdelivr.net/gh/selfhst/icons/svg/synology.svg) |
| drive-dropbox | [png](https://cdn.jsdelivr.net/gh/sixvable/proxy-rule-icons-png@main/icons/drive-dropbox.png) | [source](https://cdn.jsdelivr.net/gh/homarr-labs/dashboard-icons/svg/dropbox.svg) |
| drive-mega | [png](https://cdn.jsdelivr.net/gh/sixvable/proxy-rule-icons-png@main/icons/drive-mega.png) | [source](https://cdn.jsdelivr.net/gh/selfhst/icons/svg/mega.svg) |
| drive-imgur | [png](https://cdn.jsdelivr.net/gh/sixvable/proxy-rule-icons-png@main/icons/drive-imgur.png) | [source](https://cdn.jsdelivr.net/gh/simple-icons/simple-icons@master/icons/imgur.svg) |
| drive-internet-archive | [png](https://cdn.jsdelivr.net/gh/sixvable/proxy-rule-icons-png@main/icons/drive-internet-archive.png) | [source](https://cdn.jsdelivr.net/gh/selfhst/icons/svg/internet-archive.svg) |
| finance-wise | [png](https://cdn.jsdelivr.net/gh/sixvable/proxy-rule-icons-png@main/icons/finance-wise.png) | [source](https://cdn.jsdelivr.net/gh/simple-icons/simple-icons@master/icons/wise.svg) |
| crypto-binance | [png](https://cdn.jsdelivr.net/gh/sixvable/proxy-rule-icons-png@main/icons/crypto-binance.png) | [source](https://cdn.jsdelivr.net/gh/simple-icons/simple-icons@master/icons/binance.svg) |
| crypto-okx | [png](https://cdn.jsdelivr.net/gh/sixvable/proxy-rule-icons-png@main/icons/crypto-okx.png) | [source](https://cdn.jsdelivr.net/gh/simple-icons/simple-icons@master/icons/okx.svg) |
| finance-monzo | [png](https://cdn.jsdelivr.net/gh/sixvable/proxy-rule-icons-png@main/icons/finance-monzo.png) | [source](https://cdn.jsdelivr.net/gh/simple-icons/simple-icons@master/icons/monzo.svg) |
| finance-revolut | [png](https://cdn.jsdelivr.net/gh/sixvable/proxy-rule-icons-png@main/icons/finance-revolut.png) | [source](https://cdn.jsdelivr.net/gh/simple-icons/simple-icons@master/icons/revolut.svg) |
| shopping-ebay | [png](https://cdn.jsdelivr.net/gh/sixvable/proxy-rule-icons-png@main/icons/shopping-ebay.png) | [source](https://cdn.jsdelivr.net/gh/homarr-labs/dashboard-icons/svg/ebay.svg) |
| shopping-patreon | [png](https://cdn.jsdelivr.net/gh/sixvable/proxy-rule-icons-png@main/icons/shopping-patreon.png) | [source](https://cdn.jsdelivr.net/gh/homarr-labs/dashboard-icons/svg/patreon.svg) |
| game-gog | [png](https://cdn.jsdelivr.net/gh/sixvable/proxy-rule-icons-png@main/icons/game-gog.png) | [source](https://cdn.jsdelivr.net/gh/simple-icons/simple-icons@master/icons/gogdotcom.svg) |
| game-rockstar | [png](https://cdn.jsdelivr.net/gh/sixvable/proxy-rule-icons-png@main/icons/game-rockstar.png) | [source](https://cdn.jsdelivr.net/gh/simple-icons/simple-icons@master/icons/rockstargames.svg) |
| game-ea | [png](https://cdn.jsdelivr.net/gh/sixvable/proxy-rule-icons-png@main/icons/game-ea.png) | [source](https://cdn.jsdelivr.net/gh/selfhst/icons/svg/electronic-arts.svg) |
| game-ubisoft | [png](https://cdn.jsdelivr.net/gh/sixvable/proxy-rule-icons-png@main/icons/game-ubisoft.png) | [source](https://cdn.jsdelivr.net/gh/simple-icons/simple-icons@master/icons/ubisoft.svg) |
| short-kuaishou | [png](https://cdn.jsdelivr.net/gh/sixvable/proxy-rule-icons-png@main/icons/short-kuaishou.png) | [source](https://cdn.jsdelivr.net/gh/simple-icons/simple-icons@master/icons/kuaishou.svg) |
| showip-xiaohongshu | [png](https://cdn.jsdelivr.net/gh/sixvable/proxy-rule-icons-png@main/icons/showip-xiaohongshu.png) | [source](https://cdn.jsdelivr.net/gh/simple-icons/simple-icons@master/icons/xiaohongshu.svg) |
| showip-xigua | [png](https://cdn.jsdelivr.net/gh/sixvable/proxy-rule-icons-png@main/icons/showip-xigua.png) | [source](https://cdn.jsdelivr.net/gh/simple-icons/simple-icons@master/icons/bytedance.svg) |
| showip-tieba | [png](https://cdn.jsdelivr.net/gh/sixvable/proxy-rule-icons-png@main/icons/showip-tieba.png) | [source](https://cdn.jsdelivr.net/gh/homarr-labs/dashboard-icons/svg/baidu.svg) |
| showip-douban | [png](https://cdn.jsdelivr.net/gh/sixvable/proxy-rule-icons-png@main/icons/showip-douban.png) | [source](https://cdn.jsdelivr.net/gh/simple-icons/simple-icons@master/icons/douban.svg) |
| social-reddit | [png](https://cdn.jsdelivr.net/gh/sixvable/proxy-rule-icons-png@main/icons/social-reddit.png) | [source](https://cdn.jsdelivr.net/gh/homarr-labs/dashboard-icons/svg/reddit.svg) |
| social-whatsapp | [png](https://cdn.jsdelivr.net/gh/sixvable/proxy-rule-icons-png@main/icons/social-whatsapp.png) | [source](https://cdn.jsdelivr.net/gh/homarr-labs/dashboard-icons/svg/whatsapp.svg) |
| social-signal | [png](https://cdn.jsdelivr.net/gh/sixvable/proxy-rule-icons-png@main/icons/social-signal.png) | [source](https://cdn.jsdelivr.net/gh/homarr-labs/dashboard-icons/svg/signal.svg) |
| news-wikipedia | [png](https://cdn.jsdelivr.net/gh/sixvable/proxy-rule-icons-png@main/icons/news-wikipedia.png) | [source](https://cdn.jsdelivr.net/gh/homarr-labs/dashboard-icons/svg/wikipedia.svg) |
| ai-grok | [png](https://cdn.jsdelivr.net/gh/sixvable/proxy-rule-icons-png@main/icons/ai-grok.png) | [source](https://cdn.jsdelivr.net/gh/homarr-labs/dashboard-icons/svg/grok.svg) |
| ai-gemini | [png](https://cdn.jsdelivr.net/gh/sixvable/proxy-rule-icons-png@main/icons/ai-gemini.png) | [source](https://cdn.jsdelivr.net/gh/homarr-labs/dashboard-icons/svg/google-gemini.svg) |
| tool-adobe | [png](https://cdn.jsdelivr.net/gh/sixvable/proxy-rule-icons-png@main/icons/tool-adobe.png) | [source](https://cdn.jsdelivr.net/gh/homarr-labs/dashboard-icons/svg/adobe.svg) |
| tool-pinterest | [png](https://cdn.jsdelivr.net/gh/sixvable/proxy-rule-icons-png@main/icons/tool-pinterest.png) | [source](https://cdn.jsdelivr.net/gh/homarr-labs/dashboard-icons/svg/pinterest.svg) |
| remote-rustdesk | [png](https://cdn.jsdelivr.net/gh/sixvable/proxy-rule-icons-png@main/icons/remote-rustdesk.png) | [source](https://cdn.jsdelivr.net/gh/homarr-labs/dashboard-icons/svg/rustdesk.svg) |
