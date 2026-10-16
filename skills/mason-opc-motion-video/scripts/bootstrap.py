#!/usr/bin/env python3
"""Fetch the complete public bundle after skill-only installation."""
import argparse
from datetime import datetime,timezone
from pathlib import Path
import subprocess
import sys
import tempfile

REPOSITORY='https://github.com/masonmosen/mason-opc-motion-video.git'

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--dest',type=Path,default=Path.home()/'.agents/skills')
    parser.add_argument('--host',choices=['codex','hermes','claude','generic'],default='codex')
    parser.add_argument('--state-dir',type=Path,default=Path.home()/'.local/share/mason-opc-motion-video')
    parser.add_argument('--adu-root',type=Path)
    parser.add_argument('--ffmpeg-bin',type=Path)
    parser.add_argument('--host-root',type=Path)
    parser.add_argument('--source-only',action='store_true')
    args=parser.parse_args()
    downloads=args.state_dir.expanduser().absolute()/'downloads'
    downloads.mkdir(parents=True,exist_ok=True)
    location=Path(tempfile.mkdtemp(prefix='public-bundle-',dir=downloads))/'repository'
    # No shell interpolation, credentials, account switching or destructive reset.
    subprocess.run(['git','clone','--depth','1',REPOSITORY,str(location)],check=True)
    command=[sys.executable,str(location/'install.py'),'--dest',str(args.dest.expanduser()),'--host',args.host,'--state-dir',str(args.state_dir.expanduser())]
    for name in ['adu_root','ffmpeg_bin','host_root']:
        value=getattr(args,name)
        if value:command+=['--'+name.replace('_','-'),str(value.expanduser())]
    if args.source_only:command.append('--source-only')
    subprocess.run(command,check=True)
    print('Complete source retained at '+str(location))

if __name__=='__main__':
    try:main()
    except (OSError,subprocess.CalledProcessError) as error:
        raise SystemExit('Bootstrap incomplete: '+str(error))
