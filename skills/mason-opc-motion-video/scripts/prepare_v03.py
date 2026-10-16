#!/usr/bin/env python3
"""Build a fresh editable derivative from the accepted v03 source recipe."""
import argparse,hashlib,json,os,shutil,subprocess,sys
from pathlib import Path
from fractions import Fraction


def main():
    p=argparse.ArgumentParser(description=__doc__)
    for key in ['adu','input','episode','out']:p.add_argument('--'+key,type=Path,required=True)
    a=p.parse_args();root=Path(__file__).resolve().parents[1];adu=a.adu.resolve();out=a.out.absolute();source=a.input.resolve()
    if out.exists() or out.is_symlink():raise ValueError('Use a new output directory; existing work is never overwritten')
    if not out.parent.is_dir():raise ValueError('Create the intended project parent first')
    if not source.is_file():raise ValueError('Input video missing')
    e=json.loads(a.episode.read_text(encoding='utf-8'))
    if e.get('schema')!='mason-opc-motion-episode/1':raise ValueError('Unsupported episode schema')
    if e.get('mode') not in ['accepted-reference','reviewed-variant']:raise ValueError('Declare accepted-reference or reviewed-variant; author and review new narration semantics first')
    points=e.get('timeMap',[])
    if len(points)<2 or points[0]!=[0,0] or any(len(x)!=2 for x in points):raise ValueError('timeMap needs [baseVisualSeconds, actualOutputSeconds] points beginning [0,0]')
    if any(points[i][0]<=points[i-1][0] or points[i][1]<=points[i-1][1] for i in range(1,len(points))):raise ValueError('Both clocks must be strictly increasing')
    if abs(points[-1][0]-2434/60)>.001:raise ValueError('V03 visual map must cover its complete base ending')
    if len(e.get('roles',[]))!=4:raise ValueError('This derivative has four role objects; for another count author and validate a new variant')
    head=e.get('presenter',{}).get('headBox')
    if not isinstance(head,dict) or any(not isinstance(head.get(k),(float,int)) for k in ['x','y','w','h']) or min(head['w'],head['h'])<=0:raise ValueError('Measure and supply a full hair/ears/chin headBox for this actual input')
    sys.path.insert(0,str(adu/'scripts'))
    from color_management import image_plan,fingerprint_file,validate_review_evidence
    from import_talk import input_timing
    from pack_catalog import resolve
    from font_policy import install as fonts
    identity=fingerprint_file(source)
    if e['presenter'].get('sourceSha256')!=identity['sha256']:
        raise ValueError('Head framing belongs to another source: measure this input and bind presenter.sourceSha256; never inherit Mason headBox blindly')
    if e['mode']=='accepted-reference' and e.get('referenceSourceSha256')!=identity['sha256']:
        raise ValueError('Accepted-reference mode only applies to its exact supplied source; author a reviewed-variant for new narration')
    if not isinstance(e.get('contentEvidence'),str) or not e['contentEvidence'].strip():
        raise ValueError('Record the actual narration/semantic evidence for this episode')
    probe=json.loads(subprocess.check_output(['ffprobe','-v','error','-show_streams','-show_format','-of','json',str(source)]))
    video=next(s for s in probe['streams'] if s['codec_type']=='video');timing=input_timing(probe,60)
    fps=float(Fraction(video.get('avg_frame_rate','25/1')))
    if not .1<fps<=120:raise ValueError('Source frame rate needs inspection')
    # The adopted clip has a 22.969ms container video offset, less than one
    # native 25fps frame. Rebase that native grid explicitly, never the voice.
    # Larger offsets need a newly aligned source rather than frozen padding.
    if timing['videoStartSeconds']>1/min(60,fps)+.00001:raise ValueError('Video begins more than one native/output frame late; provide an aligned source')
    duration=round(timing['videoStreamDurationSeconds']*60)/60
    timing.update(frames=round(duration*60),duration=duration,
                  preparedVideoStartSeconds=0,videoGridAlignmentShiftSeconds=-timing['videoStartSeconds'],
                  frameResampling='native frame grid rebased within one native frame; nearest sampling on the output clock; voice unchanged')
    if abs(points[-1][1]-duration)>1/60+.001:raise ValueError('Episode actual clock does not match the supplied video. Align the new narration; do not silently stretch the old timeline')
    width,height=video['width'],video['height']
    if head['x']<0 or head['y']<0 or head['x']+head['w']>width or head['y']+head['h']>height:raise ValueError('Full-head safe rectangle exceeds actual source dimensions')
    color=image_plan(source)
    if color['reviewSignals']:
        validate_review_evidence(color,e.get('colorReview'));color['reviewEvidence']=e['colorReview']
    subs=e.get('subtitles',[])
    if not subs or any(not(0<=s['t0']<s['t1']<=duration+.05) or not s.get('zh') for s in subs):raise ValueError('Supply real-clock captions aligned to the actual voice')
    out.mkdir();assets=root/'assets/v03-template'
    for f in assets.iterdir():
        if f.is_file():shutil.copy2(f,out/f.name)
    for name in ['assets','sc','stills','talk/native']:(out/name).mkdir(parents=True,exist_ok=True)
    seq=out/'talk/native'
    subprocess.run(['ffmpeg','-v','error','-i',str(source),'-map','0:v:0','-vf',f'setpts=PTS-STARTPTS,fps={fps}:start_time=0,'+color['filter'],'-q:v','2',str(seq/'f_%05d.jpg')],check=True)
    count=len(list(seq.glob('f_*.jpg')))
    if count<1:raise ValueError('No input frames extracted')
    subprocess.run(['ffmpeg','-v','error','-i',str(source),'-map','0:a:0','-vn','-af',f'aresample=48000:first_pts=0,apad,atrim=duration={duration}','-ar','48000','-ac','2','-c:a','pcm_s16le',str(out/'voice.wav')],check=True)
    pack=resolve('continuous-performance@1.1.1-candidate',adu/'packs');manifest=json.loads((pack/'manifest.json').read_text(encoding='utf-8'))
    css,_=fonts(manifest,{'fontPolicy':'preferred'},a.episode.parent,out)
    (out/'fonts.css').write_text(css,encoding='utf-8')
    e['duration']=duration;e['sourceWidth']=width;e['sourceHeight']=height;e['sourceFps']=fps;e['sourceFrames']=count
    (out/'episode.json').write_text(json.dumps(e,ensure_ascii=False,indent=2),encoding='utf-8')
    (out/'episode_bindings.js').write_text('window.EPISODE='+json.dumps(e,ensure_ascii=False)+';\n',encoding='utf-8')
    config=dict(brand=e['profile']['brand'],account=e['profile']['creator'],fps=60,width=1080,height=1920,end=duration,subtitles=True,talkFrames=timing['frames'],
                nativeFps=fps,nativeFrames=count,sourceWidth=width,sourceHeight=height,race=dict(labels=['開場','演示','收束'],keys=[0,duration*.35,duration*.78,duration]))
    (out/'config.js').write_text('window.CONFIG='+json.dumps(config,ensure_ascii=False)+';\n',encoding='utf-8')
    (out/'subs.js').write_text('const SUBS='+json.dumps(subs,ensure_ascii=False)+';\n',encoding='utf-8')
    (out/'macro_plan.json').write_text(json.dumps(dict(schema='mason-opc-motion-v03-derivative/1',fps=60,width=1080,height=1920,end_frame=timing['frames'],durationSeconds=duration,
        pack='continuous-performance',version='1.1.1-candidate',sourceCommit='31a03c36b5f510303305f9e931c448b75baa52d5',
        method='episode derivative, not protected native groups',narrationRetimed=False,visualTimeMap=points,scenes=[]),ensure_ascii=False,indent=2),encoding='utf-8')
    imported=dict(source=source.name,fps=60,**timing,color=color,frame_width=width,frame_height=height,actualPreparedFps=fps,actualPreparedFrames=count)
    (out/'import.json').write_text(json.dumps(imported,ensure_ascii=False,indent=2),encoding='utf-8')
    (out/'INPUT_IDENTITY.json').write_text(json.dumps(dict(filename=source.name,**fingerprint_file(source),voiceClock='actual output, unretimed'),indent=2),encoding='utf-8')
    subprocess.run(['node',str(root/'scripts/qa_v03.mjs'),'--adu',str(adu),'--project',str(out),'--out',str(out/'stills/preflight'),'--bind-sfx'],check=True)
    print(json.dumps(dict(project=str(out),frames=timing['frames'],duration=duration,nativeFps=fps,nativeFrames=count,next='motion.py audio PROJECT; then QA, render, check and preview'),ensure_ascii=False))


if __name__=='__main__':
    try:main()
    except (ValueError,OSError,KeyError) as e:raise SystemExit('V03 prepare: '+str(e))
