#!/usr/bin/env python3
import argparse,ipaddress,json,re,subprocess,tempfile,unittest
from pathlib import Path
from build import Compiler,minimized_domains,minimized_networks,graph_check,yaml_load,yaml_dump,provider_variant

class OptimizerTests(unittest.TestCase):
 def test_exact_domain_does_not_remove_subdomain(self):
  self.assertEqual(minimized_domains(['example.com','api.example.com']),['api.example.com','example.com'])
 def test_suffix_covers_apex_and_descendants(self):
  self.assertEqual(minimized_domains(['+.example.com','example.com','api.example.com','+.nested.example.com','unrelated.example']),['+.example.com','unrelated.example'])
 def test_network_collapse_preserves_families_and_holes(self):
  result=minimized_networks(['192.0.2.0/25','192.0.2.128/25','2001:db8::/127','2001:db8::2/127','198.51.100.0/25'])
  self.assertEqual(set(result),{'192.0.2.0/24','2001:db8::/126','198.51.100.0/25'})
  self.assertFalse(any(ipaddress.ip_address('198.51.100.200') in ipaddress.ip_network(x) for x in result if ':' not in x))
 def test_cycle_rejected(self):
  with self.assertRaises(AssertionError):graph_check([{'name':'A','proxies':['B']},{'name':'B','proxies':['A']}])

 def test_embedded_reject_action_is_not_emitted_twice(self):
  name='PreRepairEasyPrivacy_REJECT_Do_Resolve'
  recipe={'providers':{name:{'behavior':'classical'}}}
  sources={name:{'payload':['DOMAIN-KEYWORD,app-analytics,REJECT-DROP','DOMAIN-SUFFIX,example.invalid,REJECT-DROP']}}
  compiler=Compiler(recipe,sources,Path('.'),'unused')
  self.assertEqual(compiler.expand('RULE-SET,'+name,[]),[('DOMAIN-KEYWORD,app-analytics',()),('DOMAIN-SUFFIX,example.invalid',())])
 def test_region_filter_matches_real_names_and_excludes_metadata(self):
  recipe=json.loads(Path(__file__).with_name('recipe.json').read_text())
  groups={g['name']:g for g in recipe['groups']}
  for name,samples in {'HongKong':['🇭🇰 香港1 | [x1] HK','Hong Kong 01'],'America':['🇺🇸 美国01','US LAX 01'],'TaiWan':['Taiwan 01','🇹🇼 台湾1']}.items():
   regex=re.compile(groups[name]['filter'])
   for sample in samples:self.assertIsNotNone(regex.search(sample),sample)
   self.assertIsNone(regex.search('官网 '+samples[0]))
 def test_latest_rule_priorities_and_removed_groups(self):
  recipe=json.loads(Path(__file__).with_name('recipe.json').read_text())
  rules=recipe['rules'];names=[g['name'] for g in recipe['groups']]
  self.assertEqual(len(names),112);self.assertEqual(len(rules),168)
  self.assertLess(names.index('All-FallBack'),names.index('Video-AppleTV'))
  self.assertLess(names.index('Video-AppleTV'),names.index('Network-LAN'))
  self.assertLess(rules.index('GEOSITE,private,Network-LAN'),rules.index('GEOSITE,apple-tvplus,Video-AppleTV'))
  self.assertLess(rules.index('RULE-SET,ChinaDNS_Domain,DNS-China'),rules.index('RULE-SET,GlobalDNS_IP,DNS-Global,no-resolve'))
  self.assertFalse(set(names)&{'Global-CDN','DNS-Global-Auto','AppleTV-Media-IPv6','Apple TV 双语字幕'})
  self.assertFalse(any('DST-PORT,53' in r or 'DST-PORT,853' in r for r in rules))
  self.assertFalse(any('DOMAIN-SUFFIX,onedrive.live.com,' in r for r in rules))

 def test_filter_cannot_drop_an_explicit_menu_choice(self):
  with self.assertRaisesRegex(AssertionError,'Filter excludes menu choice'):
   graph_check([{'name':'A','type':'select','include-all':True,'filter':'HK','proxies':['DIRECT']}])
  self.assertEqual(graph_check([{'name':'A','type':'select','include-all':True,'filter':'HK|^DIRECT$','proxies':['DIRECT']}]),{'A'})
 def test_legacy_include_all_structure_and_dns_region_choices(self):
  recipe=json.loads(Path(__file__).with_name('recipe.json').read_text())
  graph_check(recipe['groups'])
  groups={g['name']:g for g in recipe['groups']}
  self.assertFalse(any(n.endswith('-Manual') for n in groups))
  regions={'HongKong':'HK','TaiWan':'TW','Japan':'JP','Singapore':'SG','Southeast.Asia':'SEA','America':'US','UnitedKingdom':'UK','Germany':'DE','Europe':'EU','AllServer':'All'}
  samples=['香港 01','HK 02','美国 01','US LAX 01','Taiwan 01','Japan 01','Singapore 01','UK London 01','DE Frankfurt 01','France 01','官网 香港','邀请美国','订阅到期']
  for name,prefix in regions.items():
   with self.subTest(region=name):
    menu=groups[name]
    self.assertEqual(menu['proxies'],[prefix+'-Auto',prefix+'-FallBack','DIRECT'])
    self.assertTrue(menu['include-all'])
    pattern=re.compile(menu['filter'])
    for member in menu['proxies']:self.assertIsNotNone(pattern.search(member))
    raw=re.compile(groups[prefix+'-Auto']['filter'])
    self.assertEqual([n for n in samples if pattern.search(n)],[n for n in samples if raw.search(n)])
    for suffix,kind in [('-Auto','url-test'),('-FallBack','fallback')]:
     worker=groups[prefix+suffix]
     self.assertEqual(worker['type'],kind)
     self.assertFalse(worker.get('hidden',False))
     self.assertTrue(worker['include-all'])
     self.assertEqual(worker['filter'],groups[prefix+'-Auto']['filter'])
  self.assertEqual(groups['DNS-Global']['proxies'],['HongKong','America','Japan','Singapore','AllServer','DIRECT'])
  self.assertNotIn('include-all',groups['DNS-Global'])
  self.assertNotIn('filter',groups['DNS-Global'])
  hk=re.compile(groups['HongKong']['filter'])
  self.assertEqual([n for n in samples if hk.search(n)],['香港 01','HK 02'])

 def test_provider_mode_preserves_rules_and_uses_a_single_airport_pool(self):
  recipe=json.loads(Path(__file__).with_name('recipe.json').read_text())
  original={'proxy-groups':recipe['groups'],'rules':recipe['rules'],'version':recipe['version']}
  variant=provider_variant(original)
  self.assertEqual(variant['rules'],original['rules'])
  self.assertEqual(len(variant['proxy-groups']),112)
  changed=[g for g in variant['proxy-groups'] if 'use' in g]
  self.assertEqual(len(changed),30)
  self.assertTrue(all(g['use']==['Airport'] for g in changed))
  self.assertFalse(any('include-all' in g for g in variant['proxy-groups']))
  original_by_name={g['name']:g for g in original['proxy-groups']}
  for group in variant['proxy-groups']:
   self.assertEqual(group.get('proxies'),original_by_name[group['name']].get('proxies'))
   self.assertEqual(group.get('filter'),original_by_name[group['name']].get('filter'))
  self.assertTrue(any(g.get('include-all') for g in original['proxy-groups']))

def validate_dist(dist,mihomo):
 cfg=yaml_load((dist/'通用分流_保留机场DNS.stoverride').read_text());report=json.loads((dist/'build-report.json').read_text())
 text=(dist/'通用分流_保留机场DNS.stoverride').read_text()
 assert text.splitlines()[0]=='#SUBSCRIBED https://raw.githubusercontent.com/sixvable/proxy-rule-icons-png/stash-release/universal.stoverride'
 assert (dist/'universal.stoverride').read_text()==text
 provider_text=(dist/'universal-provider.stoverride').read_text()
 assert provider_text==(dist/'通用分流_节点池版.stoverride').read_text()
 assert provider_text.splitlines()[0]=='#SUBSCRIBED https://raw.githubusercontent.com/sixvable/proxy-rule-icons-png/stash-release/universal-provider.stoverride'
 assert yaml_load(provider_text)==provider_variant(cfg)
 assert not Path(__file__).with_name('可选_开启IPv6.stoverride').exists()
 assert not {'dns','ipv6','proxies','proxy-providers','hosts','listeners','port','socks-port','mixed-port','http','script'}&set(cfg)
 assert len(cfg['rules'])<500
 assert not any(p['behavior']=='classical' for p in cfg['rule-providers'].values())
 assert all('/rules-v2/' in p['url'] and '/universal-stash-v2/' in p['path'] for p in cfg['rule-providers'].values())
 assert not any(',REJECT-DROP,REJECT-DROP' in r for r in cfg['rules'])
 graph_check(cfg['proxy-groups'])
 assert cfg['rules'][0]=='GEOIP,LAN,DIRECT,no-resolve'
 apple=next(i for i,r in enumerate(cfg['rules']) if ',Video-AppleTV' in r)
 china=next(i for i,r in enumerate(cfg['rules']) if ',Country-China' in r)
 assert apple<china
 assert next(i for i,r in enumerate(cfg['rules']) if r=='GEOIP,CN,Country-China')>next(i for i,r in enumerate(cfg['rules']) if ',Video-YouTube' in r)
 assert next(g for g in cfg['proxy-groups'] if g['name']=='Video-AppleTV')['proxies'][0]=='DIRECT'
 raw=json.dumps(cfg,ensure_ascii=False)
 assert '18767' not in raw and '18768' not in raw and 'Apple TV 双语字幕' not in raw
 assert not any(n in raw for n in ['sub.ltyun111.com','shanhai.you','password','uuid'])
 # Parse every generated MRS in an isolated file-only config, without nodes or network listeners.
 providers={n:{'type':'file','behavior':v['behavior'],'format':'mrs','path':'./rules/'+n+'.mrs'} for n,v in cfg['rule-providers'].items()}
 probe={'mode':'rule','log-level':'info','dns':{'enable':False},'rule-providers':providers,'rules':['RULE-SET,'+n+',DIRECT' for n in providers]+['MATCH,DIRECT']}
 f=dist/'mrs-validation.yaml';f.write_text(yaml_dump(probe))
 p=subprocess.run([mihomo,'-t','-d',str(dist.resolve()),'-f',str(f.resolve())],capture_output=True,text=True)
 (dist/'mrs-validation.log').write_text(p.stdout+p.stderr)
 assert p.returncode==0,p.stdout+p.stderr
 assert not re.search(r'level=(error|fatal|warning)',p.stdout+p.stderr,re.I),p.stdout+p.stderr
 print(json.dumps({'mrs_parse_passed':len(providers),'routing_rows':len(cfg['rules']),'native_stash_runtime_tested':False}))

if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--dist',type=Path,required=True);p.add_argument('--mihomo',required=True);a=p.parse_args()
 result=unittest.TextTestRunner().run(unittest.defaultTestLoader.loadTestsFromTestCase(OptimizerTests))
 if not result.wasSuccessful():raise SystemExit(1)
 validate_dist(a.dist,a.mihomo)
