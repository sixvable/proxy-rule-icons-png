#!/usr/bin/env python3
import argparse,ipaddress,json,re,subprocess,tempfile,unittest
from pathlib import Path
from build import Compiler,minimized_domains,minimized_networks,graph_check,yaml_load,yaml_dump

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
  for name,samples in {'HK-Manual':['🇭🇰 香港1 | [x1] HK','Hong Kong 01'],'US-Manual':['🇺🇸 美国01','US LAX 01'],'TW-Manual':['Taiwan 01','🇹🇼 台湾1']}.items():
   regex=re.compile(groups[name]['filter'])
   for sample in samples:self.assertIsNotNone(regex.search(sample),sample)
   self.assertIsNone(regex.search('官网 '+samples[0]))
 def test_latest_rule_priorities_and_removed_groups(self):
  recipe=json.loads(Path(__file__).with_name('recipe.json').read_text())
  rules=recipe['rules'];names=[g['name'] for g in recipe['groups']]
  self.assertEqual(len(names),122);self.assertEqual(len(rules),168)
  self.assertLess(names.index('All-FallBack'),names.index('Video-AppleTV'))
  self.assertLess(names.index('Video-AppleTV'),names.index('Network-LAN'))
  self.assertLess(rules.index('GEOSITE,private,Network-LAN'),rules.index('GEOSITE,apple-tvplus,Video-AppleTV'))
  self.assertLess(rules.index('RULE-SET,ChinaDNS_Domain,DNS-China'),rules.index('RULE-SET,GlobalDNS_IP,DNS-Global,no-resolve'))
  self.assertFalse(set(names)&{'Global-CDN','DNS-Global-Auto','AppleTV-Media-IPv6','Apple TV 双语字幕'})
  self.assertFalse(any('DST-PORT,53' in r or 'DST-PORT,853' in r for r in rules))
  self.assertFalse(any('DOMAIN-SUFFIX,onedrive.live.com,' in r for r in rules))

 def test_dynamic_node_collection_cannot_replace_explicit_menu(self):
  with self.assertRaisesRegex(AssertionError,'Mixed node collection and menu'):
   graph_check([{'name':'A','type':'select','include-all':True,'proxies':['DIRECT']}])
  with self.assertRaisesRegex(AssertionError,'Filter on explicit menu'):
   graph_check([{'name':'A','type':'select','filter':'HK','proxies':['DIRECT']}])
 def test_region_and_dns_menus_keep_all_selection_modes(self):
  recipe=json.loads(Path(__file__).with_name('recipe.json').read_text())
  graph_check(recipe['groups'])
  groups={g['name']:g for g in recipe['groups']}
  regions={'HongKong':'HK','TaiWan':'TW','Japan':'JP','Singapore':'SG','Southeast.Asia':'SEA','America':'US','UnitedKingdom':'UK','Germany':'DE','Europe':'EU','AllServer':'All'}
  for name,prefix in regions.items():
   with self.subTest(region=name):
    menu=groups[name]
    self.assertEqual(menu['proxies'],[prefix+'-Auto',prefix+'-FallBack',prefix+'-Manual','DIRECT'])
    self.assertNotIn('include-all',menu)
    self.assertNotIn('filter',menu)
    manual=groups[prefix+'-Manual']
    self.assertEqual(manual['type'],'select')
    self.assertTrue(manual['include-all'])
    self.assertFalse(manual.get('hidden',False))
    self.assertFalse(manual.get('proxies'))
    for suffix,kind in [('-Auto','url-test'),('-FallBack','fallback')]:
     worker=groups[prefix+suffix]
     self.assertEqual(worker['type'],kind)
     self.assertEqual(worker['filter'],manual['filter'])
     self.assertTrue(worker['include-all'])
  self.assertEqual(groups['DNS-Global']['proxies'],['HongKong','America','Japan','Singapore','All-Manual','DIRECT'])
  self.assertNotIn('include-all',groups['DNS-Global'])
  self.assertNotIn('filter',groups['DNS-Global'])
  samples=['香港 01','HK 02','美国 01','官网 香港','Hong Kong 03']
  hk=re.compile(groups['HK-Manual']['filter'])
  self.assertEqual([n for n in samples if hk.search(n)],['香港 01','HK 02','Hong Kong 03'])

def validate_dist(dist,mihomo):
 cfg=yaml_load((dist/'通用分流_保留机场DNS.stoverride').read_text());report=json.loads((dist/'build-report.json').read_text())
 text=(dist/'通用分流_保留机场DNS.stoverride').read_text()
 assert text.splitlines()[0]=='#SUBSCRIBED https://raw.githubusercontent.com/sixvable/proxy-rule-icons-png/stash-release/universal.stoverride'
 assert (dist/'universal.stoverride').read_text()==text
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
