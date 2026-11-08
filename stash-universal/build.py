#!/usr/bin/env python3
"""Build indexed Stash rules from public lists. No subscription input is accepted."""
import argparse,collections,concurrent.futures,copy,hashlib,ipaddress,json,os,re,subprocess,time,urllib.error,urllib.parse,urllib.request
from pathlib import Path
try:
 import yaml
except ImportError:
 yaml=None

def yaml_load(text):
 if yaml:return yaml.safe_load(text)
 p=subprocess.run(['ruby','-ryaml','-rjson','-e','puts JSON.generate(YAML.load(STDIN.read))'],input=text,text=True,capture_output=True,check=True)
 return json.loads(p.stdout)
def yaml_dump(obj):
 if yaml:return yaml.safe_dump(obj,allow_unicode=True,sort_keys=False,width=120)
 return subprocess.run(['ruby','-ryaml','-rjson','-e','puts YAML.dump(JSON.parse(STDIN.read))'],input=json.dumps(obj,ensure_ascii=False),text=True,capture_output=True,check=True).stdout.removeprefix('---\n')
def normalized(rule):
 fields=[x.strip() for x in rule.split(',')]
 fields[0]=fields[0].upper()
 return ','.join(fields)
def minimized_domains(values):
 values=set(values);suffixes={s[2:] for s in values if s.startswith('+.')}
 out=[]
 for value in sorted(values):
  name=value[2:] if value.startswith('+.') else value
  labels=name.split('.')
  # Only remove entries covered by an ordinary suffix, not arbitrary wildcards.
  parents=['.'.join(labels[i:]) for i in range(1,len(labels))]
  if any(p in suffixes for p in parents):continue
  if not value.startswith('+.') and name in suffixes:continue
  out.append(value)
 return out

def minimized_networks(values):
 nets=[ipaddress.ip_network(x,strict=False) for x in set(values)]
 out=[]
 for version in (4,6):out += [str(x) for x in ipaddress.collapse_addresses(n for n in nets if n.version==version)]
 return out

def fetch_source(name,definition,cache,refresh):
 path=cache/(name+'.json')
 if path.exists() and not refresh:
  obj=json.loads(path.read_text());assert obj['url']==definition['url'];return name,obj
 url=definition['url'];u=urllib.parse.urlsplit(url)
 assert u.scheme=='https' and u.hostname in {'raw.githubusercontent.com','www.cloudflare.com'}
 assert not u.query and not u.username and not u.password
 error=None
 for attempt in range(3):
  try:
   req=urllib.request.Request(url,headers={'User-Agent':'Stash-Universal-Public-Rules/1.0'})
   with urllib.request.urlopen(req,timeout=30) as res:
    assert res.status==200;data=res.read(5_000_001);assert len(data)<=5_000_000
   text=data.decode('utf-8-sig')
   if definition['format']=='text':items=[x.strip() for x in text.splitlines() if x.strip() and not x.lstrip().startswith('#')]
   else:items=yaml_load(text)['payload']
   assert isinstance(items,list) and items and all(isinstance(x,str) and x.strip() for x in items)
   obj={'url':url,'payload':items,'sha256':hashlib.sha256(data).hexdigest(),'origin':'downloaded_public_source'}
   tmp=path.with_suffix('.tmp');tmp.write_text(json.dumps(obj,ensure_ascii=False));tmp.replace(path)
   return name,obj
  except Exception as e:
   error=e
   if isinstance(e,urllib.error.HTTPError) and e.code in (400,401,403,404):break
   if attempt<2:time.sleep(attempt+1)
 raise RuntimeError(f'Public source {name} failed: {type(error).__name__}')

def split_rule(rule):
 parts=rule.split(',');options=[]
 while parts[-1] in {'no-resolve','no-track'}:options.insert(0,parts.pop())
 return ','.join(parts[:-1]),parts[-1],options

def graph_check(groups):
 names={g['name'] for g in groups};assert len(names)==len(groups)
 edges={g['name']:set(g.get('proxies',[]))&names for g in groups}
 for g in groups:
  assert set(g.get('proxies',[]))<=names|{'DIRECT','REJECT','REJECT-DROP'}
  if 'filter' in g:re.compile(g['filter'])
 def visit(n,path):
  assert n not in path,f'Group cycle: {n}'
  for c in edges[n]:visit(c,path|{n})
 for n in names:visit(n,set())
 return names

class Compiler:
 def __init__(self,recipe,sources,out,mihomo):
  self.recipe=recipe;self.sources=sources;self.out=out;self.mihomo=mihomo
  self.providers={};self.rules=[];self.stats=[];self.dropped_process=0;self.residual=0;self.expanded_count=0;self.segment=0
  self.coverage=[];self.convert_log=[];self.repairs=[]
 def expand(self,predicate,options):
  kind,*values=predicate.split(',')
  if kind in {'RULE-SET','GEOSITE'}:
   name=('geosite:' if kind=='GEOSITE' else '')+values[0]
   definition=self.recipe['providers'][name];payload=self.sources[name]['payload'];behavior=definition['behavior'];result=[]
   for raw in payload:
    if behavior=='domain':
     value=raw.strip();result.append(('DOMAIN-SUFFIX,'+value[2:] if value.startswith('+.') else 'DOMAIN,'+value,tuple(options)))
    elif behavior=='ipcidr':result.append(('IP-CIDR,'+raw.strip(),tuple(options)))
    else:
     rule=normalized(raw);parts=rule.split(',');extra=[]
     while parts[-1] in {'no-resolve','no-track'}:extra.insert(0,parts.pop())
     result.append((','.join(parts),tuple(sorted(set(options+extra)))))
   return result
  return [(predicate,tuple(options))]
 def provider(self,name,behavior,values):
  assert values
  p=self.out/'rules'/f'{name}.txt';p.parent.mkdir(parents=True,exist_ok=True)
  p.write_text('\n'.join(values)+'\n')
  m=p.with_suffix('.mrs')
  run=subprocess.run([self.mihomo,'convert-ruleset',behavior,'text',str(p),str(m)],text=True,capture_output=True)
  assert run.returncode==0 and m.exists() and m.stat().st_size>4,f'MRS conversion failed: {name}: {run.stderr[:180]}'
  assert not re.search(r'level=(warning|error|fatal)',run.stdout+run.stderr,re.I),f'MRS conversion rejected data: {name}'
  self.providers[name]={'behavior':behavior,'format':'mrs','url':f'https://raw.githubusercontent.com/{self.recipe["repository"]}/stash-release/rules/{name}.mrs','path':f'./ruleset/universal-stash-v1/{name}.mrs','interval':86400}
  self.stats.append({'name':name,'behavior':behavior,'entries':len(values),'text_bytes':p.stat().st_size,'mrs_bytes':m.stat().st_size,'sha256':hashlib.sha256(m.read_bytes()).hexdigest()})
  return name
 def emit(self,target,atoms,label=None):
  self.segment+=1;dom=[];ip=collections.defaultdict(list);other=[]
  for pred,opts in atoms:
   self.expanded_count+=1
   typ,_,value=pred.partition(',')
   if typ.startswith('PROCESS-'):
    self.dropped_process+=1;continue
   if typ=='DOMAIN-SUFFIX':
    original=value
    while value.startswith('+.'):value=value[2:]
    value=value.lstrip('.')
    if value!=original:self.repairs.append({'kind':'domain_suffix_notation','before':original,'after':value})
    if any('?' in label or ('*' in label and label!='*') for label in value.split('.')):
     pattern='^(?:[^.]+\\.)*'+re.escape(value).replace(r'\*','[^.]*').replace(r'\?','[^.]')+'$'
     other.append(('DOMAIN-REGEX,'+pattern,opts))
     self.repairs.append({'kind':'partial_label_wildcard_to_regex','before':original,'after':pattern})
    else:dom.append('+.'+value)
   elif typ=='DOMAIN' and not any(x in value for x in ['*','?']):dom.append(value)
   elif typ=='DOMAIN' and value.startswith('*.'):dom.append(value)
   elif typ in {'IP-CIDR','IP-CIDR6'}:
    ip[opts].append(value)
   elif typ in {'DOMAIN-KEYWORD','DOMAIN-REGEX','DOMAIN-WILDCARD','IP-ASN','GEOIP','NETWORK','DST-PORT','SRC-PORT','AND','OR','NOT'}:other.append((pred,opts))
   else:raise AssertionError(f'Unsupported public rule type: {typ}')
  name=label or f'{self.segment:03d}-'+re.sub(r'[^A-Za-z0-9_-]','-',target)
  if dom:
   mini=minimized_domains(dom)
   suffixes={v[2:] for v in mini if v.startswith('+.')};exact=set(mini)
   for v in dom:
    h=v[2:] if v.startswith('+.') else v
    assert v in exact or any('.'.join(h.split('.')[i:]) in suffixes for i in range(len(h.split('.'))))
   key=self.provider(name if label else name+'-domain','domain',mini)
   self.rules.append(f'RULE-SET,{key},{target}')
  seen=set()
  for pred,opts in other:
   r=pred+','+target+(''+','+','.join(opts) if opts else '')
   if r not in seen:self.rules.append(r);self.residual+=1;seen.add(r)
  for idx,(opts,items) in enumerate(sorted(ip.items())):
   mini=minimized_networks(items);networks=[ipaddress.ip_network(x) for x in mini]
   for v in items:
    n=ipaddress.ip_network(v,strict=False)
    assert any(n.version==m.version and n.subnet_of(m) for m in networks)
   key=self.provider(name+f'-ip{idx}','ipcidr',mini)
   self.rules.append(f'RULE-SET,{key},{target}'+(','+','.join(opts) if opts else ''))
  self.coverage.append({'target':target,'source_atoms':len(atoms),'domain_before':len(dom),'domain_after':len(minimized_domains(dom)),'ip_before':sum(map(len,ip.values())),'process_ignored':sum(x[0].startswith('PROCESS-') for x in atoms)})
 def build(self):
  pending=[];last_target=None
  def flush():
   nonlocal pending,last_target
   if pending:self.emit(last_target,pending)
   pending=[];last_target=None
  for rule in self.recipe['rules']:
   pred,target,options=split_rule(rule);typ=pred.split(',')[0]
   if pred=='RULE-SET,'+self.recipe['dns_provider']:
    flush();self.emit(target,self.expand(pred,options),self.recipe['dns_provider']);continue
   if typ not in {'DOMAIN','DOMAIN-SUFFIX','IP-CIDR','IP-CIDR6','RULE-SET','GEOSITE'}:
    flush();self.rules.append(rule);continue
   if last_target is not None and last_target!=target:flush()
   last_target=target;pending.extend(self.expand(pred,options))
  flush()
  names=graph_check(self.recipe['groups'])
  for rule in self.rules:
   pred,target,opts=split_rule(rule);assert target in names|{'DIRECT','REJECT','REJECT-DROP'}
   if pred.startswith('RULE-SET,'):assert pred.split(',')[1] in self.providers
  assert self.rules[-1]=='MATCH,Final'
  assert not any(r.startswith(('GEOSITE,','PROCESS-')) for r in self.rules)
  cfg={'name':'通用分流｜保留机场 DNS','desc':'直接使用机场原始订阅。替换策略组与分流，保留原配置 DNS、节点和订阅更新。适用于 Stash 3.6+；请关闭其它完整分流覆写。','category':'自用分流','version':self.recipe['version'],'mode':'rule','proxy-groups':self.recipe['groups'],'rule-providers':self.providers,'rules':self.rules}
  text=yaml_dump(cfg)
  for key in ('proxy-groups','rule-providers','rules'):text=re.sub('^'+key+r':\s*$',key+': #!replace',text,flags=re.M)
  assert not set(cfg)&{'dns','hosts','proxies','proxy-providers','listeners','mixed-port','port','socks-port','tun','http','script'}
  assert yaml_load(text)==cfg
  assert all(key+': #!replace' in text for key in ('proxy-groups','rule-providers','rules'))
  (self.out/'通用分流_保留机场DNS.stoverride').write_text(text)
  (self.out/'config.json').write_text(json.dumps(cfg,ensure_ascii=False,indent=2)+'\n')
  report={'groups':len(cfg['proxy-groups']),'routing_rows':len(self.rules),'mrs_providers':len(self.providers),'classical_providers':0,'geosite_routing_rows':0,'expanded_public_atoms':self.expanded_count,'process_rules_removed':self.dropped_process,'residual_rule_rows':self.residual,'indexed_entries':sum(p['entries'] for p in self.stats),'text_bytes':sum(p['text_bytes'] for p in self.stats),'mrs_bytes':sum(p['mrs_bytes'] for p in self.stats),'dns_untouched':True,'node_and_subscription_fields_untouched':True,'coverage_assertions_passed':True,'ios_runtime_tested':False,'sources':{n:{k:v for k,v in x.items() if k!='payload'} for n,x in self.sources.items()},'providers':self.stats,'segments':self.coverage}
  report['source_notation_repairs']=self.repairs
  (self.out/'build-report.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
  print(json.dumps({k:v for k,v in report.items() if k not in ('providers','segments','sources')},ensure_ascii=False,indent=2))

if __name__=='__main__':
 ap=argparse.ArgumentParser();ap.add_argument('--cache',type=Path,default=Path('.cache'));ap.add_argument('--out',type=Path,default=Path('dist'));ap.add_argument('--mihomo',required=True);ap.add_argument('--refresh',action='store_true');ap.add_argument('--fetch-only',action='store_true');a=ap.parse_args()
 recipe=json.loads(Path(__file__).with_name('recipe.json').read_text());a.cache.mkdir(parents=True,exist_ok=True);a.out.mkdir(parents=True,exist_ok=True)
 sources={};errors=[]
 with concurrent.futures.ThreadPoolExecutor(max_workers=6) as pool:
  fs={pool.submit(fetch_source,n,d,a.cache,a.refresh):n for n,d in recipe['providers'].items()}
  for i,f in enumerate(concurrent.futures.as_completed(fs),1):
   try:n,obj=f.result();sources[n]=obj
   except Exception as e:errors.append(str(e))
   if i%20==0:print(f'Public sources processed: {i}/{len(fs)}',flush=True)
 if errors:
  (a.out/'fetch-errors.json').write_text(json.dumps(errors,ensure_ascii=False,indent=2));raise SystemExit('\n'.join(errors))
 if not a.fetch_only:Compiler(recipe,sources,a.out,a.mihomo).build()
