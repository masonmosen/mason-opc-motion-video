import fs from 'node:fs';import path from 'node:path';import {createRequire} from 'node:module';import {pathToFileURL} from 'node:url';
const args=process.argv.slice(2),get=k=>{const i=args.indexOf(k);if(i<0||!args[i+1])throw Error('Missing '+k);return args[i+1];};
const adu=path.resolve(get('--adu')),project=path.resolve(get('--project')),out=path.resolve(get('--out'));
const require=createRequire(path.join(adu,'package.json'));const {chromium}=require('playwright-core');
const {chrome}=await import(pathToFileURL(path.join(adu,'scripts/chrome.mjs')).href);
fs.mkdirSync(out,{recursive:true});
const browser=await chromium.launch({executablePath:chrome(),headless:true,args:['--allow-file-access-from-files','--disable-gpu','--disable-accelerated-2d-canvas','--force-color-profile=srgb']});
try{
 const page=await browser.newPage({viewport:{width:1080,height:1920}}),errors=[];
 await page.route('**/*',route=>['file:','data:','blob:'].includes(new URL(route.request().url()).protocol)?route.continue():route.abort());
 page.on('pageerror',e=>errors.push(e.message));page.on('requestfailed',r=>errors.push(r.failure()?.errorText));
 await page.goto(pathToFileURL(path.join(project,'index.html')).href);await page.evaluate(async()=>{await READY;await imgWait();await Promise.all([...document.images].map(i=>i.decode()));});
 if(args.includes('--bind-sfx')){
  if(errors.length)throw Error(errors.join('\n'));
  fs.writeFileSync(path.join(project,'sfx.json'),JSON.stringify(await page.evaluate(()=>SFX),null,2));
  await page.screenshot({path:path.join(out,'first-frame.png')});console.log(JSON.stringify({sfxBound:true,errors}));
 }else{
  const end=await page.evaluate(()=>END),rows=[];
  const times=new Set(Array.from({length:Math.ceil(end*10)},(_,i)=>Math.min(end-1/60,i/10)));
  const keys=await page.evaluate(()=>V03_ACTOR_KEYS.map(([t,,d])=>[EPISODE.toOutput(t),EPISODE.toOutput(t+d)]));
  for(const [a,b] of keys)for(let x=a;x<=b;x+=1/60)if(x<end)times.add(x);
  for(const t of [...times].sort((a,b)=>a-b)){
   await page.evaluate(async t=>{await renderAt(t);await imgWait();await Promise.all([...document.images].filter(i=>i.src).map(i=>i.decode()));},t);
   rows.push(await page.evaluate(()=>{
    const s=structuredClone(V03_STATE),p=s.presenter,b=p.sourceSafeBox,r=Math.min(p.r,p.w/2,p.h/2),corners=[[b.x,b.y],[b.x+b.w,b.y],[b.x,b.y+b.h],[b.x+b.w,b.y+b.h]].map(([x,y])=>[p.ix+x*p.scale,p.iy+y*p.scale]);
    const headInside=corners.every(([x,y])=>{const xx=Math.max(r,Math.min(p.w-r,x)),yy=Math.max(r,Math.min(p.h-r,y));return x>=4&&x<=p.w-4&&y>=4&&y<=p.h-4&&(x-xx)**2+(y-yy)**2<=(Math.max(0,r-3))**2;});
    const titles=[...document.querySelectorAll('#type>.type')].filter(e=>+e.style.opacity>.5).map(e=>{const r=e.getBoundingClientRect();return{text:e.innerText,x:r.x,y:r.y,w:r.width,h:r.height};});
    return {...s,headInside,overlap:titles.filter(r=>r.x<p.x+p.w&&r.x+r.w>p.x&&r.y<p.y+p.h&&r.y+r.h>p.y),overflow:titles.filter(r=>r.x<20||r.x+r.w>1045||r.y<145||r.y+r.h>1600)};
   }));
  }
  const repeat=[];for(const fraction of [.05,.15,.35,.5,.65,.8,.94]){
   const t=end*fraction;await page.evaluate(async t=>{await renderAt(t);await imgWait();},t);const a=await page.evaluate(()=>structuredClone(V03_STATE));
   await page.evaluate(async t=>{await renderAt(Math.max(0,t-2));await imgWait();await renderAt(t);await imgWait();},t);const b=await page.evaluate(()=>structuredClone(V03_STATE));
   repeat.push({t,poseAndFrameIdentical:JSON.stringify(a)===JSON.stringify(b)});
  }
  const bad=rows.filter(r=>!r.headInside||r.overlap.length||r.overflow.length),report={errors,samples:rows.length,bad,repeat,rows};
  fs.writeFileSync(path.join(out,'geometry.json'),JSON.stringify(report,null,2));
  for(let i=0;i<12;i++){const t=Math.min(end-1/60,end*i/12);await page.evaluate(async t=>{await renderAt(t);await imgWait();await Promise.all([...document.images].filter(i=>i.src).map(i=>i.decode()));},t);await page.screenshot({path:path.join(out,`frame_${i.toString().padStart(2,'0')}.png`)});}
  console.log(JSON.stringify({samples:rows.length,bad:bad.map(r=>({t:r.t,headInside:r.headInside,overlap:r.overlap,overflow:r.overflow})),errors,repeat}));
  if(errors.length||bad.length||repeat.some(r=>!r.poseAndFrameIdentical))throw Error('V03 layout/seek QA failed; review geometry.json and fix this episode before export');
 }
}finally{await browser.close();}
