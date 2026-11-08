#!/usr/bin/env python3
import argparse,ipaddress,json,re,subprocess,tempfile,unittest
from pathlib import Path
from build import minimized_domains,minimized_networks,graph_check,yaml_load,yaml_dump

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

def validate_dist(dist,mihomo):
 cfg=yaml_load((dist/'通用分流_保留机场DNS.stoverride').read_text());report=json.loads((dist/'build-report.json').read_text())
 assert not {'dns','proxies','proxy-providers','hosts','listeners','port','socks-port','mixed-port','http','script'}&set(cfg)
 assert len(cfg['rules'])<500
 assert not any(p['behavior']=='classical' for p in cfg['rule-providers'].values())
 graph_check(cfg['proxy-groups'])
 assert cfg['rules'][0]=='GEOIP,LAN,DIRECT,no-resolve'
 apple=next(i for i,r in enumerate(cfg['rules']) if ',Video-AppleTV' in r)
 china=next(i for i,r in enumerate(cfg['rules']) if ',Country-China' in r)
 assert apple<china
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
