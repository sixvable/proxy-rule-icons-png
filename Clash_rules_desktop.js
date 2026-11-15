// 完整全局扩展脚本。全部复制到 Clash Verge Rev 的全局扩展脚本。
// 全局扩展配置使用 {}。不需要刷新机场订阅。
// 保留香港首选、Apple TV 字幕固定直连及机场节点 DNS；缺失时补齐阿里 DoH。
function main(config) {
  var source = JSON.parse(JSON.stringify(config || {}));
  var result = JSON.parse(JSON.stringify(source));
  var airportDns = source.dns || {};
  function list(s) { return s ? s.split(",") : []; }
  var baseMenu = list("Proxy,America,Japan,UnitedKingdom,Australia,DIRECT,REJECT,REJECT-DROP,Final,HongKong,TaiWan,Singapore,Southeast.Asia,Canada,Germany,Netherlands,France,Korea,Europe,Oceania,West.Asia,Africa,South.America,AllServer,PASS");
  function menu(s) {
    var p = list(s);
    return p.concat(baseMenu.filter(function (n) { return p.indexOf(n) < 0; }));
  }
  function icon(s) { return "https://cdn.jsdelivr.net/gh/Koolson/Qure@master/IconSet/Color/" + s + ".png"; }
  var excludeFilter = "(?i)^(Apple TV 字幕桥接)$|流量|剩余|剩餘|到期|过期|過期|官网|官網|更新客户端|更新客戶端|订阅地址|訂閱地址|\\b(?:Traffic|Expir(?:e[ds]?|y|ation)|Remaining|Reset)\\b";
  var filters = {
    "HongKong":"(?i)香港|港|🇭🇰|Hong\\s*Kong|(?<![A-Z])(?:HK|HKG)[0-9]*(?![A-Z])",
    "TaiWan":"(?i)台|台湾|台灣|臺灣|湾|灣|🇹🇼|Taiwan|Taipei|Hinet|CHT|(?<![A-Z])(?:TW|TWN)[0-9]*(?![A-Z])",
    "Japan":"(?i)日本|东京|東京|大阪|🇯🇵|Japan|Tokyo|Osaka|(?<![A-Z])(?:JP|JPN|TYO|NRT|KIX)[0-9]*(?![A-Z])",
    "Singapore":"(?i)新加坡|坡|狮城|獅城|🇸🇬|Singapore|Singa|(?<![A-Z])(?:SG|SGP)[0-9]*(?![A-Z])",
    "Southeast.Asia":"(?i)东南亚|東南亞|东南亞|東南亚|新马泰|新馬泰|马来|馬來|马来西亚|馬來西亞|吉隆坡|泰国|泰國|曼谷|越南|胡志明|河内|河內|印尼|印度尼西亚|印度尼西亞|雅加达|雅加達|菲律宾|菲律賓|马尼拉|馬尼拉|柬埔寨|金边|金邊|老挝|老撾|寮国|寮國|缅甸|緬甸|仰光|文莱|汶萊|新加坡|狮城|獅城|🇸🇬|🇲🇾|🇹🇭|🇻🇳|🇮🇩|🇵🇭|🇰🇭|🇱🇦|🇲🇲|🇧🇳|Singapore|Malaysia|Kuala\\s*Lumpur|Thailand|Bangkok|Vietnam|Ho\\s*Chi\\s*Minh|Hanoi|Indonesia|Jakarta|Philippines|Manila|Cambodia|Phnom\\s*Penh|Laos|Myanmar|Burma|Yangon|Brunei|Southeast\\s*Asia|South\\s*East\\s*Asia|SE\\s*Asia|(?<![A-Z])(?:SG|SGP|MY|MYS|TH|THA|VN|VNM|ID|IDN|PH|PHL|KH|KHM|LAO|MM|MMR|BN|BRN)[0-9]*(?![A-Z])",
    "America":"(?i)美国|美國|美西|美东|美東|洛杉矶|洛杉磯|圣何塞|聖何塞|旧金山|舊金山|纽约|紐約|西雅图|西雅圖|🇺🇸|🇺🇲|United\\s*States|Los\\s*Angeles|San\\s*Jose|San\\s*Francisco|New\\s*York|Seattle|(?<![A-Z])(?:US|USA|LAX|SJC|SFO|NYC|SEA|IAD)[0-9]*(?![A-Z])",
    "Canada":"(?i)加拿大|🇨🇦|Canada|Toronto|Vancouver|(?<![A-Z])(?:CA|CAN|YYZ|YVR)[0-9]*(?![A-Z])",
    "UnitedKingdom":"(?i)英国|英國|🇬🇧|United\\s*Kingdom|Britain|London|(?<![A-Z])(?:UK|GB|GBR|LHR)[0-9]*(?![A-Z])",
    "Australia":"(?i)澳洲|澳大利亚|澳大利亞|澳州|🇦🇺|Australia|Sydney|Melbourne|(?<![A-Z])(?:AU|AUS|SYD|MEL)[0-9]*(?![A-Z])",
    "Germany":"(?i)德国|德國|🇩🇪|Germany|Frankfurt|Berlin|(?<![A-Z])(?:DE|DEU|FRA)[0-9]*(?![A-Z])",
    "Netherlands":"(?i)荷兰|荷蘭|尼德兰|尼德蘭|🇳🇱|Netherlands|Holland|Amsterdam|(?<![A-Z])(?:NL|NLD|AMS)[0-9]*(?![A-Z])",
    "France":"(?i)法国|法國|🇫🇷|France|Paris|(?<![A-Z])(?:FR|CDG)[0-9]*(?![A-Z])",
    "Korea":"(?i)韩国|韓國|首尔|首爾|🇰🇷|Korea|Seoul|(?<![A-Z])(?:KR|KOR|ICN)[0-9]*(?![A-Z])",
    "Europe":"(?i)欧洲|歐洲|欧盟|歐盟|🇪🇺|🇬🇧|🇩🇪|🇳🇱|🇫🇷|🇨🇭|🇸🇪|🇳🇴|🇫🇮|🇩🇰|🇮🇸|🇮🇪|🇪🇸|🇵🇹|🇮🇹|🇦🇹|🇧🇪|🇱🇺|🇨🇿|🇵🇱|🇭🇺|🇷🇴|🇧🇬|🇬🇷|Europe|European|英国|英國|德国|德國|法国|法國|荷兰|荷蘭|瑞士|瑞典|挪威|芬兰|芬蘭|丹麦|丹麥|冰岛|冰島|爱尔兰|愛爾蘭|西班牙|葡萄牙|意大利|奥地利|奧地利|比利时|比利時|卢森堡|盧森堡|捷克|波兰|波蘭|匈牙利|罗马尼亚|羅馬尼亞|保加利亚|保加利亞|希腊|希臘|United\\s*Kingdom|Britain|Germany|Netherlands|Holland|France|Switzerland|Sweden|Norway|Finland|Denmark|Iceland|Ireland|Spain|Portugal|Italy|Austria|Belgium|Luxembourg|Czech|Poland|Hungary|Romania|Bulgaria|Greece|London|Frankfurt|Berlin|Amsterdam|Paris|Zurich|Stockholm|Oslo|Helsinki|Copenhagen|Dublin|Madrid|Milan|Vienna|Brussels|Warsaw|Prague|(?<![A-Z])(?:EU|EUR|UK|GB|GBR|DE|DEU|NL|NLD|FR|FRA|CH|CHE|SE|SWE|NO|NOR|FI|FIN|DK|DNK|IS|ISL|IE|IRL|ES|ESP|PT|PRT|IT|ITA|AT|AUT|BE|BEL|LU|LUX|CZ|CZE|PL|POL|HU|HUN|RO|ROU|BG|BGR|GR|GRC|LHR|AMS|CDG|ZRH)[0-9]*(?![A-Z])",
    "Oceania":"(?i)大洋洲|澳洲|澳大利亚|澳大利亞|澳州|新西兰|新西蘭|纽西兰|紐西蘭|🇦🇺|🇳🇿|Oceania|Australia|New\\s*Zealand|Sydney|Melbourne|Auckland|Wellington|(?<![A-Z])(?:AU|AUS|NZ|NZL|SYD|MEL|AKL|WLG)[0-9]*(?![A-Z])",
    "West.Asia":"(?i)(^|[\\s\\[\\]()|/_-])西[亚亞]([\\s\\[\\]()|/_-]|$)|中东|中東|中亚|中亞|阿联酋|阿聯酋|迪拜|土耳其|伊斯坦布尔|伊斯坦堡|以色列|特拉维夫|特拉維夫|沙特|沙特阿拉伯|卡塔尔|卡塔爾|科威特|巴林|阿曼|约旦|約旦|黎巴嫩|伊朗|伊拉克|叙利亚|敘利亞|格鲁吉亚|格魯吉亞|亚美尼亚|亞美尼亞|阿塞拜疆|🇦🇪|🇹🇷|🇮🇱|🇸🇦|🇶🇦|🇰🇼|🇧🇭|🇴🇲|🇯🇴|🇱🇧|West\\s*Asia|Middle\\s*East|Dubai|Istanbul|Tel\\s*Aviv|Riyadh|Doha|(?<![A-Z])(?:AE|UAE|TR|TUR|IL|ISR|SAU|QA|QAT|KW|KWT|BH|BHR|OM|OMN|JO|JOR|LB|LBN|IR|IRN|IQ|IRQ|GE|GEO|AM|ARM|AZ|AZE)[0-9]*(?![A-Z])",
    "Africa":"(?i)非洲|南非|埃及|尼日利亚|尼日利亞|肯尼亚|肯尼亞|摩洛哥|阿尔及利亚|阿爾及利亞|突尼斯|加纳|加納|埃塞俄比亚|埃塞俄比亞|安哥拉|乌干达|烏干達|喀麦隆|喀麥隆|塞内加尔|塞內加爾|🇿🇦|🇪🇬|🇳🇬|🇰🇪|🇲🇦|Africa|South\\s*Africa|Egypt|Nigeria|Kenya|Morocco|Johannesburg|Cape\\s*Town|Cairo|Lagos|Nairobi|Casablanca|(?<![A-Z])(?:ZA|ZAF|EG|EGY|NG|NGA|KE|KEN|MA|MAR|DZ|DZA|TN|TUN|GH|GHA|ET|ETH|AO|AGO|UG|UGA|CM|CMR|SN|SEN)[0-9]*(?![A-Z])",
    "South.America":"(?i)南美|南美洲|拉美|拉丁美洲|巴西|阿根廷|智利|哥伦比亚|哥倫比亞|秘鲁|秘魯|乌拉圭|烏拉圭|巴拉圭|玻利维亚|玻利維亞|厄瓜多尔|厄瓜多爾|委内瑞拉|委內瑞拉|🇧🇷|🇦🇷|🇨🇱|🇨🇴|🇵🇪|South\\s*America|Latin\\s*America|Brazil|Argentina|Chile|Colombia|Peru|Sao\\s*Paulo|São\\s*Paulo|Rio|Buenos\\s*Aires|Santiago|Bogota|Lima|(?<![A-Z])(?:BR|BRA|AR|ARG|CL|CHL|CO|COL|PE|PER|UY|URY|PY|PRY|BO|BOL|EC|ECU|VE|VEN)[0-9]*(?![A-Z])",
    "AllServer":".+",
    "DNS-Global":"(?i)(?:香港|港|🇭🇰|Hong\\s*Kong|(?<![A-Z])(?:HK|HKG)[0-9]*(?![A-Z]))|(?:美国|美國|美西|美东|美東|洛杉矶|洛杉磯|圣何塞|聖何塞|旧金山|舊金山|纽约|紐約|西雅图|西雅圖|🇺🇸|🇺🇲|United\\s*States|Los\\s*Angeles|San\\s*Jose|San\\s*Francisco|New\\s*York|Seattle|(?<![A-Z])(?:US|USA|LAX|SJC|SFO|NYC|SEA|IAD)[0-9]*(?![A-Z]))|(?:日本|东京|東京|大阪|🇯🇵|Japan|Tokyo|Osaka|(?<![A-Z])(?:JP|JPN|TYO|NRT|KIX)[0-9]*(?![A-Z]))|(?:新加坡|坡|狮城|獅城|🇸🇬|Singapore|Singa|(?<![A-Z])(?:SG|SGP)[0-9]*(?![A-Z]))",
  };
  var groupTemplates = [
    {"name":null,"type":"select","icon":null,"proxies":null},
    {"name":null,"type":"select","icon":null,"include-all":true,"proxies":null,"filter":null,"exclude-filter":excludeFilter},
    {"name":null,"type":"url-test","include-all":true,"url":"https://www.gstatic.com/generate_204","interval":300,"lazy":true,"hidden":true,"expected-status":"204","tolerance":50,"filter":null,"exclude-filter":excludeFilter},
    {"name":null,"type":"fallback","include-all":true,"url":"https://www.gstatic.com/generate_204","interval":300,"lazy":true,"hidden":true,"expected-status":"204","filter":null,"exclude-filter":excludeFilter},
    {"name":null,"default-selected":"DIRECT","icon":null,"type":"select","proxies":null},
    {"name":null,"type":"select","icon":null,"proxies":null,"use":["AppleTV 字幕桥接节点"]},
    {"name":null,"icon":null,"type":"select","include-all":true,"default-selected":"HongKong","proxies":null,"filter":null,"exclude-filter":excludeFilter},
  ];
  var groupRows = [
    [0,"Proxy",icon("Rocket"),list("HongKong,TaiWan,Japan,Singapore,Southeast.Asia,America,Canada,UnitedKingdom,Australia,Germany,Netherlands,France,Korea,Europe,Oceania,West.Asia,Africa,South.America,AllServer,DIRECT")],
    [0,"Final",icon("Final"),list("Proxy,AllServer,DIRECT")],
    [1,"HongKong",icon("Hong_Kong"),list("HK-Auto,HK-FallBack,DIRECT"),filters["HongKong"]],
    [1,"TaiWan",icon("Taiwan"),list("TW-Auto,TW-FallBack,DIRECT"),filters["TaiWan"]],
    [1,"Japan",icon("Japan"),list("JP-Auto,JP-FallBack,DIRECT"),filters["Japan"]],
    [1,"Singapore",icon("Singapore"),list("SG-Auto,SG-FallBack,DIRECT"),filters["Singapore"]],
    [1,"Southeast.Asia","https://cdn.jsdelivr.net/gh/sixvable/proxy-rule-icons-png@main/icons/region-asean.png",list("SEA-Auto,SEA-FallBack,DIRECT"),filters["Southeast.Asia"]],
    [1,"America",icon("United_States"),list("US-Auto,US-FallBack,DIRECT"),filters["America"]],
    [1,"Canada",icon("Canada"),list("CA-Auto,CA-FallBack,DIRECT"),filters["Canada"]],
    [1,"UnitedKingdom",icon("United_Kingdom"),list("UK-Auto,UK-FallBack,DIRECT"),filters["UnitedKingdom"]],
    [1,"Australia",icon("Australia"),list("AU-Auto,AU-FallBack,DIRECT"),filters["Australia"]],
    [1,"Germany",icon("Germany"),list("DE-Auto,DE-FallBack,DIRECT"),filters["Germany"]],
    [1,"Netherlands","https://flagcdn.com/w80/nl.png",list("NL-Auto,NL-FallBack,DIRECT"),filters["Netherlands"]],
    [1,"France",icon("France"),list("FR-Auto,FR-FallBack,DIRECT"),filters["France"]],
    [1,"Korea",icon("Korea"),list("KR-Auto,KR-FallBack,DIRECT"),filters["Korea"]],
    [1,"Europe",icon("Europe_Map"),list("EU-Auto,EU-FallBack,DIRECT"),filters["Europe"]],
    [1,"Oceania",icon("Oceania_Map"),list("OC-Auto,OC-FallBack,DIRECT"),filters["Oceania"]],
    [1,"West.Asia",icon("Asia_Map"),list("WA-Auto,WA-FallBack,DIRECT"),filters["West.Asia"]],
    [1,"Africa",icon("Africa_Map"),list("AF-Auto,AF-FallBack,DIRECT"),filters["Africa"]],
    [1,"South.America",icon("LA_Map"),list("SAM-Auto,SAM-FallBack,DIRECT"),filters["South.America"]],
    [1,"AllServer",icon("Airport"),list("All-Auto,All-FallBack,DIRECT"),filters["AllServer"]],
    [2,"HK-Auto",filters["HongKong"]],
    [2,"TW-Auto",filters["TaiWan"]],
    [2,"JP-Auto",filters["Japan"]],
    [2,"SG-Auto",filters["Singapore"]],
    [2,"SEA-Auto",filters["Southeast.Asia"]],
    [2,"US-Auto",filters["America"]],
    [2,"CA-Auto",filters["Canada"]],
    [2,"UK-Auto",filters["UnitedKingdom"]],
    [2,"AU-Auto",filters["Australia"]],
    [2,"DE-Auto",filters["Germany"]],
    [2,"NL-Auto",filters["Netherlands"]],
    [2,"FR-Auto",filters["France"]],
    [2,"KR-Auto",filters["Korea"]],
    [2,"EU-Auto",filters["Europe"]],
    [2,"OC-Auto",filters["Oceania"]],
    [2,"WA-Auto",filters["West.Asia"]],
    [2,"AF-Auto",filters["Africa"]],
    [2,"SAM-Auto",filters["South.America"]],
    [2,"All-Auto",filters["AllServer"]],
    [3,"HK-FallBack",filters["HongKong"]],
    [3,"TW-FallBack",filters["TaiWan"]],
    [3,"JP-FallBack",filters["Japan"]],
    [3,"SG-FallBack",filters["Singapore"]],
    [3,"SEA-FallBack",filters["Southeast.Asia"]],
    [3,"US-FallBack",filters["America"]],
    [3,"CA-FallBack",filters["Canada"]],
    [3,"UK-FallBack",filters["UnitedKingdom"]],
    [3,"AU-FallBack",filters["Australia"]],
    [3,"DE-FallBack",filters["Germany"]],
    [3,"NL-FallBack",filters["Netherlands"]],
    [3,"FR-FallBack",filters["France"]],
    [3,"KR-FallBack",filters["Korea"]],
    [3,"EU-FallBack",filters["Europe"]],
    [3,"OC-FallBack",filters["Oceania"]],
    [3,"WA-FallBack",filters["West.Asia"]],
    [3,"AF-FallBack",filters["Africa"]],
    [3,"SAM-FallBack",filters["South.America"]],
    [3,"All-FallBack",filters["AllServer"]],
    [4,"Video-AppleTV",icon("Apple_TV"),menu("DIRECT,America")],
    [5,"Apple TV 双语字幕",icon("Apple_TV"),list("DIRECT")],
    [0,"Network-LAN",icon("WiFi"),menu("DIRECT,REJECT,REJECT-DROP,Proxy,Final,HongKong,TaiWan,Japan,Singapore,Southeast.Asia,America,Canada")],
    [0,"Protection-HTTPDNS",icon("Hijacking"),menu("REJECT-DROP,REJECT,DIRECT,America,Japan,UnitedKingdom,Australia")],
    [0,"Protection-Hijacking",icon("Hijacking"),menu("REJECT-DROP,REJECT,DIRECT,Proxy,Final,HongKong,TaiWan,Japan,Singapore,Southeast.Asia,America,Canada")],
    [0,"DNS-China",icon("China"),menu("DIRECT,REJECT-DROP,REJECT,Proxy,Final,HongKong,TaiWan,Japan,Singapore,Southeast.Asia,America,Canada")],
    [6,"DNS-Global",icon("World_Map"),list("HongKong,America,Japan,Singapore,DIRECT"),filters["DNS-Global"]],
    [0,"NTP-Global",icon("World_Map"),menu("DIRECT,America,Japan,UnitedKingdom,Australia")],
    [0,"NTP-China",icon("China"),menu("DIRECT,REJECT-DROP,REJECT,Proxy,Final,HongKong,TaiWan,Japan,Singapore,Southeast.Asia,America,Canada")],
    [0,"Country-China",icon("China"),menu("DIRECT,REJECT,REJECT-DROP,Proxy,Final,HongKong,TaiWan,Japan,Singapore,Southeast.Asia,America,Canada")],
    [0,"Speedtest",icon("Speedtest"),menu("DIRECT,America,Japan,UnitedKingdom,Australia,Proxy,REJECT-DROP")],
    [0,"NAS-Synology","https://cdn.jsdelivr.net/gh/sixvable/proxy-rule-icons-png@main/icons/app-synology.png",menu("DIRECT")],
    [0,"Home-Aqara","https://is1-ssl.mzstatic.com/image/thumb/Purple211/v4/41/94/7e/41947edf-870c-ac6a-218a-6d72b8886715/AppIcon-0-0-1x_U007emarketing-0-8-0-sRGB-85-220.png/512x512bb.jpg",menu("DIRECT")],
    [0,"Drive-OneDrive",icon("OneDrive"),menu("DIRECT")],
    [0,"Drive-Dropbox","https://cdn.jsdelivr.net/gh/sixvable/proxy-rule-icons-png@main/icons/drive-dropbox.png",menu()],
    [0,"Drive-MEGA","https://cdn.jsdelivr.net/gh/sixvable/proxy-rule-icons-png@main/icons/drive-mega.png",menu()],
    [0,"Drive-Imgur","https://cdn.jsdelivr.net/gh/sixvable/proxy-rule-icons-png@main/icons/drive-imgur.png",menu()],
    [0,"Drive-InternetArchive","https://cdn.jsdelivr.net/gh/sixvable/proxy-rule-icons-png@main/icons/drive-internet-archive.png",menu()],
    [0,"Finance-PayPal",icon("PayPal"),menu("Proxy,America,UnitedKingdom,Australia,DIRECT,REJECT,REJECT-DROP,Final,HongKong,TaiWan")],
    [0,"Finance-Wise","https://is1-ssl.mzstatic.com/image/thumb/Purple211/v4/b9/0c/1d/b90c1d16-7473-6596-8bf6-609cc4af01c4/AppIcon-0-0-1x_U007epad-0-1-0-sRGB-85-220.png/512x512bb.jpg",menu("Proxy,America,UnitedKingdom,DIRECT,REJECT,REJECT-DROP,Final,HongKong,TaiWan,Japan,Singapore,Southeast.Asia,Canada")],
    [0,"Crypto-Binance","https://is1-ssl.mzstatic.com/image/thumb/Purple221/v4/ae/3b/3f/ae3b3f2e-d4db-4a89-fbe8-2a6fd2d8e2c6/AppIcon-0-0-1x_U007emarketing-0-8-0-85-220.png/512x512bb.jpg",menu("Proxy,Japan,America,DIRECT,REJECT,REJECT-DROP,Final,HongKong,TaiWan,Singapore,Southeast.Asia,Canada")],
    [0,"Crypto-OKX","https://is1-ssl.mzstatic.com/image/thumb/Purple221/v4/03/aa/a0/03aaa030-4c0d-b75c-d9a3-49f4125b8331/AppIcon-0-0-1x_U007emarketing-0-8-0-85-220.png/512x512bb.jpg",menu("Proxy,Japan,America,DIRECT,REJECT,REJECT-DROP,Final,HongKong,TaiWan,Singapore,Southeast.Asia,Canada")],
    [0,"Finance-Monzo","https://is1-ssl.mzstatic.com/image/thumb/Purple211/v4/53/e9/17/53e9176c-a48d-f03e-0bc9-097f225a28d4/AppIconProd-0-0-1x_U007ephone-0-1-0-0-sRGB-85-220.png/512x512bb.jpg",menu("Proxy,America,UnitedKingdom,DIRECT,REJECT,REJECT-DROP,Final,HongKong,TaiWan,Japan,Singapore,Southeast.Asia,Canada")],
    [0,"Finance-Revolut","https://is1-ssl.mzstatic.com/image/thumb/Purple211/v4/db/e3/5a/dbe35a64-c880-15fe-46ce-81f70e920e8d/AppIcon-Production-0-0-1x_U007epad-0-1-85-220.png/512x512bb.jpg",menu("Proxy,America,UnitedKingdom,DIRECT,REJECT,REJECT-DROP,Final,HongKong,TaiWan,Japan,Singapore,Southeast.Asia,Canada")],
    [0,"Shopping-eBay","https://cdn.jsdelivr.net/gh/sixvable/proxy-rule-icons-png@main/icons/shopping-ebay.png",menu()],
    [0,"Shopping-Patreon","https://is1-ssl.mzstatic.com/image/thumb/Purple221/v4/bd/40/c6/bd40c6aa-793c-ca87-14fb-34313e30f01a/AppIcon-0-0-1x_U007epad-0-1-0-85-220.png/512x512bb.jpg",menu()],
    [0,"Game-Xbox",icon("Xbox"),menu("DIRECT")],
    [0,"Game-PlayStation",icon("PlayStation"),menu("DIRECT")],
    [0,"Game-Nintendo",icon("Nintendo"),menu("DIRECT")],
    [0,"Game-Steam",icon("Steam"),menu("Proxy,DIRECT")],
    [0,"Game-Epic",icon("Epic_Games"),menu("Proxy,DIRECT")],
    [0,"Game-GOG","https://img.icons8.com/fluency/512/gog-galaxy.png",menu("Proxy,DIRECT")],
    [0,"Game-Rockstar","https://img.icons8.com/nolan/512/rockstar-games.png",menu("Proxy,DIRECT")],
    [0,"Game-EA-Origin","https://cdn.jsdelivr.net/gh/sixvable/proxy-rule-icons-png@main/icons/game-ea.png",menu("Proxy,DIRECT")],
    [0,"Game-Ubisoft","https://img.icons8.com/doodle/512/ubisoft-connect.png",menu("Proxy,DIRECT")],
    [0,"Video-Netflix",icon("Netflix"),menu()],
    [0,"Video-DisneyPlus",icon("Disney+"),menu()],
    [0,"Video-PrimeVideo",icon("Prime_Video"),menu()],
    [0,"Video-HBO",icon("HBO"),menu()],
    [0,"Video-FOX",icon("FOX"),menu()],
    [0,"Video-Adult",icon("Pornhub"),menu()],
    [0,"Live-Twitch",icon("Twitch"),menu("Proxy,America,Japan,UnitedKingdom,Australia,DIRECT,REJECT,REJECT-DROP,TaiWan")],
    [0,"Audio-Spotify",icon("Spotify"),menu()],
    [0,"Social-Facebook",icon("Facebook"),menu()],
    [0,"Social-Reddit","https://cdn.jsdelivr.net/gh/sixvable/proxy-rule-icons-png@main/icons/social-reddit.png",menu()],
    [0,"Social-Telegram",icon("Telegram"),menu()],
    [0,"Social-WhatsApp","https://cdn.jsdelivr.net/gh/sixvable/proxy-rule-icons-png@main/icons/social-whatsapp.png",menu()],
    [0,"Social-LINE",icon("Line"),menu()],
    [0,"Social-Discord",icon("Discord"),menu()],
    [0,"Social-LinkedIn",icon("Linkedin"),menu()],
    [0,"Social-Clubhouse",icon("Clubhouse"),menu()],
    [0,"Social-Signal","https://cdn.jsdelivr.net/gh/sixvable/proxy-rule-icons-png@main/icons/social-signal.png",menu()],
    [0,"News-Wikipedia","https://cdn.jsdelivr.net/gh/sixvable/proxy-rule-icons-png@main/icons/news-wikipedia.png",menu()],
    [0,"AI-AppleAI",icon("Apple_2"),menu("DIRECT,Proxy,America,UnitedKingdom")],
    [0,"AI-OpenAI","https://is1-ssl.mzstatic.com/image/thumb/Purple221/v4/cf/c8/33/cfc83360-f210-5c47-cee1-ef9458924dfa/AppIcon-0-0-1x_U007epad-0-0-0-1-0-P3-85-220.png/512x512bb.jpg",menu("TaiWan,Proxy,America,UnitedKingdom")],
    [0,"AI-Grok","https://is1-ssl.mzstatic.com/image/thumb/Purple221/v4/8b/4f/c6/8b4fc632-ad34-0bf5-6003-0fa5a4723145/AppIcon-0-0-1x_U007epad-0-0-0-1-0-0-P3-0-85-220.png/512x512bb.jpg",menu("TaiWan,Proxy,America,UnitedKingdom")],
    [0,"Social-Twitter",icon("X"),menu("Proxy,America,Japan,UnitedKingdom,Australia,DIRECT,REJECT,REJECT-DROP,TaiWan")],
    [0,"AI-Claude","https://is1-ssl.mzstatic.com/image/thumb/Purple221/v4/bd/6d/22/bd6d2240-8ddf-6cd4-f55a-fc74122c96a4/AppIcon-0-0-1x_U007epad-0-1-85-220.png/512x512bb.jpg",menu("TaiWan,Proxy,America,UnitedKingdom")],
    [0,"AI-Gemini","https://cdn.jsdelivr.net/gh/sixvable/proxy-rule-icons-png@main/icons/ai-gemini.png",menu("TaiWan,Proxy,America,UnitedKingdom")],
    [0,"AI-Copilot",icon("Copilot"),menu("TaiWan,Proxy,America,UnitedKingdom")],
    [0,"AI-GlobalAI",icon("AI"),menu("TaiWan,Proxy,America,UnitedKingdom")],
    [0,"Tool-Adobe","https://cdn.jsdelivr.net/gh/sixvable/proxy-rule-icons-png@main/icons/tool-adobe.png",menu("DIRECT,Proxy,America,UnitedKingdom")],
    [0,"Tool-GitHub",icon("GitHub"),menu("DIRECT,Proxy,America,UnitedKingdom")],
    [0,"Tool-BingEdge","https://cdn.jsdelivr.net/gh/shindgewongxj/WHATSINStash@master/icon/bing.png",menu("DIRECT,America,Proxy,UnitedKingdom")],
    [0,"Tool-Notion",icon("Notion"),menu("DIRECT,Proxy,America,UnitedKingdom")],
    [0,"Tool-Pinterest","https://cdn.jsdelivr.net/gh/sixvable/proxy-rule-icons-png@main/icons/tool-pinterest.png",menu("Proxy,America,UnitedKingdom")],
    [0,"Drive-GoogleDrive",icon("Google_Drive"),menu()],
    [0,"Video-YouTube",icon("YouTube"),menu()],
    [0,"Audio-YouTubeMusic",icon("YouTube_Music"),menu()],
    [0,"Apps-Google",icon("Google"),menu("Proxy,America,UnitedKingdom")],
    [0,"Apps-Amazon",icon("Amazon"),menu()],
    [0,"Apps-Apple",icon("Apple"),menu("DIRECT,America,Proxy,UnitedKingdom")],
    [0,"Apps-Microsoft",icon("Microsoft"),menu("DIRECT,America,Proxy,UnitedKingdom")],
  ];
  var groups = groupRows.map(function (row, index) {
    var g = JSON.parse(JSON.stringify(groupTemplates[row[0]]));
    var i = 1;
    ["name","icon","proxies","filter"].forEach(function (key) {
      if (Object.prototype.hasOwnProperty.call(g, key)) g[key] = row[i++];
    });
    if (row[0] === 0 && index > 1) return {name:g.name, icon:g.icon, type:g.type, proxies:g.proxies};
    return g;
  });
  var ruleProviders = {};
  var ruleBases = ["https://cdn.jsdelivr.net/gh/Accademia/Additional_Rule_For_Clash@latest/","https://cdn.jsdelivr.net/gh/blackmatrix7/ios_rule_script@latest/rule/Clash/"];
  var yamlRules = [
    ["GlobalDNS_Domain","d",0,"GlobalDNS/GlobalDNS_Domain"],
    ["GlobalDNS_IP","i",0,"GlobalDNS/GlobalDNS_IP"],
    ["ChinaDNS_Domain","d",0,"ChinaDNS/ChinaDNS_Domain"],
    ["ChinaDNS_IP","i",0,"ChinaDNS/ChinaDNS_IP"],
    ["Lan_Do_Resolve","c",1,"Lan/Lan"],
    ["BlockHttpDNS_Do_Resolve","c",1,"BlockHttpDNS/BlockHttpDNS"],
    ["Hijacking_Do_Resolve","c",1,"Hijacking/Hijacking"],
    ["HijackingPlus_Do_Resolve","c",0,"HijackingPlus/HijackingPlus"],
    ["PreRepairEasyPrivacy_REJECT_Do_Resolve","c",0,"PreRepairEasyPrivacy/PreRepairEasyPrivacy_REJECT"],
    ["GeositeCN_Domain","d",0,"GeositeCN/GeositeCN_Domain"],
    ["Speedtest_Do_Resolve","c",1,"Speedtest/Speedtest"],
    ["Synology_Do_Resolve","c",1,"Synology/Synology"],
    ["AqaraGlobal_Do_Resolve","c",0,"Aqara/AqaraGlobal"],
    ["OneDrive_Do_Resolve","c",1,"OneDrive/OneDrive"],
    ["Dropbox_Do_Resolve","c",1,"Dropbox/Dropbox"],
    ["MEGA_Do_Resolve","c",1,"MEGA/MEGA"],
    ["GoogleDrive_Do_Resolve","c",1,"GoogleDrive/GoogleDrive"],
    ["WaybackMachine_Domain","d",0,"WaybackMachine/WaybackMachine_Domain"],
    ["WaybackMachine_IP","i",0,"WaybackMachine/WaybackMachine_IP"],
    ["Paypal_Do_Resolve","c",0,"VirtualFinance/Paypal"],
    ["Wise_Do_Resolve","c",0,"VirtualFinance/Wise"],
    ["Binance_Do_Resolve","c",1,"Binance/Binance"],
    ["Monzo_Do_Resolve","c",0,"VirtualFinance/Monzo"],
    ["Revolut_Do_Resolve","c",0,"VirtualFinance/Revolut"],
    ["eBay_Do_Resolve","c",1,"eBay/eBay"],
    ["Xbox_Do_Resolve","c",1,"Xbox/Xbox"],
    ["Nintendo_Do_Resolve","c",1,"Nintendo/Nintendo"],
    ["Steam_Do_Resolve","c",1,"Steam/Steam"],
    ["EPIC_Do_Resolve","c",1,"Epic/Epic","EPIC"],
    ["GOG_Do_Resolve","c",1,"Gog/Gog","GOG"],
    ["RockStar_Do_Resolve","c",1,"Rockstar/Rockstar","RockStar"],
    ["EA_Do_Resolve","c",1,"EA/EA"],
    ["UBI_Do_Resolve","c",1,"UBI/UBI"],
    ["YouTube_Do_Resolve","c",1,"YouTube/YouTube"],
    ["Netflix_Do_Resolve","c",1,"Netflix/Netflix"],
    ["Disney_Do_Resolve","c",1,"Disney/Disney"],
    ["PrimeVideo_Do_Resolve","c",1,"PrimeVideo/PrimeVideo"],
    ["HBO_Do_Resolve","c",1,"HBO/HBO"],
    ["FOXPlus_Do_Resolve","c",1,"FOXPlus/FOXPlus"],
    ["FOXNOW_Do_Resolve","c",1,"FOXNOW/FOXNOW"],
    ["AppleTV_Do_Resolve","c",1,"AppleTV/AppleTV"],
    ["Pornhub_Domain","d",0,"Pornhub/Pornhub_Domain"],
    ["Twitch_Do_Resolve","c",1,"Twitch/Twitch"],
    ["Spotify_Do_Resolve","c",1,"Spotify/Spotify"],
    ["Twitter_Do_Resolve","c",1,"Twitter/Twitter"],
    ["Facebook_Do_Resolve","c",1,"Facebook/Facebook"],
    ["Telegram_Do_Resolve","c",1,"Telegram/Telegram"],
    ["Whatsapp_Do_Resolve","c",1,"Whatsapp/Whatsapp"],
    ["Line_Do_Resolve","c",1,"Line/Line"],
    ["Reddit_Do_Resolve","c",1,"Reddit/Reddit"],
    ["Discord_Do_Resolve","c",1,"Discord/Discord"],
    ["Clubhouse_Do_Resolve","c",1,"Clubhouse/Clubhouse"],
    ["ClubhouseIP_Do_Resolve","c",1,"ClubhouseIP/ClubhouseIP"],
    ["Signal_Domain","d",0,"Signal/Signal_Domain"],
    ["Wikipedia_Do_Resolve","c",1,"Wikipedia/Wikipedia"],
    ["AppleAI_Domain","d",0,"AppleAI/AppleAI_Domain"],
    ["OpenAI_Do_Resolve","c",1,"OpenAI/OpenAI"],
    ["Grok_Domain","d",0,"Grok/Grok_Domain","Grok_Domian"],
    ["Gemini_Domain","d",0,"Gemini/Gemini_Domain","Gemini_Domian"],
    ["Claude_Do_Resolve","c",1,"Claude/Claude"],
    ["Copilot_Domain","d",0,"Copilot/Copilot_Domain","Copilot_Domian"],
    ["Adobe_Do_Resolve","c",1,"Adobe/Adobe"],
    ["GitHub_Do_Resolve","c",1,"GitHub/GitHub"],
    ["Notion_Do_Resolve","c",1,"Notion/Notion"],
    ["MicrosoftEdge_Do_Resolve","c",1,"MicrosoftEdge/MicrosoftEdge"],
    ["Google_Do_Resolve","c",1,"Google/Google"],
    ["Amazon_Do_Resolve","c",1,"Amazon/Amazon"],
    ["MicrosoftAPPs_Domain","d",0,"MicrosoftAPPs/MicrosoftAPPs_Domain","MicrosoftAPPs"],
    ["Apple_Domain","d",0,"Apple/Apple_Domain"],
    ["Apple_IP","i",0,"Apple/Apple_IP"],
  ];
  yamlRules.forEach(function (r) {
    var filename = r[4] || r[3].split("/").pop();
    ruleProviders[r[0]] = {
      type:"http", behavior:{d:"domain",c:"classical",i:"ipcidr"}[r[1]],
      format:"yaml", interval:86400, proxy:"Proxy",
      url:ruleBases[r[2]] + r[3] + ".yaml", path:"./ruleset/" + filename + ".yaml"
    };
  });
  list("category-httpdns-cn,apple-tvplus,cloudflare-cn,synology,dropbox,mega,imgur,paypal,wise,binance,okx,ebay,patreon,xbox,playstation,nintendo,steam,gog,rockstar,ea,origin,ubisoft,primevideo,hbo,fox,pornhub,twitch,spotify,facebook,reddit,telegram,whatsapp,line,discord,linkedin,clubhouse,signal,apple-intelligence,xai,twitter,anthropic,google-gemini,adobe,github,bing,notion,pinterest,youtube").forEach(function (tag) {
    ruleProviders["GeoSiteMRS-" + tag] = {
      type:"http", behavior:"domain", format:"mrs", interval:86400, proxy:"Proxy",
      url:"https://raw.githubusercontent.com/MetaCubeX/meta-rules-dat/meta/geo/geosite/" + tag + ".mrs",
      path:"./ruleset/geosite/" + tag + ".mrs"
    };
  });
  var desktopOverride = {
    "keep-alive-interval":60,
    "find-process-mode":"strict",
    "tcp-concurrent":true,
    "geodata-mode":false,
    "geo-auto-update":true,
    "geo-update-interval":24,
    "geox-url":{"geoip":"https://testingcf.jsdelivr.net/gh/MetaCubeX/meta-rules-dat@release/geoip.dat","geosite":"https://testingcf.jsdelivr.net/gh/MetaCubeX/meta-rules-dat@release/geosite.dat","mmdb":"https://testingcf.jsdelivr.net/gh/MetaCubeX/meta-rules-dat@release/country.mmdb","asn":"https://github.com/xishang0128/geoip/releases/download/latest/GeoLite2-ASN.mmdb"},
    "profile":{"store-selected":true},
    "sniffer":{"enable":true,"override-destination":false,"sniff":{"HTTP":{"ports":[80,"8080-8880"],"override-destination":true},"TLS":{"ports":[443,8443]},"QUIC":{"ports":[443,8443]}},"force-domain":["+.v2ex.com"],"skip-domain":["Mijia Cloud","dlg.io.mi.com","+.apple.com","+.icloud.com","+.wechat.com","+.qpic.cn","+.qq.com","+.wechatapp.com","+.vivox.com","+.oray.com","+.sunlogin.net"]},
    "ntp":{"enable":true,"write-to-system":false,"server":"time.apple.com","port":123},
    "hosts":{"+.clash.dev":"127.0.0.1","+.stash.dev":"127.0.0.1"},
    "dns":{"enable":true,"cache-algorithm":"arc","prefer-h3":false,"ipv6":true,"listen":"0.0.0.0:53","enhanced-mode":"redir-host","use-hosts":true,"use-system-hosts":true,"respect-rules":false,"default-nameserver":["https://223.5.5.5/dns-query#DIRECT","https://223.6.6.6/dns-query#DIRECT"],"direct-nameserver":["https://223.5.5.5/dns-query#DIRECT","https://223.6.6.6/dns-query#DIRECT"],"direct-nameserver-follow-policy":true,"nameserver":["https://dns.google/dns-query#DNS-Global","https://cloudflare-dns.com/dns-query#DNS-Global"],"fallback":[],"nameserver-policy":{"geosite:private":["system"],"rule-set:GeositeCN_Domain":["https://223.5.5.5/dns-query#DIRECT","https://223.6.6.6/dns-query#DIRECT"]}},
    "listeners":[{"name":"Apple TV 字幕直连出口","type":"mixed","listen":"127.0.0.1","port":18767,"proxy":"DIRECT"}],
    "proxy-providers":{"AppleTV 字幕桥接节点":{"type":"inline","payload":[{"name":"Apple TV 字幕桥接","type":"http","server":"127.0.0.1","port":18768,"udp":false}],"health-check":{"enable":false}}},
    "proxy-groups":groups,
    "rule-providers":ruleProviders,
    "rules":[
      "IP-CIDR         , 127.0.0.0/8                                  , DIRECT , no-resolve",
      "AND,((NETWORK,UDP),(DST-PORT,443),(DOMAIN,uts-api.itunes.apple.com)),REJECT",
      "AND,((NETWORK,UDP),(DST-PORT,443),(DOMAIN,hls-amt.itunes.apple.com)),REJECT",
      "DOMAIN          , uts-api.itunes.apple.com                     , Apple TV 双语字幕",
      "DOMAIN          , hls-amt.itunes.apple.com                     , Apple TV 双语字幕",
      "IP-CIDR         , 10.103.30.33/32                              , DIRECT , no-resolve",
      "GEOSITE         , private                                    , Network-LAN",
      "RULE-SET        , Lan_Do_Resolve                             , Network-LAN,no-resolve",
      "RULE-SET,GeoSiteMRS-category-httpdns-cn,Protection-HTTPDNS",
      "RULE-SET        , BlockHttpDNS_Do_Resolve                    , Protection-HTTPDNS,no-resolve",
      "RULE-SET        , Hijacking_Do_Resolve                       , Protection-Hijacking,no-resolve",
      "RULE-SET        , HijackingPlus_Do_Resolve                   , Protection-Hijacking,no-resolve",
      "RULE-SET        , PreRepairEasyPrivacy_REJECT_Do_Resolve     , REJECT-DROP",
      "RULE-SET,GeoSiteMRS-apple-tvplus,Video-AppleTV",
      "RULE-SET        , AppleTV_Do_Resolve                         , Video-AppleTV",
      "DOMAIN          , tv.g.apple.com                             , Video-AppleTV",
      "DOMAIN          , linear.tv.apple.com                        , Video-AppleTV",
      "DOMAIN          , ocvideo.apple.com                          , Video-AppleTV",
      "DOMAIN          , hls-svod.itunes.apple.com                  , Video-AppleTV",
      "DOMAIN-SUFFIX   , itunes.g.aaplimg.com                       , Video-AppleTV",
      "RULE-SET        , ChinaDNS_Domain                            , DNS-China",
      "RULE-SET        , GlobalDNS_Domain                           , DNS-Global",
      "RULE-SET        , ChinaDNS_IP                                , DNS-China,no-resolve",
      "RULE-SET        , GlobalDNS_IP                               , DNS-Global,no-resolve",
      "AND,((NETWORK,udp),(DST-PORT,123),(NOT,((GEOIP,CN))))        , NTP-Global",
      "AND,((NETWORK,udp),(DST-PORT,123),(GEOIP,CN))                , NTP-China",
      "RULE-SET        , GeositeCN_Domain                           , Country-China",
      "RULE-SET,GeoSiteMRS-cloudflare-cn,Country-China",
      "GEOSITE         , amazon@cn                                  , Country-China",
      "GEOSITE         , ookla-speedtest                            , Speedtest",
      "RULE-SET        , Speedtest_Do_Resolve                       , Speedtest",
      "DOMAIN-SUFFIX   , oca.nflxvideo.net                          , Speedtest",
      "RULE-SET,GeoSiteMRS-synology,NAS-Synology",
      "RULE-SET        , Synology_Do_Resolve                        , NAS-Synology",
      "RULE-SET        , AqaraGlobal_Do_Resolve                     , Home-Aqara",
      "GEOSITE         , onedrive                                   , Drive-OneDrive",
      "RULE-SET        , OneDrive_Do_Resolve                        , Drive-OneDrive",
      "DOMAIN-SUFFIX   , events.data.microsoft.com                  , Drive-OneDrive",
      "DOMAIN-SUFFIX   , ecs.office.com                             , Drive-OneDrive",
      "RULE-SET,GeoSiteMRS-dropbox,Drive-Dropbox",
      "RULE-SET        , Dropbox_Do_Resolve                         , Drive-Dropbox",
      "RULE-SET,GeoSiteMRS-mega,Drive-MEGA",
      "RULE-SET        , MEGA_Do_Resolve                            , Drive-MEGA",
      "RULE-SET,GeoSiteMRS-imgur,Drive-Imgur",
      "RULE-SET        , WaybackMachine_Domain                      , Drive-InternetArchive",
      "RULE-SET        , WaybackMachine_IP                          , Drive-InternetArchive",
      "RULE-SET,GeoSiteMRS-paypal,Finance-PayPal",
      "RULE-SET        , Paypal_Do_Resolve                          , Finance-PayPal",
      "RULE-SET,GeoSiteMRS-wise,Finance-Wise",
      "RULE-SET        , Wise_Do_Resolve                            , Finance-Wise",
      "RULE-SET,GeoSiteMRS-binance,Crypto-Binance",
      "RULE-SET        , Binance_Do_Resolve                         , Crypto-Binance",
      "RULE-SET,GeoSiteMRS-okx,Crypto-OKX",
      "RULE-SET        , Monzo_Do_Resolve                           , Finance-Monzo",
      "RULE-SET        , Revolut_Do_Resolve                         , Finance-Revolut",
      "RULE-SET,GeoSiteMRS-ebay,Shopping-eBay",
      "RULE-SET        , eBay_Do_Resolve                            , Shopping-eBay",
      "RULE-SET,GeoSiteMRS-patreon,Shopping-Patreon",
      "RULE-SET,GeoSiteMRS-xbox,Game-Xbox",
      "RULE-SET        , Xbox_Do_Resolve                            , Game-Xbox",
      "RULE-SET,GeoSiteMRS-playstation,Game-PlayStation",
      "RULE-SET,GeoSiteMRS-nintendo,Game-Nintendo",
      "RULE-SET        , Nintendo_Do_Resolve                        , Game-Nintendo",
      "RULE-SET,GeoSiteMRS-steam,Game-Steam",
      "RULE-SET        , Steam_Do_Resolve                           , Game-Steam",
      "DOMAIN-SUFFIX   , steamserver.net                            , Game-Steam",
      "GEOSITE         , epicgames                                  , Game-Epic",
      "RULE-SET        , EPIC_Do_Resolve                            , Game-Epic",
      "RULE-SET,GeoSiteMRS-gog,Game-GOG",
      "RULE-SET        , GOG_Do_Resolve                             , Game-GOG",
      "RULE-SET,GeoSiteMRS-rockstar,Game-Rockstar",
      "RULE-SET        , RockStar_Do_Resolve                        , Game-Rockstar",
      "RULE-SET,GeoSiteMRS-ea,Game-EA-Origin",
      "RULE-SET        , EA_Do_Resolve                              , Game-EA-Origin",
      "RULE-SET,GeoSiteMRS-origin,Game-EA-Origin",
      "RULE-SET,GeoSiteMRS-ubisoft,Game-Ubisoft",
      "RULE-SET        , UBI_Do_Resolve                             , Game-Ubisoft",
      "GEOSITE         , netflix                                    , Video-Netflix",
      "RULE-SET        , Netflix_Do_Resolve                         , Video-Netflix",
      "GEOSITE         , disney                                     , Video-DisneyPlus",
      "RULE-SET        , Disney_Do_Resolve                          , Video-DisneyPlus",
      "RULE-SET,GeoSiteMRS-primevideo,Video-PrimeVideo",
      "RULE-SET        , PrimeVideo_Do_Resolve                      , Video-PrimeVideo",
      "RULE-SET,GeoSiteMRS-hbo,Video-HBO",
      "RULE-SET        , HBO_Do_Resolve                             , Video-HBO",
      "RULE-SET,GeoSiteMRS-fox,Video-FOX",
      "RULE-SET        , FOXPlus_Do_Resolve                         , Video-FOX",
      "RULE-SET        , FOXNOW_Do_Resolve                          , Video-FOX",
      "RULE-SET,GeoSiteMRS-pornhub,Video-Adult",
      "RULE-SET        , Pornhub_Domain                             , Video-Adult",
      "RULE-SET,GeoSiteMRS-twitch,Live-Twitch",
      "RULE-SET        , Twitch_Do_Resolve                          , Live-Twitch",
      "RULE-SET,GeoSiteMRS-spotify,Audio-Spotify",
      "RULE-SET        , Spotify_Do_Resolve                         , Audio-Spotify",
      "RULE-SET,GeoSiteMRS-facebook,Social-Facebook",
      "RULE-SET        , Facebook_Do_Resolve                        , Social-Facebook",
      "RULE-SET,GeoSiteMRS-reddit,Social-Reddit",
      "RULE-SET        , Reddit_Do_Resolve                          , Social-Reddit",
      "RULE-SET,GeoSiteMRS-telegram,Social-Telegram",
      "RULE-SET        , Telegram_Do_Resolve                        , Social-Telegram",
      "RULE-SET,GeoSiteMRS-whatsapp,Social-WhatsApp",
      "RULE-SET        , Whatsapp_Do_Resolve                        , Social-WhatsApp",
      "RULE-SET,GeoSiteMRS-line,Social-LINE",
      "RULE-SET        , Line_Do_Resolve                            , Social-LINE",
      "RULE-SET,GeoSiteMRS-discord,Social-Discord",
      "RULE-SET        , Discord_Do_Resolve                         , Social-Discord",
      "RULE-SET,GeoSiteMRS-linkedin,Social-LinkedIn",
      "RULE-SET,GeoSiteMRS-clubhouse,Social-Clubhouse",
      "RULE-SET        , Clubhouse_Do_Resolve                       , Social-Clubhouse",
      "RULE-SET        , ClubhouseIP_Do_Resolve                     , Social-Clubhouse",
      "RULE-SET,GeoSiteMRS-signal,Social-Signal",
      "RULE-SET        , Signal_Domain                              , Social-Signal",
      "RULE-SET        , Wikipedia_Do_Resolve                       , News-Wikipedia",
      "RULE-SET,GeoSiteMRS-apple-intelligence,AI-AppleAI",
      "RULE-SET        , AppleAI_Domain                             , AI-AppleAI",
      "GEOSITE         , openai                                     , AI-OpenAI",
      "RULE-SET        , OpenAI_Do_Resolve                          , AI-OpenAI",
      "RULE-SET,GeoSiteMRS-xai,AI-Grok",
      "RULE-SET        , Grok_Domain                                , AI-Grok",
      "RULE-SET,GeoSiteMRS-twitter,Social-Twitter",
      "RULE-SET        , Twitter_Do_Resolve                         , Social-Twitter",
      "RULE-SET,GeoSiteMRS-anthropic,AI-Claude",
      "RULE-SET        , Claude_Do_Resolve                          , AI-Claude",
      "RULE-SET,GeoSiteMRS-google-gemini,AI-Gemini",
      "RULE-SET        , Gemini_Domain                              , AI-Gemini",
      "RULE-SET        , Copilot_Domain                             , AI-Copilot",
      "GEOSITE         , category-ai-!cn                            , AI-GlobalAI",
      "RULE-SET,GeoSiteMRS-adobe,Tool-Adobe",
      "RULE-SET        , Adobe_Do_Resolve                           , Tool-Adobe",
      "RULE-SET,GeoSiteMRS-github,Tool-GitHub",
      "RULE-SET        , GitHub_Do_Resolve                          , Tool-GitHub",
      "RULE-SET,GeoSiteMRS-bing,Tool-BingEdge",
      "RULE-SET        , MicrosoftEdge_Do_Resolve                   , Tool-BingEdge",
      "RULE-SET,GeoSiteMRS-notion,Tool-Notion",
      "RULE-SET        , Notion_Do_Resolve                          , Tool-Notion",
      "RULE-SET,GeoSiteMRS-pinterest,Tool-Pinterest",
      "RULE-SET        , GoogleDrive_Do_Resolve                     , Drive-GoogleDrive",
      "DOMAIN,music.youtube.com,Audio-YouTubeMusic",
      "RULE-SET,GeoSiteMRS-youtube,Video-YouTube",
      "RULE-SET        , YouTube_Do_Resolve                         , Video-YouTube",
      "GEOSITE         , google                                     , Apps-Google",
      "RULE-SET        , Google_Do_Resolve                          , Apps-Google",
      "GEOSITE         , amazon                                     , Apps-Amazon",
      "RULE-SET        , Amazon_Do_Resolve                          , Apps-Amazon",
      "RULE-SET        , Apple_Domain                               , Apps-Apple",
      "RULE-SET        , Apple_IP                                   , Apps-Apple",
      "RULE-SET        , MicrosoftAPPs_Domain                       , Apps-Microsoft",
      "GEOIP,CN,Country-China",
      "MATCH                                                        , Final",
    ],
  };
  Object.keys(desktopOverride).forEach(function (key) {
    result[key] = desktopOverride[key];
  });

  function own(obj, key) {
    return Object.prototype.hasOwnProperty.call(obj, key);
  }
  function copy(value) {
    return JSON.parse(JSON.stringify(value));
  }
  function fail(message) {
    throw new Error('Clash-Desktop: ' + message);
  }
  var builtins = Object.create(null);
  ['DIRECT', 'REJECT', 'REJECT-DROP', 'PASS', 'PASS-RULE', 'COMPATIBLE', 'GLOBAL'].forEach(function (name) {
    builtins[name] = true;
  });
  var used = Object.create(null);
  Object.keys(builtins).forEach(function (name) { used[name] = true; });
  desktopOverride['proxy-groups'].forEach(function (g) { used[g.name] = true; });
  used['Apple TV 字幕桥接'] = true;
  var nodes = Array.isArray(source.proxies) ? source.proxies : [];
  var oldGroups = Object.create(null);
  (Array.isArray(source['proxy-groups']) ? source['proxy-groups'] : []).forEach(function (g) {
    if (!g || typeof g.name !== 'string') fail('机场策略组缺少有效名称');
    if (own(oldGroups, g.name)) fail('机场策略组名称重复：' + g.name);
    oldGroups[g.name] = g;
  });
  var nodeNames = Object.create(null);
  nodes.forEach(function (node) {
    if (!node || typeof node.name !== 'string') fail('机场节点缺少有效名称');
    if (own(nodeNames, node.name)) fail('机场节点名称重复：' + node.name);
    nodeNames[node.name] = node.name;
  });
  Object.keys(nodeNames).forEach(function (name) { used[name] = true; });
  Object.keys(oldGroups).forEach(function (name) { used[name] = true; });
  function unique(prefix, name) {
    var candidate = prefix + name;
    var suffix = 2;
    while (own(used, candidate)) candidate = prefix + name + ' #' + suffix++;
    used[candidate] = true;
    return candidate;
  }
  var desktopNames = Object.create(null);
  desktopOverride['proxy-groups'].forEach(function (g) { desktopNames[g.name] = true; });
  nodes.forEach(function (node) {
    var name = node.name;
    if (own(desktopNames, name) || own(builtins, name) || name === 'Apple TV 字幕桥接') {
      nodeNames[name] = unique('Airport-Node::', name);
      node.name = nodeNames[name];
    }
  });

  var originalProviders = source['proxy-providers'] || {};
  var providers = Object.create(null);
  var providerNames = Object.create(null);
  Object.keys(originalProviders).forEach(function (name) { used[name] = true; });
  Object.keys(desktopOverride['proxy-providers']).forEach(function (name) {
    used[name] = true;
    providers[name] = desktopOverride['proxy-providers'][name];
  });
  Object.keys(originalProviders).forEach(function (name) {
    var mapped = own(providers, name) ? unique('Airport-Provider::', name) : name;
    providerNames[name] = mapped;
    providers[mapped] = originalProviders[name];
  });

  var groupNames = Object.create(null);
  var visiting = Object.create(null);
  var retained = [];
  function resolveReference(name, context) {
    if (typeof name !== 'string' || !name) fail(context + ' 缺少有效的代理名称');
    if (own(oldGroups, name)) return retainGroup(name);
    if (own(nodeNames, name)) return nodeNames[name];
    if (own(builtins, name) || own(desktopNames, name)) return name;
    fail(context + ' 引用了不存在的代理或策略组：' + name);
  }
  function retainGroup(name) {
    if (visiting[name]) fail('机场策略组依赖形成循环：' + name);
    if (own(groupNames, name)) return groupNames[name];
    visiting[name] = true;
    var group = copy(oldGroups[name]);
    group.name = unique('Airport-Dependency::', name);
    groupNames[name] = group.name;
    group.hidden = true;
    if (Array.isArray(group.proxies)) {
      group.proxies = group.proxies.map(function (target) {
        return resolveReference(target, '机场依赖组 ' + name);
      });
    }
    if (Array.isArray(group.use)) {
      group.use = group.use.map(function (provider) {
        if (!own(providerNames, provider)) fail('机场依赖组 ' + name + ' 引用了不存在的 provider：' + provider);
        return providerNames[provider];
      });
    }
    if (group['default-selected']) {
      var selected = group['default-selected'];
      if (own(oldGroups, selected) || own(nodeNames, selected)) {
        group['default-selected'] = resolveReference(selected, '机场依赖组的默认选择');
      }
    }
    if (group['empty-fallback'] && own(nodeNames, group['empty-fallback'])) {
      group['empty-fallback'] = nodeNames[group['empty-fallback']];
    }
    if (group['include-all'] || group['include-all-proxies'] || group['include-all-providers']) {
      var exclude = group['exclude-filter'];
      group['exclude-filter'] = (exclude ? '(?:' + exclude + ')|' : '') + '^(Apple TV 字幕桥接)$';
    }
    visiting[name] = false;
    retained.push(group);
    return group.name;
  }
  function rewriteNode(node, context) {
    if (node && node['dialer-proxy']) {
      node['dialer-proxy'] = resolveReference(node['dialer-proxy'], context + ' dialer-proxy');
    }
  }
  nodes.forEach(function (node) { rewriteNode(node, '机场节点 ' + node.name); });
  Object.keys(originalProviders).forEach(function (name) {
    var provider = providers[providerNames[name]];
    if (!provider || typeof provider !== 'object') fail('无效的机场 provider：' + name);
    if (provider.proxy) provider.proxy = resolveReference(provider.proxy, '机场 provider ' + name);
    if (provider.override) rewriteNode(provider.override, '机场 provider ' + name + ' override');
    if (Array.isArray(provider.payload)) {
      provider.payload.forEach(function (node) { rewriteNode(node, '机场 provider ' + name + ' 节点'); });
    }
  });
  result.proxies = nodes;
  result['proxy-providers'] = providers;

  // Preserve node DNS, including transport-policy dependencies when supplied.
  function rewriteDns(value) {
    if (Array.isArray(value)) return value.map(rewriteDns);
    if (typeof value !== 'string') return value;
    var hash = value.indexOf('#');
    if (hash < 0) return value;
    var tail = value.slice(hash + 1);
    var amp = tail.indexOf('&');
    var transport = amp < 0 ? tail : tail.slice(0, amp);
    if (!own(oldGroups, transport) && !own(nodeNames, transport)) return value;
    return value.slice(0, hash + 1) + resolveReference(transport, '机场节点 DNS') + (amp < 0 ? '' : tail.slice(amp));
  }
  // Node DNS policies may depend on airport rule providers, not only proxy groups.
  var airportRuleProviders = source['rule-providers'] || {};
  var dnsRuleNames = Object.create(null);
  var rulePaths = Object.create(null);
  function cachePath(path) {
    return typeof path === 'string' ? path.replace(/\\/g, '/').replace(/^\.\//, '') : '';
  }
  Object.keys(result['rule-providers']).forEach(function (name) {
    used[name] = true;
    var path = cachePath(result['rule-providers'][name].path);
    if (path) rulePaths[path] = true;
  });
  Object.keys(airportRuleProviders).forEach(function (name) { used[name] = true; });
  function retainDnsRule(name) {
    if (own(dnsRuleNames, name)) return dnsRuleNames[name];
    if (!name || !own(airportRuleProviders, name)) fail('机场节点 DNS policy 引用了不存在的规则集：' + name);
    var provider = copy(airportRuleProviders[name]);
    if (!provider || typeof provider !== 'object' || Array.isArray(provider)) fail('无效的机场节点 DNS 规则集：' + name);
    // DNS policy keys use ':' as a separator, so generated rule-set names must not.
    var mapped = own(result['rule-providers'], name) ? unique('Airport-DNS-RuleSet-', name) : name;
    dnsRuleNames[name] = mapped;
    if (provider.proxy) provider.proxy = resolveReference(provider.proxy, '机场节点 DNS 规则集 ' + name);
    var path = cachePath(provider.path);
    if (path && own(rulePaths, path)) {
      if (provider.type !== 'http') fail('机场节点 DNS 规则集缓存路径冲突：' + provider.path);
      var stem = './ruleset/airport-node-dns/' + encodeURIComponent(mapped);
      var suffix = provider.format === 'mrs' ? '.mrs' : provider.format === 'text' ? '.txt' : '.yaml';
      provider.path = stem + suffix;
      var sequence = 2;
      while (own(rulePaths, cachePath(provider.path))) provider.path = stem + '-' + sequence++ + suffix;
      path = cachePath(provider.path);
    }
    if (path) rulePaths[path] = true;
    Object.defineProperty(result['rule-providers'], mapped, {value:provider, enumerable:true, writable:true, configurable:true});
    return mapped;
  }
  function rewriteNodeDnsPolicyKey(key) {
    if (key.indexOf('rule-set:') !== 0) return key;
    return 'rule-set:' + key.slice(9).split(',').map(function (name) {
      return retainDnsRule(name.trim());
    }).join(',');
  }
  // Keep the airport's resolvers when present. This is a configuration default,
  // not an append list or a runtime DNS failure fallback.
  function normalizeNodeDns(value) {
    if (value === undefined || value === null) return [];
    if (typeof value === 'string') value = [value];
    if (!Array.isArray(value)) fail('dns.proxy-server-nameserver 必须为字符串或字符串数组');
    var servers = [];
    value.forEach(function (server) {
      if (server === undefined || server === null) return;
      if (typeof server !== 'string') fail('dns.proxy-server-nameserver 中的非空条目必须为字符串');
      server = server.trim();
      if (server) servers.push(server);
    });
    return servers;
  }
  var nodeDns = normalizeNodeDns(airportDns['proxy-server-nameserver']);
  if (nodeDns.length > 0) {
    result.dns['proxy-server-nameserver'] = rewriteDns(nodeDns);
  } else {
    result.dns['proxy-server-nameserver'] = [
      'https://223.5.5.5/dns-query#DIRECT',
      'https://223.6.6.6/dns-query#DIRECT'
    ];
  }
  var nodeDnsPolicy = airportDns['proxy-server-nameserver-policy'];
  if (nodeDnsPolicy && typeof nodeDnsPolicy === 'object' && !Array.isArray(nodeDnsPolicy)) {
    var policies = Object.create(null);
    Object.keys(nodeDnsPolicy).forEach(function (name) {
      policies[rewriteNodeDnsPolicyKey(name)] = rewriteDns(nodeDnsPolicy[name]);
    });
    result.dns['proxy-server-nameserver-policy'] = policies;
  }
  result['proxy-groups'] = result['proxy-groups'].concat(retained);
  return result;
}

// END — 完整脚本结束