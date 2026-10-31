#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""List and refresh the public MotionTemplates catalog, without credentials."""
import argparse, html, json, os, tempfile, urllib.request
from pathlib import Path
from datetime import datetime, timezone

SOURCE='https://raw.githubusercontent.com/motiontemplates/all/main/catalog.json'
SNAPSHOT=Path(__file__).resolve().parents[1]/'references/motiontemplates-catalog.json'

def normalize(data):
    if data.get('format')!='motiongit.catalog/1' or not isinstance(data.get('templates'),list):
        raise ValueError('Unsupported public catalog format')
    declared=data.get('listing',{}).get('templateCount')
    if isinstance(declared,int) and declared!=len(data['templates']):
        raise ValueError('Catalog template count mismatch')
    rows=[]
    def add(item,kind='template'):
        title=item.get('title') or {};download=item.get('download') or {}
        rows.append({'id':str(item.get('repositoryId') or item.get('previewId') or ''),
                     'title':title.get('zh') if isinstance(title,dict) else str(title),
                     'orientation':item.get('orientation'),'ratio':item.get('ratio'),
                     'website':item.get('website'),'repository':item.get('repository'),
                     'version':item.get('version'),'demo':item.get('demo'),'preview':item.get('preview') or item.get('poster'),
                     'kind':kind,'availability':download.get('availability'),
                     'downloadType':download.get('type'),'directDownloadUrls':download.get('urls') if download.get('type')=='direct-package' else None,
                     'githubSourceIncluded':item.get('githubSourceIncluded',False)})
    for entry in data['templates']:
        add(entry)
        for item in entry.get('additionalDemos',[]):add(item,'additional-demo')
    for entry in data.get('previews',[]):add(entry,'preview-only')
    return {'format':'mason.motiontemplates-index/1','source':SOURCE,
            'retrievedAt':datetime.now(timezone.utc).isoformat(),
            'declaredCounts':{k:data.get('listing',{}).get(k) for k in ('templateCount','previewCount','demoCount')},'entries':rows}

def refresh(path):
    request=urllib.request.Request(SOURCE,headers={'User-Agent':'Mason-OPC-Motion-Catalog/1'})
    with urllib.request.urlopen(request,timeout=15) as response:
        if response.geturl()!=SOURCE:raise ValueError('Unexpected redirect')
        raw=response.read(4000001)
    if len(raw)>4000000:raise ValueError('Catalog exceeds size limit')
    data=normalize(json.loads(raw))
    path.parent.mkdir(parents=True,exist_ok=True)
    fd,tmp=tempfile.mkstemp(prefix='.catalog-',dir=path.parent)
    try:
        with os.fdopen(fd,'w',encoding='utf-8') as out:json.dump(data,out,ensure_ascii=False,indent=2)
        os.replace(tmp,path)
    finally:
        if os.path.exists(tmp):os.unlink(tmp)
    return data

def main():
    cfg=os.environ.get('MASON_MOTION_CONFIG');state=Path(cfg).expanduser().parent if cfg else Path.home()/'.local/share/mason-opc-motion-video'
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--refresh',action='store_true');p.add_argument('--cache',type=Path,default=state/'website-catalog.json');p.add_argument('--layout',choices=['all','portrait','landscape'],default='all');p.add_argument('--summary',action='store_true');p.add_argument('--html',type=Path,help='write a browseable catalog to a new file');a=p.parse_args()
    error=None
    if a.refresh:
        try:data=refresh(a.cache);origin='live'
        except Exception as e:
            error=type(e).__name__
            try:
                data=json.loads(a.cache.read_text(encoding='utf-8'))
                if not isinstance(data['entries'],list):raise ValueError('Invalid cache')
                origin='cached-fallback'
            except (OSError,ValueError,KeyError):data=json.loads(SNAPSHOT.read_text(encoding='utf-8'));origin='bundled-fallback'
    elif a.cache.is_file():
        try:
            data=json.loads(a.cache.read_text(encoding='utf-8'))
            if not isinstance(data['entries'],list):raise ValueError('Invalid cache')
            origin='cache'
        except (OSError,ValueError,KeyError):data=json.loads(SNAPSHOT.read_text(encoding='utf-8'));origin='bundled-fallback';error='InvalidCache'
    else:data=json.loads(SNAPSHOT.read_text(encoding='utf-8'));origin='bundled-snapshot'
    rows=data['entries'] if a.layout=='all' else [r for r in data['entries'] if r.get('orientation')==a.layout]
    result={'origin':origin,'retrievedAt':data.get('retrievedAt'),'source':data.get('source'),'declaredCounts':data.get('declaredCounts'),'matched':len(rows),'refreshError':error,'statusNote':'Catalog metadata is not an installed .motion package; availability must be checked at the official page.'}
    if a.html:
        def safe(u):return u if isinstance(u,str) and u.startswith('https://') else ''
        cards=[]
        for r in rows:
            esc=lambda value:html.escape(str(value or ''),quote=True)
            site=esc(safe(r.get('website')));demo=esc(safe(r.get('demo')));pic=esc(safe(r.get('preview')))
            title=esc(r.get('title'));orientation=esc(r.get('orientation'));identity=esc(r.get('id'));status=esc(r.get('availability'))
            img=f'<img loading="lazy" src="{pic}" alt="">' if pic else ''
            links=(f'<a href="{site}">官网模板</a> ' if site else '')+(f'<a href="{demo}">观看 Demo</a>' if demo else '')
            for language,url in (r.get('directDownloadUrls') or {}).items():
                link=esc(safe(url))
                if link:links+=f' <a href="{link}">公开包 {esc(language)}</a>'
            cards.append(f'<article data-layout="{orientation}"><div class="thumb">{img}</div><h2>{title}</h2><p>#{identity} · {orientation} · {status}</p><p>{links}</p></article>')
        body='\n'.join(cards)
        doc='''<!doctype html><html lang="zh-CN"><meta charset="utf-8"><title>MotionTemplates 完整选型</title><style>body{font:16px system-ui;background:#f4f5f8;color:#20222a;margin:0}header{padding:30px 5%;background:#18233d;color:white}main{padding:24px 5%}input,select{padding:10px;font-size:16px}#list{display:grid;grid-template-columns:repeat(auto-fill,minmax(240px,1fr));gap:16px;margin-top:20px}article{background:white;border-radius:12px;padding:12px}h2{font-size:17px}.thumb{height:140px;background:#e7e9ef;overflow:hidden}.thumb img{width:100%;height:100%;object-fit:contain}a{color:#2255aa}p{font-size:13px;color:#596371}</style><header><h1>MotionTemplates 网站模板</h1><div>公开目录 · 个人包需由用户本人领取与验签</div></header><main><p>目录来源：'''+html.escape(str(data.get('retrievedAt','')))+'''；目录信息并不代表已经安装。最新领取状态请打开官网核对。</p><input id="q" placeholder="搜索名称或编号"><select id="layout"><option value="all">全部画幅</option><option value="portrait">竖屏</option><option value="landscape">横屏</option></select><div id="count"></div><div id="list">'''+body+'''</div></main><script>const q=document.querySelector('#q'),s=document.querySelector('#layout'),cards=[...document.querySelectorAll('article')];function draw(){let n=0;for(const c of cards){const ok=c.textContent.toLowerCase().includes(q.value.toLowerCase())&&(s.value==='all'||c.dataset.layout===s.value);c.hidden=!ok;if(ok)n++}document.querySelector('#count').textContent='显示 '+n+' 项'}q.addEventListener('input',draw);s.addEventListener('change',draw);draw()</script></html>'''
        with a.html.open('x',encoding='utf-8') as out:out.write(doc)
        result['html']=str(a.html)
    if not a.summary:result['entries']=rows
    print(json.dumps(result,ensure_ascii=False,indent=2))

if __name__=='__main__':main()
