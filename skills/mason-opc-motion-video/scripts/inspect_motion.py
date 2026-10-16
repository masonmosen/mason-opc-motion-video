"""Inspect an untrusted .motion ZIP without running it or printing secrets."""
from pathlib import Path,PurePosixPath
import hashlib,json,os,re,shutil,stat,zipfile


def inspect(source,save_private=False):
    source=source.expanduser().resolve()
    if not zipfile.is_zipfile(source):raise ValueError('This file is not a ZIP-compatible .motion package; inspect its publisher documentation without executing unknown files')
    with zipfile.ZipFile(source) as z:
        items=z.infolist();total=sum(i.file_size for i in items)
        if total>2_000_000_000:raise ValueError('Expanded archive needs manual size review')
        for i in items:
            p=PurePosixPath(i.filename)
            if p.is_absolute() or '..' in p.parts or '\\' in i.filename or re.match(r'^[A-Za-z]:',i.filename):raise ValueError('Unsafe archive member path')
            if stat.S_ISLNK(i.external_attr>>16):raise ValueError('Archive links need publisher review')
        safe={}
        for filename in ['manifest.json','motion.json','package.json']:
            hit=next((i for i in items if i.filename==filename and i.file_size<262144),None)
            if hit:
                try:d=json.loads(z.read(hit))
                except (ValueError,UnicodeError):continue
                # Do not echo arbitrary name/id strings: a hostile archive can
                # put an embedded key in an otherwise innocently named field.
                for key in ['version','formatVersion']:
                    value=d.get(key)
                    if isinstance(value,(str,int,float)) and re.fullmatch(r'[0-9]{1,4}(?:\.[0-9]{1,4}){0,3}(?:-[A-Za-z0-9.-]{1,30})?',str(value)):safe[key]=value
    digest=hashlib.sha256(source.read_bytes()).hexdigest()
    result=dict(sha256=digest,files=len(items),expandedBytes=total,metadata=safe,executed=False,
        signature='Not verified by this inspector; use the publisher official verifier',
        credentialHandling='Package content was not printed or copied into shared skills')
    if save_private:
        parent=Path.home()/'.local/share/mason-opc-motion-video/private-motion'/digest
        parent.mkdir(parents=True,exist_ok=True,mode=0o700);os.chmod(parent,0o700)
        target=parent/'template.motion'
        if not target.exists():shutil.copyfile(source,target)
        if hashlib.sha256(target.read_bytes()).hexdigest()!=digest:raise ValueError('Private copy byte mismatch')
        os.chmod(target,0o600);result['privatePath']=str(target)
    return result
