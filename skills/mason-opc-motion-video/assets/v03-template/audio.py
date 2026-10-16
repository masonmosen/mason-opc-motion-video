"""Original v03 cue-composed score and spatial SFX; no external service.

The explicitly bound music file is this episode's composition, not the retired
upstream source-score fallback. Voice is the unretimed text-free-source audio.
"""
from pathlib import Path
import hashlib,json,math,wave
import numpy as np

P=Path(__file__).resolve().parent
E=json.loads((P/'episode.json').read_text(encoding='utf-8'))
SR=48000;DUR=E['duration'];N=round(SR*DUR)
def mapping(value,axis):
    points=E['timeMap']
    i=1
    while i<len(points)-1 and value>points[i][axis]:i+=1
    a,b=points[i-1],points[i];q=max(0,min(1,(value-a[axis])/(b[axis]-a[axis])))
    return a[1-axis]+(b[1-axis]-a[1-axis])*q
def visual_time(t):return mapping(t,1)
def output_time(t):return mapping(t,0)
rng=np.random.default_rng(131003)
score=np.zeros((N,2),np.float64)
fx=np.zeros_like(score)

def pan(signal,p=0):
    # Constant-power pan: narration remains independent and centered.
    return np.column_stack((signal*np.sqrt((1-p)/2),signal*np.sqrt((1+p)/2)))

def add(dest,signal,at,gain=1,p=0):
    a=round(at*SR);source=0
    if a<0:source=-a;a=0
    count=min(len(signal)-source,N-a)
    if count<=0:return
    signal=signal[source:source+count]
    if signal.ndim==1:signal=pan(signal,p)
    dest[a:a+count]+=signal*gain

def ts(d):return np.arange(round(d*SR),dtype=np.float64)/SR
def hz(m):return 440*2**((m-69)/12)
def env(t,d,attack=.008,release=.09):
    return np.minimum(1,t/max(attack,.0001))*np.minimum(1,np.maximum(0,(d-t))/max(release,.0001))
def tone(m,d=.3,style='pluck'):
    t=ts(d);freq=hz(m)
    if style=='bass':
        a=np.sin(2*np.pi*freq*t)+.20*np.sin(2*np.pi*freq*2*t)+.08*np.sin(2*np.pi*freq*3*t)
        return a*np.exp(-t*4)*env(t,d,.008,.06)
    if style=='pad':
        a=(np.sin(2*np.pi*freq*t)+.22*np.sin(2*np.pi*freq*2.003*t))*.6
        return a*env(t,d,.18,.5)
    a=np.sin(2*np.pi*freq*t)+.22*np.sin(2*np.pi*freq*2.01*t)+.12*np.sin(2*np.pi*freq*3.99*t)
    return a*np.exp(-t*9)*env(t,d,.004,.1)
def noise(d):
    a=rng.normal(0,1,round(d*SR));return a/4
def bright(d):
    a=noise(d);return np.concatenate(([0],np.diff(a)))
def kick(d=.32):
    t=ts(d);phase=2*np.pi*(47*t+95*.024*(1-np.exp(-t/.024)))
    return np.sin(phase)*np.exp(-t*15)+bright(d)*np.exp(-t*150)*.15
def snare(d=.18):
    t=ts(d);return (bright(d)*np.exp(-t*24)*.55+np.sin(2*np.pi*183*t)*np.exp(-t*32)*.25)*env(t,d,.001,.03)
def hat(d=.055):
    t=ts(d);return bright(d)*np.exp(-t*65)*env(t,d,.001,.01)

# One D-minor theme, arranged as intro, sparse pain break, build, three textures,
# collaboration drive, creator return and a resolving sting. No full-song loop.
BPM=E.get('music',{}).get('bpm',144);beat=60/BPM
progression=[(38,[62,65,69,72]),(34,[58,62,65,69]),(41,[65,69,72,76]),(36,[60,64,67,70])]
motif=[74,77,81,79,77,72,74,69]
def energy(t):
    t=visual_time(t)
    if t<2.62:return .38
    if t<5.18:return .60
    if t<5.41:return .12
    if t<7.68:return .90
    if t<12.01:return .42
    if t<13.15:return .68
    if t<13.29:return .04
    if t<14.11:return .86
    if t<19.17:return .67
    if t<23.27:return .54
    if t<29.06:return .82
    if t<31.48:return .95
    if t<34.2:return .62
    if t<36.38:return .94
    return .60

for bar in range(math.ceil(DUR/(beat*4))):
    at=bar*beat*4
    root,chord=progression[bar%4]
    for k,note in enumerate(chord):
        add(score,tone(note,beat*4+.15,'pad'),at,.095*energy(at),p=(-.7+k*.45))
    for step in range(8):
        pos=at+step*beat/2
        if pos>=DUR:break
        e=energy(pos)
        if step in [0,3,4,6]:add(score,tone(root+(12 if step==3 else 0),beat*.44,'bass'),pos,.36*e)
        add(score,tone(motif[(step+bar*2)%8],.31),pos,.065*e,p=(-.5 if step%2 else .5))
        # Alternating eighth hats, with sparse syncopation through pain points.
        if not (7.68<visual_time(pos)<12.01 and step%2):add(score,hat(),pos,.13*e,p=.35 if step%2 else -.35)
    for b in [0,1.5,2,3.25]:
        pos=at+b*beat
        if not (7.68<visual_time(pos)<12.01):add(score,kick(),pos,.39*energy(pos))
    for b in [1,3]:
        pos=at+b*beat
        add(score,snare(),pos,.22*energy(pos),p=.05)

# Narrow-band rhythmic detail for the swarm, and short stereo pluck delays.
for pos in np.arange(output_time(24.74),output_time(31.3),beat/4):
    add(score,hat(.034),float(pos),.035*energy(pos),p=.55*math.sin(pos*4))
delayed=score.copy()
offset=round(beat*.75*SR)
delayed[offset:,0]+=score[:-offset,1]*.15
delayed[offset:,1]+=score[:-offset,0]*.15
score=delayed
clock=np.arange(N)/SR
duck=np.ones(N)
for time in [5.41,6.92,13.29,14.7,19.17,23.27,24.74,31.48,34.38,39.48]:
    time=output_time(time)
    # Anticipation clears music immediately before semantic impacts.
    duck*=1-.68*np.exp(-((clock-(time-.085))/.055)**2)
score*=duck[:,None]
score*=np.minimum(1,clock/.07)[:,None]
score*=np.minimum(1,np.maximum(0,DUR-clock)/.45)[:,None]
score*=.073/(np.sqrt(np.mean(score*score))+1e-12)

events=json.loads((P/'sfx.json').read_text())
def sound(kind):
    if kind in ['whip','reverse','riser','rewind','data','water']:
        d={'whip':.3,'reverse':.24,'riser':.7,'rewind':.34,'data':.21,'water':.5}[kind];t=ts(d);p=t/d
        a=bright(d)*np.sin(np.pi*p)**1.4
        if kind=='water':a=noise(d)*np.sin(np.pi*p)**1.8*.6+np.sin(2*np.pi*(430*t-240*t*t/d))*np.exp(-t*9)*.35
        else:a+=np.sin(2*np.pi*(150*t+900*t*t/(2*d)))*.22*np.sin(np.pi*p)
        if kind in ['reverse','rewind']:a=a[::-1]
        if kind=='rewind':a*=.5+.5*np.sin(2*np.pi*33*t)
        return a
    if kind in ['impact','bass','power','intro','shatter','fracture']:
        d=.62 if kind in ['power','shatter'] else .36;t=ts(d)
        a=np.sin(2*np.pi*(46*t+36*.035*(1-np.exp(-t/.035))))*np.exp(-t*9)
        a+=bright(d)*np.exp(-t*55)*.4
        if kind in ['shatter','fracture']:
            a+=bright(d)*np.exp(-t*8)*.5
            for n in [84,91,96]:a+=tone(n,d)*.17
        return a
    if kind in ['snap','click','reject','typing','glitch','reset','split']:
        d=.25 if kind in ['reset','glitch','split'] else .09;t=ts(d)
        a=bright(d)*np.exp(-t*70)+np.sin(2*np.pi*740*t)*np.exp(-t*80)*.25
        if kind in ['reset','glitch']:a=(bright(d)*.6+np.sin(2*np.pi*(1400*t-1000*t*t/d))*.22)*(np.sin(t*2*np.pi*38)>.2)*np.exp(-t*9)
        if kind=='reject':a+=np.sin(2*np.pi*135*t)*np.exp(-t*32)*.6
        return a
    if kind=='bounce':
        t=ts(.25);return np.sin(2*np.pi*(240*t-100*t*t))*np.exp(-t*28)+bright(.25)*np.exp(-t*80)*.3
    d=.48;t=ts(d);a=np.zeros(len(t))
    for n,delay in [(77,0),(81,.045),(86,.095)]:
        v=tone(n,d-delay);z=round(delay*SR);a[z:z+len(v)]+=v*.4
    return a

for event in events:
    a=sound(event['type']);a/=max(.4,np.max(np.abs(a)))
    add(fx,a,event['t'],event['g']*1.25,event.get('p',0))

def save(path,a):
    # Clip count is audited separately; never use automatic hard clipping as mix.
    assert np.max(np.abs(a))<.98,(path,np.max(np.abs(a)))
    with wave.open(str(path),'wb') as f:
        f.setnchannels(2);f.setsampwidth(2);f.setframerate(SR)
        f.writeframes(np.round(a*32767).astype('<i2').tobytes())

track=P/'assets/score_original.wav'
save(track,score);save(P/'bgm.wav',score);save(P/'sfx.wav',fx)
binding=dict(mode='track',path='assets/'+track.name,offset=0,
             sha256=hashlib.sha256(track.read_bytes()).hexdigest(),
             origin='Original episode-specific composition by Codex; local synthesis',
             name='Continuous Reaction',bpm=BPM,notRetiredUpstreamFallback=True)
(P/'music_binding.json').write_text(json.dumps(binding,ensure_ascii=False,indent=2))
(P/'audio_design.json').write_text(json.dumps(dict(
    music=binding,duration=DUR,sampleRate=SR,events=len(events),
    soundFamilies=sorted(set(e['type'] for e in events)),
    nonCenteredEvents=sum(abs(e.get('p',0))>.01 for e in events),
    scorePeak=float(np.abs(score).max()),scoreRms=float(np.sqrt(np.mean(score*score))),
    fxPeak=float(np.abs(fx).max()),paidCalls=0,
    voice='Unretimed audio from matching text-free source; original BGM mix excluded'),ensure_ascii=False,indent=2))
print(json.dumps({'music':binding,'sfx':len(events),'peak':float(np.abs(fx).max())},ensure_ascii=False))
