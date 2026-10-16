#!/usr/bin/env python3
"""Install this complete portable bundle without replacing personal edits."""
import argparse,hashlib,json,os,platform,shutil,stat,subprocess,sys,tempfile
from pathlib import Path
from datetime import datetime,timezone

ROOT=Path(__file__).resolve().parent
NAME='mason-opc-motion-video'

def digest(path):
    h=hashlib.sha256()
    with path.open('rb') as f:
        for b in iter(lambda:f.read(1024*1024),b''):h.update(b)
    return h.hexdigest()

def files(root):
    result={}
    for p in root.rglob('*'):
        if '.git' in p.relative_to(root).parts or '__pycache__' in p.parts or p.name=='.DS_Store':continue
        if p.is_symlink():raise ValueError('Portable bundle must not contain symlinks: '+str(p))
        if p.is_file():result[p.relative_to(root).as_posix()]=p
    return result

def verify():
    record=json.loads((ROOT/'package_manifest.json').read_text(encoding='utf-8'))
    actual=files(ROOT);actual.pop('package_manifest.json',None)
    expected=record['files']
    if set(actual)!=set(expected):raise ValueError('Bundle is incomplete or has unexpected files; transfer the whole folder and keep local output outside it')
    for relative,p in actual.items():
        if digest(p)!=expected[relative]['sha256'] or p.stat().st_size!=expected[relative]['bytes']:raise ValueError('Bundle file changed: '+relative)
    return record

def compatible(source,target,adu=False):
    if not target.is_dir():return False
    for relative,p in files(source).items():
        q=target/relative
        if not q.is_file():return False
        if digest(q)!=digest(p):
            # Preserve the already verified upstream text plus an appended local
            # launcher note; never accept changes to template/runtime sources.
            if not(adu and relative=='SKILL.md' and q.read_bytes().startswith(p.read_bytes())):return False
    return True

def publish(source,target):
    if target.exists() or target.is_symlink():raise ValueError('Refusing existing destination: '+str(target))
    target.parent.mkdir(parents=True,exist_ok=True)
    temp=Path(tempfile.mkdtemp(prefix='.'+target.name+'-',dir=target.parent))
    try:
        shutil.copytree(source,temp/'content')
        if target.exists() or target.is_symlink():raise ValueError('Destination appeared during install')
        (temp/'content').rename(target)
    finally:shutil.rmtree(temp,ignore_errors=True)

def version_python(candidate):
    try:
        p=subprocess.run([str(candidate),'-c','import sys;print("%d.%d"%sys.version_info[:2])'],capture_output=True,text=True,timeout=10)
        if p.returncode==0 and tuple(map(int,p.stdout.strip().split('.'))) >= (3,12):return str(candidate)
    except (OSError,ValueError,subprocess.TimeoutExpired):pass
    return None

def setup(adu,env):
    python=adu/('.venv/Scripts/python.exe' if os.name=='nt' else '.venv/bin/python')
    if not python.is_file():
        candidates=[sys.executable]+[shutil.which(n) for n in ['python3.14','python3.13','python3.12','python3','python']]
        selected=next((version_python(x) for x in candidates if x and version_python(x)),None)
        if not selected:raise ValueError('Python 3.12+ missing (validated on 3.14). Agent: complete references/install.md, then rerun. Source copy is not runtime completion.')
        subprocess.run([selected,'-m','venv',str(adu/'.venv')],check=True)
    if not version_python(python):raise ValueError('Existing dependency venv is below Python 3.12; preserve it and use an isolated supported runtime')
    def doctor():return subprocess.run([str(python),str(adu/'scripts/pipeline.py'),'doctor'],env=env).returncode
    if doctor()==0:return str(python)
    # Official setup owns npm/Python dependencies. It does not install OS tools.
    subprocess.run([str(python),str(adu/'scripts/pipeline.py'),'setup'],env=env,check=True)
    if doctor()!=0:raise ValueError('Runtime doctor failed; finish the listed missing tools. Do not report full installation.')
    return str(python)

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--dest',type=Path,default=Path.home()/'.agents/skills')
    p.add_argument('--host',choices=['codex','hermes','claude','generic'],default='codex')
    p.add_argument('--host-root',type=Path,help='explicit custom discovery directory, e.g. isolated validation')
    p.add_argument('--state-dir',type=Path,default=Path.home()/'.local/share/mason-opc-motion-video')
    p.add_argument('--adu-root',type=Path,help='reuse a complete matching existing dependency')
    p.add_argument('--ffmpeg-bin',type=Path)
    p.add_argument('--verify-only',action='store_true')
    p.add_argument('--source-only',action='store_true',help='explicit incomplete-runtime installation for offline intake')
    a=p.parse_args();record=verify()
    if a.verify_only:print(json.dumps(dict(bundle='verified',version=record['version'],files=len(record['files'])),ensure_ascii=False));return
    dest=a.dest.expanduser().absolute();state=a.state_dir.expanduser().absolute()
    source=ROOT/'skills'/NAME;target=dest/NAME
    if target.is_symlink():
        if not compatible(source,target.resolve()):raise ValueError('Existing skill link differs; preserve personal edits and compare versions')
    elif target.exists():
        if not compatible(source,target):raise ValueError('Existing skill differs; preserve personal edits and compare versions instead of overwriting')
    else:publish(source,target)
    dep=ROOT/'dependencies/adu-motion-video';adu=(a.adu_root.expanduser().absolute() if a.adu_root else dest/'adu-motion-video')
    if adu.exists():
        if not compatible(dep,adu,True):
            if a.adu_root:raise ValueError('Specified Adu source is incomplete or different from the pinned family')
            adu=state/'dependencies'/record['adu']['commit']/'adu-motion-video'
            if adu.exists() and not compatible(dep,adu,True):raise ValueError('Isolated dependency differs; inspect without overwriting')
            if not adu.exists():publish(dep,adu)
    else:publish(dep,adu)
    env=os.environ.copy();ffb=a.ffmpeg_bin
    if not ffb:
        candidate=Path.home()/'.local/share/adu-motion-video/runtime/ffmpeg-9.0.2/bin'
        if (candidate/('ffmpeg.exe' if os.name=='nt' else 'ffmpeg')).is_file():ffb=candidate
    if ffb:env['PATH']=str(ffb.expanduser())+os.pathsep+env.get('PATH','')
    state.mkdir(parents=True,exist_ok=True)
    config=state/'runtime.json';config.write_text(json.dumps(dict(adu_root=str(adu),ffmpeg_bin=str(ffb.expanduser()) if ffb else None),indent=2),encoding='utf-8')
    host_path=None;host_mode=None
    if a.host in ['hermes','claude']:
        host_root=a.host_root.expanduser().absolute() if a.host_root else Path.home()/('.hermes/skills' if a.host=='hermes' else '.claude/skills')
        host_root.mkdir(parents=True,exist_ok=True);alias=host_root/NAME
        if alias.exists() or alias.is_symlink():
            if alias.resolve()!=target.resolve():raise ValueError('Host discovery path is already occupied: '+str(alias))
            host_mode='same-source-existing'
        else:
            try:alias.symlink_to(target,target_is_directory=True);host_mode='same-source-link'
            except OSError:
                # Windows may deny directory links. The receipt declares a
                # frozen copy; later upgrades must compare it explicitly.
                publish(source,alias);host_mode='host-frozen-copy'
        host_path=str(alias)
    status='source_installed_runtime_unverified' if a.source_only else 'runtime_doctor_passed'
    python=None if a.source_only else setup(adu,env)
    receipt=dict(version=record['version'],createdAt=datetime.now(timezone.utc).isoformat(),
        skill=str(target),adu=str(adu),runtimeConfig=str(config),python=python,host=a.host,
        hostPath=host_path,hostMode=host_mode,status=status,
        discovery='New chat/reload and native host listing still required',
        production='Run an actual sample; doctor alone is not end-to-end media acceptance',
        credentialsCopied=False,paidCalls=0)
    (state/'install_receipt.json').write_text(json.dumps(receipt,ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps(receipt,ensure_ascii=False,indent=2))

if __name__=='__main__':
    try:main()
    except (ValueError,OSError,subprocess.CalledProcessError) as e:raise SystemExit('Install incomplete: '+str(e))
