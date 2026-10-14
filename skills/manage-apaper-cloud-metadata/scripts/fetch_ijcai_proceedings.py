#!/usr/bin/env python3
"""Acquire final IJCAI proceedings, retaining publisher subjects and ordered authors."""
import argparse
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime
from html.parser import HTMLParser
import json
from pathlib import Path
import re
from urllib.request import Request, urlopen

class Node:
    def __init__(self, tag='', attrs=None, parent=None):
        self.tag, self.attrs, self.parent, self.children = tag, dict(attrs or []), parent, []
    def text(self):
        return ' '.join(' '.join(c.text() if isinstance(c, Node) else c for c in self.children).split())
    def has(self, name):
        return name in self.attrs.get('class','').split()
    def nodes(self):
        yield self
        for child in self.children:
            if isinstance(child, Node): yield from child.nodes()

class HTML(HTMLParser):
    def __init__(self, value):
        super().__init__(convert_charrefs=True)
        self.root = self.current = Node()
        self.feed(value)
    def handle_starttag(self, tag, attrs):
        node = Node(tag, attrs, self.current); self.current.children.append(node)
        if tag not in {'meta','link','img','br','hr','input','source','wbr'}: self.current = node
    def handle_endtag(self, tag):
        node = self.current
        while node.parent:
            if node.tag == tag: self.current = node.parent; break
            node = node.parent
    def handle_data(self, value): self.current.children.append(value)

def fetch(url, path):
    if path.exists(): return path.read_text()
    request=Request(url, headers={'User-Agent':'aPaper-Cloud-Metadata/1.0'})
    with urlopen(request,timeout=45) as response: value=response.read().decode('utf-8')
    path.write_text(value); return value

def parse_index(html, year):
    rows=[]
    for paper in (n for n in HTML(html).root.nodes() if n.has('paper_wrapper')):
        parent=paper.parent
        while parent and not parent.has('subsection'): parent=parent.parent
        label=next((n.text() for n in parent.nodes() if n.has('subsection_title')), '') if parent else ''
        kind='subject_area'
        if not label:
            section=parent
            while section and not section.has('section'): section=section.parent
            label=next((n.text() for n in section.nodes() if n.has('section_title')), '') if section else ''
            kind='track'
        rows.append((paper.attrs['id'].removeprefix('paper'),label,kind))
    if not rows or len({row[0] for row in rows}) != len(rows): raise ValueError('empty or duplicate IJCAI index')
    return rows

def parse_detail(html, number, label, year, group_kind="subject_area"):
    nodes=list(HTML(html).root.nodes()); meta={}
    for n in nodes:
        if n.tag=='meta' and n.attrs.get('name'):meta.setdefault(n.attrs['name'],[]).append(n.attrs.get('content',''))
    abstract=next((n.text() for n in nodes if n.has('col-md-12') and not any(x.has('keywords') for x in n.nodes()) and n.text()),'')
    date=datetime.strptime(meta['citation_publication_date'][0],'%Y/%m/%d')
    if date.year!=year:raise ValueError('wrong publisher year')
    title=meta['citation_title'][0];authors=meta['citation_author'];pdf=meta['citation_pdf_url'][0]
    if not all([title,authors,abstract,pdf]):raise ValueError('incomplete IJCAI paper')
    group=None
    if label:group={'id':'ijcai.'+re.sub(r'[^a-z0-9]+','-',label.lower()).strip('-'),'name':label,'kind':group_kind}
    return {'id':f'ijcai-{year}-{number}','source_paper_id':f'ijcai-{year}-{number}',
        'title':title,'authors':authors,'abstract':abstract,'link':f'https://www.ijcai.org/proceedings/{year}/{number}',
        'pdf_url':pdf,'doi':(meta.get('citation_doi') or [''])[0],
        'categories':[n.text() for n in nodes if n.has('topic')], 'source_group':group,
        'published':date.strftime('%Y-%m-%dT00:00:00Z'),'updated_at':date.strftime('%Y-%m-%dT00:00:00Z')}

def main():
    p=argparse.ArgumentParser();p.add_argument('--year',type=int,required=True);p.add_argument('--cache-dir',type=Path,required=True);p.add_argument('--output',type=Path,required=True);args=p.parse_args()
    args.cache_dir.mkdir(parents=True,exist_ok=True);origin=f'https://www.ijcai.org/proceedings/{args.year}'
    index=fetch(origin+'/',args.cache_dir/'index.html');rows=parse_index(index,args.year)
    def acquire(row):
        number,label,kind=row;return parse_detail(fetch(origin+'/'+number,args.cache_dir/(number+'.html')),number,label,args.year,kind)
    with ThreadPoolExecutor(max_workers=4) as pool: records=list(pool.map(acquire,rows))
    args.output.write_text(json.dumps(records,ensure_ascii=False,indent=2)+'\n');print(f'record_count={len(records)}')
if __name__=='__main__':main()
