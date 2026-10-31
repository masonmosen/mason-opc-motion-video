#!/usr/bin/env python3
"""Portable Mason OPC entrypoint. No keys, account state or machine paths."""
import argparse
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]


def runtime():
    config = Path(os.environ.get('MASON_MOTION_CONFIG', str(Path.home()/'.local/share/mason-opc-motion-video/runtime.json'))).expanduser()
    values = json.loads(config.read_text()) if config.is_file() else {}
    supplied = os.environ.get('ADU_MOTION_VIDEO_ROOT') or values.get('adu_root')
    adu = Path(supplied).expanduser() if supplied else ROOT.parent/'adu-motion-video'
    if not (adu/'scripts/pipeline.py').is_file():
        raise ValueError('Full adu-motion-video dependency missing. Read references/install.md and install the complete family.')
    python = adu/('.venv/Scripts/python.exe' if os.name=='nt' else '.venv/bin/python')
    if not python.is_file():
        raise ValueError('Dependency source exists but its isolated Python environment is missing. Complete setup; do not report installation ready.')
    env = os.environ.copy()
    ffb = env.get('MASON_FFMPEG_BIN') or values.get('ffmpeg_bin')
    if not ffb:
        preferred = Path.home()/'.local/share/adu-motion-video/runtime/ffmpeg-9.0.2/bin'
        if (preferred/('ffmpeg.exe' if os.name=='nt' else 'ffmpeg')).is_file(): ffb = str(preferred)
    if ffb: env['PATH'] = str(Path(ffb).expanduser())+os.pathsep+env.get('PATH','')
    env.update(ADU_MOTION_VIDEO_ROOT=str(adu), ADU_PYTHON=str(python), PYTHONUTF8='1', PYTHONIOENCODING='utf-8')
    return adu.resolve(), python, env


def call(args, env=None):
    result = subprocess.run([str(a) for a in args], env=env)
    if result.returncode: raise SystemExit(result.returncode)


def catalog(adu, layout):
    sys.path.insert(0, str(adu/'scripts'))
    from pack_catalog import resolve
    data=json.loads((adu/'references/template-catalog.json').read_text(encoding='utf-8'))
    rows=[]
    for group in data['templates']:
        for style in group['styles']:
            selection=style.get('portraitSelection') if layout=='portrait' else style.get('selection')
            if layout not in style.get('layouts', {'landscape':{}}):continue
            pack=resolve(selection,adu/'packs')
            manifest=json.loads((pack/'manifest.json').read_text(encoding='utf-8'))
            rows.append(dict(id=style['id'],title=style['title'],family=group['title'],selection=selection,
                units=len(manifest['scenes']),packDirectory=pack.relative_to(adu).as_posix(),
                demo=style.get('portraitDemo') if layout=='portrait' and style.get('portraitDemo') else style.get('demo'),
                requires=style.get('requires',[]),status=manifest.get('status','experimental'),
                masonAcceptance='v03 episode derivative adopted, not unchanged full-group acceptance' if style['id']=='01-B' else 'not established by Mason v03 approval'))
    print(json.dumps(dict(layout=layout,styles=len(rows),groups=sum(r['units'] for r in rows),options=rows),ensure_ascii=False,indent=2))


def main():
    p=argparse.ArgumentParser(description=__doc__)
    s=p.add_subparsers(dest='cmd',required=True)
    s.add_parser('doctor')
    c=s.add_parser('catalog');c.add_argument('--layout',choices=['portrait','landscape'],default='portrait')
    w=s.add_parser('web-catalog');w.add_argument('--layout',choices=['all','portrait','landscape'],default='all');w.add_argument('--refresh',action='store_true');w.add_argument('--summary',action='store_true');w.add_argument('--html')
    v=s.add_parser('prepare-v03');v.add_argument('--input',required=True);v.add_argument('--episode',required=True);v.add_argument('--out',required=True)
    a=s.add_parser('audio');a.add_argument('project')
    q=s.add_parser('qa-v03');q.add_argument('project');q.add_argument('--out',required=True)
    n=s.add_parser('pipeline');n.add_argument('args',nargs=argparse.REMAINDER)
    m=s.add_parser('inspect-motion');m.add_argument('file');m.add_argument('--save-private',action='store_true')
    args=p.parse_args()
    if args.cmd=='web-catalog':
        command=[sys.executable,ROOT/'scripts/website_catalog.py','--layout',args.layout]
        if args.refresh:command.append('--refresh')
        if args.summary:command.append('--summary')
        if args.html:command.extend(['--html',args.html])
        call(command);return
    if args.cmd=='inspect-motion':
        from inspect_motion import inspect
        print(json.dumps(inspect(Path(args.file),args.save_private),ensure_ascii=False,indent=2));return
    adu,python,env=runtime()
    if args.cmd=='catalog':catalog(adu,args.layout)
    elif args.cmd=='doctor':
        print('Mason skill: '+str(ROOT),flush=True)
        call([python,adu/'scripts/pipeline.py','doctor'],env)
    elif args.cmd=='prepare-v03':
        call([python,ROOT/'scripts/prepare_v03.py','--adu',adu,'--input',args.input,'--episode',args.episode,'--out',args.out],env)
    elif args.cmd=='audio':
        project=Path(args.project).resolve()
        call([python,project/'audio.py'],env)
        call([python,adu/'scripts/pipeline.py','mix',project,'0.52'],env)
    elif args.cmd=='qa-v03':
        call(['node',ROOT/'scripts/qa_v03.mjs','--adu',adu,'--project',Path(args.project).resolve(),'--out',Path(args.out).resolve()],env)
    elif args.cmd=='pipeline':
        if not args.args:raise ValueError('Supply an Adu pipeline command, such as auto-capabilities, macro-plan, render or preview')
        call([python,adu/'scripts/pipeline.py',*args.args],env)


if __name__=='__main__':
    try:main()
    except (ValueError,OSError,json.JSONDecodeError) as e:raise SystemExit('Mason motion: '+str(e))
