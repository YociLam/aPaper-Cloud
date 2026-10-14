#!/usr/bin/env python3
"""Bounded publisher/Crossref journal extraction. No runtime service dependency."""
from __future__ import annotations
import argparse, concurrent.futures, hashlib, html, json, re, time
from pathlib import Path
from urllib.parse import urlencode
from urllib.request import Request, urlopen
from html.parser import HTMLParser
LIMIT=32*1024*1024
class Metadata(HTMLParser):
    def __init__(self): super().__init__(); self.meta={}
    def handle_starttag(self, tag, attrs):
        a=dict(attrs)
        if tag=='meta' and a.get('name','').startswith('citation_'): self.meta[a['name']]=a.get('content','')
def acquire(url, raw):
    path=raw/(hashlib.sha256(url.encode()).hexdigest()+'.input')
    if path.exists():
        b=path.read_bytes()
        if not b or len(b)>=LIMIT: raise ValueError("cached response is empty or reaches the byte ceiling")
        return b
    error=None
    for attempt in range(3):
        try:
            if url.startswith('https://api.crossref.org/'): time.sleep(1)
            with urlopen(Request(url,headers={'User-Agent':'aPaper-Cloud-Metadata/1.0 (journal collection verification)'}),timeout=45) as r:
                b=r.read(LIMIT+1)
                if len(b)>=LIMIT: raise ValueError('response ceiling reached; completeness unproven')
                if r.headers.get('Content-Length') and r.headers.get('Content-Encoding') is None and len(b)!=int(r.headers['Content-Length']):raise ValueError('truncated response')
            if not b:raise ValueError('empty acquisition response')
            path.write_bytes(b);return b
        except Exception as e:
            error=e
            if attempt<2:
                delay = min(30, int(getattr(e, 'headers', {}).get('Retry-After', '5'))) if getattr(e, 'code', None) == 429 else attempt+1
                time.sleep(delay)
    raise RuntimeError(f'{url}: {error}')
def text(value):
    value=re.sub(r'</(?:jats:)?(?:p|title|sec)>','\n',value,flags=re.I)
    return '\n'.join(' '.join(html.unescape(re.sub('<[^>]+>',' ',line)).split()) for line in value.splitlines() if line.strip()).strip()
def date(parts):
    if not parts:return None
    p=parts.get('date-parts',[[]])[0]
    return '-'.join(str(n) if i==0 else f'{n:02d}' for i,n in enumerate(p)) or None
def crossref(c,year,cutoff,raw):
    items={};pages=[];dups=0
    # Union covers online-first and records which only provide issue dates.
    for field in ['online-pub-date','pub-date']:
        cursor='*';seen=set();total=None;count=0
        for number in range(200):
            url='https://api.crossref.org/journals/'+c['issn']+'/works?'+urlencode({'filter':f'from-{field}:{year}-01-01,until-{field}:{cutoff[:10]}','rows':200,'cursor':cursor})
            msg=json.loads(acquire(url,raw))['message'];batch=msg['items']
            if total is None:total=msg['total-results']
            if total!=msg['total-results']:raise ValueError('Crossref count changed within pagination')
            pages.append({'url':url,'count':len(batch),'total':total,'terminal':not batch})
            if not batch:
                if count!=total:raise ValueError(f'incomplete pagination {count}/{total}')
                break
            count+=len(batch)
            for r in batch:
                doi=r['DOI'].lower()
                if doi in items:dups+=1
                items[doi]=r
            nxt=msg['next-cursor']
            if nxt in seen:raise ValueError('repeated nonterminal cursor')
            seen.add(nxt);cursor=nxt
        else:raise ValueError('pagination bound exceeded')
    return items,pages,dups

def plos(c,year,cutoff,raw):
    items={};pages=[];total=None
    q=f'eissn:{c["issn"]} AND doc_type:full AND publication_date:[{year}-01-01T00:00:00Z TO {cutoff}]'
    for start in range(0,30001,200):
        url='https://api.plos.org/search?'+urlencode({'q':q,'wt':'json','rows':200,'start':start,'sort':'id asc'})
        r=json.loads(acquire(url,raw))['response'];batch=r['docs']
        if total is None:total=r['numFound']
        if r['numFound']!=total:raise ValueError('publisher count changed')
        pages.append({'url':url,'count':len(batch),'total':total,'terminal':not batch})
        if not batch:
            if len(items)!=total:raise ValueError('publisher pagination mismatch')
            if total == 0:raise ValueError('empty publisher corpus requires explicit latest-period investigation')
            return items,pages
        for item in batch:
            if item['id'] in items:raise ValueError('duplicate publisher identity')
            if item['eissn']!=c['issn'] or item['journal'].casefold()!=c['title'].casefold():raise ValueError('publisher identity mismatch')
            items[item['id'].lower()]=item
    raise ValueError('publisher pagination bound exceeded')

def normalize(doi,r,p,c,source,year,cutoff,raw):
    online=date(r.get('published-online'));issue=date(r.get('published-print'));published=p['publication_date'][:10] if p else online or date(r.get('issued'))
    if not published or not f'{year}-01-01'<=published<=cutoff[:10]:return None,'excluded','outside_canonical_publication_period'
    title=text((r.get('title') or [''])[0]);abstract=text(' '.join(p.get('abstract',[]))) if p else text(r.get('abstract',''))
    native=p['article_type'] if p else r.get('type','')
    landing=r.get('resource',{}).get('primary',{}).get('URL') or r['URL'];pdf=None
    if source=='glj':
        try:
            b=acquire(landing,raw);page=b.decode('utf-8');parser=Metadata();parser.feed(page)
            if '</html>' not in page.lower() or parser.meta.get('citation_doi','').lower()!=doi:return None,'unresolved','publisher_page_incomplete_or_identity_mismatch'
            match=re.search(r'>\s*Type\s*</dt>\s*<dd[^>]*>(.*?)</dd>',page,re.S);native=text(match[1]) if match else ''
            pdf=parser.meta.get('citation_pdf_url');abstract=parser.meta.get('citation_abstract') or abstract
        except Exception as e:return None,'unresolved','publisher_page_acquisition: '+str(e)
    elif p:
        landing=f'https://journals.plos.org/{c["slug"]}/article?id={doi}'
        pdf=f'https://journals.plos.org/{c["slug"]}/article/file?id={doi}&type=printable'
    else:
        pdf=next((a['URL'] for a in r.get('link',[]) if a.get('content-type')=='application/pdf' and a['URL'].startswith('https://academic.oup.com/')),None)
    if native not in c['types'] or re.match(r'(?i)^(correction|retraction|expression of concern|erratum|editorial|corrigendum)',title):return None,'excluded','publisher_article_type: '+native
    if any(x.get('type') in ['correction','retraction','withdrawal','expression_of_concern','erratum'] for x in r.get('update-to',[])) or r.get('relation',{}).get('is-retracted-by'):return None,'excluded','publication_update_or_retraction_relation'
    licenses=[l['URL'].replace('http://creativecommons.org/','https://creativecommons.org/') for l in r.get('license',[]) if (date(l.get('start')) or '0000')<=cutoff[:10]]
    license=next((l for l in licenses if re.match(r'https://creativecommons.org/(?:licenses/by/\d|publicdomain/zero/1.0/)' ,l)),None)
    if not license and p:
        try:
            b=acquire(landing,raw);page=b.decode('utf-8');parser=Metadata();parser.feed(page)
            if '</html>' in page.lower() and parser.meta.get('citation_doi','').lower()==doi:
                match=re.search(r'https?://creativecommons.org/(?:licenses/by/4.0/|publicdomain/zero/1.0/)' ,page)
                if match: license=match.group().replace('http://','https://')
        except Exception: pass
    if not license:
        if any('/licenses/by-nc' in url for url in licenses): return None,'excluded','noncommercial_license_outside_redistribution_scope'
        return None,'unresolved','missing_effective_abstract_reuse_license'
    authors=[' '.join(filter(None,[a.get('given'),a.get('family')])) or a.get('name','') for a in r.get('author',[])]
    if not abstract or not title or not authors or any(not a for a in authors):return None,'unresolved','missing_abstract_title_or_ordered_authors'
    journal={'title':c['title'],'publisher':c['publisher'],'issns':[c['issn']], 'article_type':native,'volume':r.get('volume'),'issue':r.get('issue'),'article_number':r.get('article-number'),'pages':r.get('page'),'provenance_urls':['https://api.crossref.org/works/'+doi,landing],'online_published_at':online,'issue_published_at':issue,'license_url':license,'publication_updates':[{'doi':u['DOI'].lower(),'update_type':u['type'],'published_at':date(u.get('updated'))} for u in r.get('update-to',[])]}
    return {'schema_version':1,'source_kind':'journal','journal':journal,'id':doi,'venue_id':source,'edition_id':f'{source}:{year}','year':year,'title':title,'authors':authors,'abstract':abstract,'landing_url':landing,'pdf_url':pdf,'doi':doi,'categories':[],'published_at':published,'updated_at':published,'acceptance_status':'published','provenance_url':'https://api.crossref.org/works/'+doi,'metadata_channel':'publisher-crossref'+('-plos-api' if p else '-cambridge-page' if source=='glj' else '')},'admitted','licensed_published_article'

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--source',required=True);ap.add_argument('--year',type=int,required=True);ap.add_argument('--cutoff',required=True);ap.add_argument('--output',type=Path,required=True);a=ap.parse_args()
    c=json.loads(Path(__file__).with_name('journal_sources.json').read_text())[a.source]
    a.output.mkdir(parents=True,exist_ok=True);raw=a.output/'raw';raw.mkdir(exist_ok=True)
    records,pages,dups=crossref(c,a.year,a.cutoff,raw)
    publisher,ppages=plos(c,a.year,a.cutoff,raw) if 'plos' in c else ({},[])
    ids=sorted(set(publisher) if publisher else records);out=[];audit=[]
    def one(doi):
        if publisher.get(doi,{}).get('article_type') not in c['types'] and publisher:
            return doi,None,'excluded','publisher_article_type: '+publisher[doi].get('article_type','unknown')
        if doi not in records:return doi,None,'unresolved','publisher_identity_absent_from_deposit'
        record,status,reason=normalize(doi,records[doi],publisher.get(doi),c,a.source,a.year,a.cutoff,raw)
        return doi,record,status,reason
    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:
        for doi,record,status,reason in pool.map(one,ids):
            upstream=records.get(doi,{})
            audit.append({'doi':doi,'status':status,'reason':reason,'publisher_updates':upstream.get('update-to',[]),'publisher_relations':upstream.get('relation',{}),'publisher_license_urls':[x['URL'] for x in upstream.get('license',[])],'publisher_article_type':publisher.get(doi,{}).get('article_type') or upstream.get('type')})
            if record:out.append(record)
    checks_path = a.output/'pdf-checks.json'
    if checks_path.exists():
        checks = json.loads(checks_path.read_text())
        for record in out:
            check = checks.get(record['id'])
            if check and check['url'] == record['pdf_url'] and check['status'] != 'verified': record['pdf_url'] = None
    if not out:raise ValueError('zero admitted articles is not successful ingestion')
    counts={k:sum(x['status']==k for x in audit) for k in ['admitted','excluded','unresolved']}
    coverage={'period_start':f'{a.year}-01-01','period_end':a.cutoff[:10],'cutoff':a.cutoff,'included_article_types':c['types'],'discovered':len(ids),**counts,'duplicates':dups,'completeness':'snapshot_partial' if counts['unresolved'] else 'snapshot_complete','identity_basis':'PLOS publisher Solr index' if publisher else 'publisher-deposited Crossref online/issued works'}
    result={'source':a.source,'identity':c,'coverage':coverage,'identity_basis':'PLOS publisher index' if publisher else 'publisher-deposited Crossref works (not independently complete publisher archive)','duplicate_basis':'overlap between the two Crossref date-filter enumerations; packs contain unique DOI records','crossref_only_ids':sorted(set(records)-set(publisher)) if publisher else [],'pages':pages+ppages,'identities':audit,'raw_input_hashes':{p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in raw.iterdir()}}
    (a.output/(a.source+'.jsonl')).write_text(''.join(json.dumps(r,ensure_ascii=False)+'\n' for r in out))
    (a.output/'reconciliation.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps(coverage))
if __name__=='__main__':main()
