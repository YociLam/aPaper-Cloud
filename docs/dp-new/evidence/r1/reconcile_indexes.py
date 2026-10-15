import pathlib,re,json,subprocess,html,collections
from html.parser import HTMLParser
app=pathlib.Path('/Users/junesum/.codex/worktrees/dp-new-candidate/AtomPaper');root=pathlib.Path('/tmp/dp-new-r1-audit')
class Links(HTMLParser):
 def __init__(self):super().__init__();self.links=[]
 def handle_starttag(self,tag,attrs):
  if tag=='a':self.links.append(dict(attrs).get('href',''))
def links(name):p=Links();p.feed((root/(name+'.data')).read_text());return p.links
def rows(venue,year):
 data=subprocess.check_output(['zstd','-dc',str(app/f'apaper-cloud/public/v1/conferences/packs/{venue}/{year}.jsonl.zst')]);return [json.loads(l) for l in data.splitlines()]
result={}
for v in ['cvpr','acl']:
 r=rows(v,2026); ids={x['id'] for x in r}
 if v=='cvpr':official={x.split('/')[-1].removesuffix('.html') for x in links(v) if '/content/CVPR2026/html/' in x}
 else:official={x.strip('/') for x in links(v) if re.fullmatch(r'/2026\.(?:acl-(?:long|short|demo|industry|srw|tutorials)|findings-acl)\.\d+/',x)}
 result[v]={'official_count':len(official),'pack_count':len(ids),'index_only':sorted(official-ids),'pack_only':sorted(ids-official)}
 if v=='acl':result[v]['findings_count']=len({x.strip('/') for x in links('findings') if re.fullmatch(r'/2026\.findings-acl\.\d+/',x)});result[v]['group_counts']=dict(collections.Counter(x['id'].rsplit('.',1)[0] for x in r))
(root/'reconciliation.json').write_text(json.dumps(result,indent=2));print(json.dumps(result,indent=2))
print('ICLR group',json.dumps(json.loads((root/'iclr_group.data').read_text())['groups'][0].get('content'),indent=2)[:6000])
for v in ['sosp2026','sp_publications','emnlp']:
 print(v,[x for x in links(v) if any(t in x.lower() for t in ['paper','program','proceed','2026','2025'])][:35])
