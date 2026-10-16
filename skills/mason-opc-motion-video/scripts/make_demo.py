#!/usr/bin/env python3
"""Generate an original synthetic input, never a real person's image or voice."""
import argparse,hashlib,json,subprocess,sys
from pathlib import Path
from motion import ROOT,runtime

def generate(out):
    from PIL import Image,ImageDraw
    adu,_,_=runtime();sys.path.insert(0,str(adu/'scripts'))
    from color_management import export_plan
    if out.exists() or out.is_symlink():raise ValueError('Use a new output directory')
    if not out.parent.is_dir():raise ValueError('Create the intended parent first')
    out.mkdir()
    image=Image.new('RGB',(540,960),'#dfe8f2');d=ImageDraw.Draw(image)
    # Measured full head fits x115 y135 w310 h425. All artwork is original geometry.
    d.rounded_rectangle((60,590,480,1060),80,fill='#2462ea')
    d.rectangle((220,470,320,620),fill='#e9b7a4')
    d.ellipse((130,150,410,535),fill='#19304b')
    d.ellipse((140,225,400,545),fill='#edc2ad')
    d.ellipse((122,335,162,420),fill='#edc2ad');d.ellipse((378,335,418,420),fill='#edc2ad')
    d.pieslice((130,150,410,390),180,355,fill='#19304b')
    d.ellipse((205,340,221,354),fill='#19304b');d.ellipse((320,340,336,354),fill='#19304b')
    d.arc((225,383,314,448),0,180,fill='#9d5d59',width=5)
    image.save(out/'synthetic-presenter.png')
    subprocess.run(['ffmpeg','-v','error','-loop','1','-framerate','25','-i',str(out/'synthetic-presenter.png'),'-f','lavfi','-i','sine=frequency=440:sample_rate=48000',
        '-t','12','-vf',export_plan()['filter'],
        '-af','volume=0.08,afade=t=in:d=0.2,afade=t=out:st=11.5:d=0.5','-c:v','libx264','-crf','20','-preset','fast',
        '-color_primaries','bt709','-color_trc','bt709','-colorspace','bt709','-color_range','tv','-x264-params','colorprim=bt709:transfer=bt709:colormatrix=bt709',
        '-c:a','aac','-ar','48000','-ac','2','-movflags','+faststart',str(out/'source.mp4')],check=True)
    episode=json.loads((ROOT/'assets/demo-episode.json').read_text(encoding='utf-8'))
    episode['presenter']['sourceSha256']=hashlib.sha256((out/'source.mp4').read_bytes()).hexdigest()
    (out/'episode.json').write_text(json.dumps(episode,ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps(dict(input=str(out/'source.mp4'),episode=str(out/'episode.json'),synthetic=True,realVoice=False)))

def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--out',type=Path,required=True);parser.add_argument('--runtime-child',action='store_true',help=argparse.SUPPRESS);args=parser.parse_args()
    if args.runtime_child:generate(args.out.absolute());return
    _,python,env=runtime()
    subprocess.run([str(python),str(Path(__file__).resolve()),'--out',str(args.out.absolute()),'--runtime-child'],env=env,check=True)

if __name__=='__main__':
    try:main()
    except (ValueError,OSError,subprocess.CalledProcessError) as error:raise SystemExit('Demo incomplete: '+str(error))
