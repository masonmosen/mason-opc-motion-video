/* Episode-owned v03 derivative of Adu 01-B. One continuous container, split,
 * curved handoffs and consolidation; new semantic choreography, not a claim
 * that the two protected native groups have been played unchanged or sped up.
 * Adu lib.js/MOTION own easing, images and deterministic Bezier travel.
 */
(()=>{'use strict';
 const E=window.EPISODE;
 const map=(value,axis)=>{const points=E.timeMap;let i=1;while(i<points.length-1&&value>points[i][axis])i++;const a=points[i-1],b=points[i],q=Math.max(0,Math.min(1,(value-a[axis])/(b[axis]-a[axis])));return a[1-axis]+(b[1-axis]-a[1-axis])*q;};
 E.toVisual=t=>map(t,1);E.toOutput=t=>map(t,0);
 const C=clamp,L=lerp,Q=MOTION.at,TAU=Math.PI*2;
 $('brand').textContent=E.profile.displayName||E.profile.creator;
 const brandLine=document.createElement('span');brandLine.textContent=E.profile.tagline||'AI / CREATOR';$('brand').append(brandLine);
 $('disclosure').textContent=E.disclosure;

 const font='"Adu Sans",sans-serif',mono='"Adu Mono",monospace';
 const c=$('demo').getContext('2d'),f=$('field').getContext('2d'),actor=$('actor'),image=$('presenter'),carrier=$('carrier');
 const W=960,H=900,B='#2462ea',INK='#10121c',PAPER='#f7f7f5',LIGHT='#91b4ff';
 const layers=[],diagnostic={};
 function text(id,html,x,y,size,color=INK,cls=''){
  html=E.labels?.[id]??html;
  const e=document.createElement('div');e.className='type '+cls;e.innerHTML=html;
  Object.assign(e.style,{left:x+'px',top:y+'px',fontSize:size+'px',color});$('type').append(e);layers.push(e);return e;
 }
 function paint(e,on=1,tx=0,ty=0,s=1,r=0,blur=0){e.style.opacity=String(C(on));e.style.visibility=on<.001?'hidden':'visible';e.style.transform=`translate(${tx}px,${ty}px) rotate(${r}deg) scale(${s})`;e.style.filter=blur?`blur(${blur}px)`:'';}
 function enter(e,t,a,d=.24,opt={}){let p=C((t-a)/d),z=EZ.out5(p);paint(e,p*5,(opt.dx||0)*(1-z),(opt.dy??35)*(1-z),1+(opt.zoom??.1)*(1-z),0,6*(1-z));}
 function alpha(e,t,a,b,d=.2){enter(e,t,a,d);const out=C((t-b)/d);if(out>0)paint(e,1-out,0,-30*EZ.in(out),1,0,out*5);}
 const hook=text('hook','AI，只會聊天？',64,220,108),know=text('know','AI 認知',64,210,156),zero=text('zero','徹底<span style="color:#2462ea">清零</span>',64,220,148);
 const hookTag=text('hookTag','GEMINI 4 / CONCEPT CUT',68,405,26,'#62738a','mini');
 const chatH=text('chatH','還停在<br><span style="color:#2462ea">對話框？</span>',64,270,116);
 const era=text('era','時代變了',64,330,133,'#fff'),gem=text('gem','Gemini 4',64,365,160,'#fff'),breakH=text('breakH','破界降臨',68,555,104,'#fff');
 const oldAI=text('oldAI','過去的 AI',64,330,108),painA=text('painA','抽卡＝<span style="color:#2462ea">廢片</span>',105,700,105),painB=text('painB','長文<span style="color:#2462ea">失憶</span>',105,700,114),painC=text('painC','又要<span style="color:#2462ea">重來？</span>',105,700,108);
 const limitH=text('limitH','所有算力瓶頸',64,315,100),smash=text('smash','一秒<br><span style="color:#2462ea">粉碎</span>',64,580,174);
 const memN=text('memN','突破 01',64,220,35,LIGHT,'mini'),memH=text('memH','無損記憶',64,320,122,'#fff'),memNum=text('memNum','10M <span style="font-size:60px;letter-spacing:0">TOKENS</span>',64,480,130,'#fff');
 const physN=text('physN','突破 02',64,220,35,B,'mini'),physH=text('physH','3D 物理引擎',64,350,110);
 const swarmN=text('swarmN','突破 03',64,220,35,'#d2e1ff','mini'),singleH=text('singleH','從 1 個助手',64,345,112,'#fff'),swarmH=text('swarmH','AI 蜂群軍團',64,345,115,'#fff');
 const cmd=text('cmd','只需一句指令',64,490,55,'#d5e4ff'),deliveryH=text('deliveryH','協同交付',64,350,138,'#fff');
 const team=text('team','一人，<br>就是一支<br><span style="color:#2462ea">頂尖團隊</span>',64,410,88);
 const upgrade=text('upgrade','工具<br>升級？',64,450,123),life=text('life','超級<br>外掛<br><span style="color:#2462ea">人生</span>',64,420,132);
 const finalGem=text('finalGem','Gemini 4',64,320,147),world=text('world','萬物共生<br><span style="color:#2462ea">智造無限</span>',64,510,90);
 const next=text('next','下一代<br>創作主場',475,920,87),now=text('now','現在<br>開啟',475,1160,119,B);
 const bubble=text('bubble','聊完了，然後呢？',465,1050,37,INK,'bubble');
 const roles=E.roles;
 const roleLabels=roles.map((s,i)=>text('role-'+i,s,0,0,44,'#fff'));
 const actorKeys=[
  [0,{x:140,y:540,w:800,h:980,r:38},0],
  [3.1,{x:60,y:810,w:350,h:600,r:32},.26],
  [5.41,{x:790,y:150,w:230,h:230,r:115},0],
  [7.68,{x:760,y:145,w:250,h:250,r:125},0],
  [9.26,{x:760,y:145,w:250,h:250,r:38},.18],
  [10.54,{x:64,y:1050,w:310,h:440,r:30},0],
  [12.01,{x:740,y:1050,w:280,h:440,r:28},0],
  [14.11,{x:64,y:1310,w:240,h:240,r:120},.22],
  [19.17,{x:790,y:145,w:230,h:230,r:115},0],
  [23.27,{x:64,y:1050,w:300,h:470,r:30},0],
  [29.06,{x:790,y:145,w:230,h:230,r:115},0],
  [31.48,{x:435,y:525,w:585,h:1000,r:36},0],
  [33.16,{x:435,y:525,w:585,h:1000,r:36},0],
  [34.38,{x:435,y:525,w:585,h:1000,r:36},0],
  [36.38,{x:64,y:800,w:350,h:710,r:32},.26]
 ];
 function keyPose(keys,t){let i=keys.length-1;while(i>0&&t<keys[i][0])i--;const [a,b,d]=keys[i];if(!d||i===0)return {...b};let z=EZ.out5(C((t-a)/d)),old=keys[i-1][1];return Object.fromEntries(Object.keys(b).map(k=>[k,L(old[k],b[k],z)]));}
 function presenter(t){const p=keyPose(actorKeys,t),round=p.r>=Math.min(p.w,p.h)*.42;
  // The conservative source box includes hair, ears and chin, not eyes/mouth only.
  const safe=E.presenter.headBox;let scale,cy;
  const k=Q(p.r/(Math.min(p.w,p.h)/2),.25,.99);
  const portraitScale=Math.min(p.w*.76/safe.w,p.h*.76/safe.h);
  scale=L(portraitScale,p.w*.94/CONFIG.sourceWidth,k);cy=p.h*L(.44,.50,k);
  // During a rectangle-to-circle morph the safe rectangle must fit the actual
  // rounded mask too. Shrink around the same head center until all corners fit.
  const inside=(x,y)=>{
   const rr=Math.min(p.r,p.w/2,p.h/2),xx=C(x,rr,p.w-rr),yy=C(y,rr,p.h-rr);
   return x>=5&&x<=p.w-5&&y>=5&&y<=p.h-5&&(x-xx)**2+(y-yy)**2<=(rr-4)**2;
  };
  for(let tries=0;tries<60;tries++){
   const points=[[-safe.w/2,-safe.h/2],[safe.w/2,-safe.h/2],[-safe.w/2,safe.h/2],[safe.w/2,safe.h/2]];
   if(points.every(([x,y])=>inside(p.w/2+x*scale,cy+y*scale)))break;scale*=.98;
  }
  const ix=p.w/2-(safe.x+safe.w/2)*scale,iy=cy-(safe.y+safe.h/2)*scale;
  Object.assign(actor.style,{left:p.x+'px',top:p.y+'px',width:p.w+'px',height:p.h+'px',borderRadius:p.r+'px'});
  Object.assign(image.style,{width:CONFIG.sourceWidth*scale+'px',height:CONFIG.sourceHeight*scale+'px',left:ix+'px',top:iy+'px'});
  const n=Math.min(CONFIG.nativeFrames,Math.floor(window.EPISODE_OUTPUT_T*CONFIG.nativeFps+.5)+1);setFrame(image,'talk/native/f_'+String(n).padStart(5,'0')+'.jpg');
  diagnostic.presenter={...p,round,scale,ix,iy,sourceFrame:n,sourceSafeBox:safe};actor.dataset.pose=JSON.stringify(diagnostic.presenter);
 }
 const carrierKeys=[
  [0,{x:62,y:430,w:956,h:1120,r:45},0],
  [3.1,{x:430,y:650,w:590,h:730,r:36},.28],
  [5.41,{x:64,y:760,w:952,h:660,r:60},.28],
  [7.68,{x:64,y:580,w:952,h:900,r:36},.26],
  [12.01,{x:64,y:560,w:952,h:910,r:36},.24],
  [14.11,{x:64,y:650,w:952,h:900,r:36},.26],
  [19.17,{x:64,y:600,w:952,h:900,r:36},.26],
  [23.27,{x:400,y:650,w:620,h:860,r:36},.26],
  [29.06,{x:64,y:650,w:952,h:860,r:36},.26],
  [31.48,{x:435,y:525,w:585,h:1000,r:36},.28],
  [36.38,{x:450,y:830,w:570,h:710,r:36},.26]
 ];
 function rect(ctx,x,y,w,h,r=20,fill='#fff',stroke=null){ctx.beginPath();ctx.roundRect(x,y,w,h,r);if(fill){ctx.fillStyle=fill;ctx.fill();}if(stroke){ctx.strokeStyle=stroke;ctx.lineWidth=2;ctx.stroke();}}
 function line(ctx,pts,col,width=3,alpha=1){ctx.globalAlpha=alpha;ctx.strokeStyle=col;ctx.lineWidth=width;ctx.lineCap='round';ctx.lineJoin='round';ctx.beginPath();pts.forEach((p,i)=>i?ctx.lineTo(...p):ctx.moveTo(...p));ctx.stroke();ctx.globalAlpha=1;}
 function label(ctx,s,x,y,size=40,col=INK,weight=700,align='left'){ctx.font=`${weight} ${size}px ${font}`;ctx.textAlign=align;ctx.fillStyle=col;ctx.fillText(s,x,y);ctx.textAlign='left';}
 function circle(ctx,x,y,r,col,stroke=null){ctx.beginPath();ctx.arc(x,y,r,0,TAU);if(col){ctx.fillStyle=col;ctx.fill();}if(stroke){ctx.strokeStyle=stroke;ctx.lineWidth=3;ctx.stroke();}}
 function sparkle(ctx,x,y,r,col){line(ctx,[[x-r,y],[x+r,y]],col,3);line(ctx,[[x,y-r],[x,y+r]],col,3);}
 function icon(ctx,id,x,y,s,col=B){ctx.save();ctx.translate(x,y);ctx.scale(s,s);ctx.strokeStyle=col;ctx.lineWidth=4;ctx.lineCap='round';
  if(id===0){rect(ctx,-35,-22,70,48,7,null,col);line(ctx,[[-35,-32],[35,-32]],col,8);for(let j=0;j<4;j++)line(ctx,[[-29+j*19,-38],[-21+j*19,-26]],PAPER,4);}
  if(id===1){label(ctx,'{ }',0,18,66,col,800,'center');}
  if(id===2){line(ctx,[[-28,29],[27,-28]],col,8);sparkle(ctx,22,-23,17,col);sparkle(ctx,-23,-28,9,col);}
  if(id===3){for(let j=0;j<7;j++)line(ctx,[[-28+j*9,-(10+Math.sin(j*1.2)*10)],[-28+j*9,10+Math.sin(j*1.2)*10]],col,5);}
  ctx.restore();
 }
 function strip(ctx,x,y,w,h,col,seed){rect(ctx,x,y,w,h,12,col);ctx.fillStyle='#ffffffbb';for(let j=0;j<6;j++){ctx.fillRect(x+12+j*(w-30)/6,y+8,10,5);ctx.fillRect(x+12+j*(w-30)/6,y+h-13,10,5);}for(let j=0;j<4;j++){ctx.fillStyle=['#9dc4f8','#c1ddf5','#497eae','#82adc2'][(j+seed)%4];ctx.fillRect(x+15+j*(w-30)/4,y+24,(w-40)/4,h-47);}}
 function timeline(ctx,t,x=90,y=260,w=780,h=440){
  rect(ctx,x,y,w,h,26,'#102452','#aec7ff');label(ctx,'一句指令 → 成片',x+32,y+64,42,'#fff');
  for(let i=0;i<4;i++){icon(ctx,i,x+62,y+128+i*72,.45,'#a9c7ff');const p=Q(t,29.13+i*.14,29.65+i*.14);rect(ctx,x+112,y+101+i*72,(w-150)*p,48,9,['#377bff','#7a66ef','#54abdd','#e0b67b'][i]);}
  const z=Q(t,29.8,30.9);line(ctx,[[x+112+(w-150)*z,y+93],[x+112+(w-150)*z,y+400]],'#fff',3);circle(ctx,x+w-42,y+40,13,t>30.4?'#a2f4c3':'#d5e4ff');
 }
 function background(t,dark,blue){
  f.reset();f.fillStyle=blue?B:dark?'#101728':PAPER;f.fillRect(0,0,1080,1920);
  const col=blue?'#ffffff13':dark?'#91b4ff0d':'#2462ea0a';f.strokeStyle=col;f.lineWidth=1;
  for(let j=0;j<13;j++){f.beginPath();f.moveTo(540,1450);f.lineTo(-300+j*140,1920);f.stroke();}
  for(let j=0;j<7;j++){const y=1460+j*j*12;f.beginPath();f.moveTo(0,y);f.lineTo(1080,y);f.stroke();}
  // Secondary marks belong to semantic stages; no whole-frame continuous shake.
  if(t>=14.11&&t<31.48){for(let i=0;i<22;i++){const x=hash(i+3)*1080,y=170+hash(i+20)*1360;f.globalAlpha=.1+.13*hash(i+8);circle(f,x,y,1.5+hash(i+4)*2,dark||blue?'#cbdcff':B);}f.globalAlpha=1;}
  if(t>=13.29&&t<14.11){const a=t-13.29;for(let i=0;i<42;i++){const angle=hash(i)*TAU,v=200+hash(i+2)*850,x=520+Math.cos(angle)*v*a,y=920+Math.sin(angle)*v*a+a*a*230;
    // Keep the presenter silhouette clear while the old boundary fractures.
    if(x>710&&y>1000)continue;f.save();f.translate(x,y);f.rotate(a*(hash(i+5)*6-3));f.globalAlpha=C(1-a/.85);rect(f,-20,-9,18+hash(i+7)*58,8+hash(i+9)*32,3,i%3?B:'#18263f');f.restore();}}
 }
 function opening(t){
  c.clearRect(0,0,W,H);const small=Q(t,0,.18);c.strokeStyle='#b8ccf4';c.lineWidth=3;
  // A four-role outcome is visible from frame zero, before its explanation.
  const yy=790;for(let i=0;i<4;i++){icon(c,i,140+i*220,yy,.58,B);if(i<3)line(c,[[177+i*220,yy],[312+i*220,yy]],'#c4d5f6',3);}
  if(t>=2.62){const q=Q(t,2.62,2.84);label(c,String(Math.round(100*(1-q))).padStart(3,'0'),480,210,150,B,800,'center');line(c,[[330,242],[630,242]],B,8);}
 }
 function chat(t){c.clearRect(0,0,W,H);rect(c,0,0,W,H,30,'#fff');rect(c,0,0,W,85,0,'#eef3fe');for(let i=0;i<3;i++)circle(c,35+i*33,43,8,'#b4c6e7');label(c,'CHAT',140,58,30,'#62738a');
  const a=Q(t,3.24,3.55);rect(c,280+(1-a)*200,155,610,145,35,'#2462ea');label(c,'幫我完成創作',330+(1-a)*200,245,58,'#fff');
  const b=Q(t,4.0,4.24);rect(c,50-(1-b)*140,365,720,210,35,'#edf2fc');label(c,'好的，我來聊聊……',98-(1-b)*140,468,54,INK);
  for(let i=0;i<3;i++)circle(c,120+i*55,530,8+3*Math.sin(t*7+i),B);
  line(c,[[60,742],[890,742]],'#d5dfef',3);label(c,'輸入訊息',92,815,44,'#9aa7bb');circle(c,850,803,28,B);line(c,[[836,803],[864,803]],'#fff',4);
 }
 function breakthrough(t){c.clearRect(0,0,W,H);const p=Q(t,6.85,7.18);c.save();c.translate(480,450);c.rotate(-.035*(1-p));
  for(let i=0;i<4;i++){const a=(i-1.5)*170;rect(c,a-65,-160,130,320,20,'#ffffff12','#aec8ff');icon(c,i,a,0,.9,'#fff');}
  for(let i=0;i<7;i++){c.globalAlpha=.7*(1-p);line(c,[[-450+i*150,-380],[-450+i*150+(i-3)*100*p,380]],'#fff',3);}c.restore();c.globalAlpha=1;
 }
 function pain(t){c.clearRect(0,0,W,H);rect(c,0,0,W,H,28,'#fff');const phase=t<9.26?0:t<10.54?1:2;
  label(c,['抽卡 / IMAGE','長文 / CONTEXT','工作流 / RESET'][phase],42,76,30,'#7b8aa4');
  if(phase===0){for(let i=0;i<3;i++){const x=50+i*290,p=Q(t,7.75+i*.07,8.03+i*.07);c.save();c.translate(x,270+40*(1-p));c.rotate((i-1)*.04);strip(c,0,0,265,320,['#cad9ee','#e1e6ef','#b4cae7'][i],i);let z=Q(t,8.53+i*.04,8.72+i*.04);line(c,[[30,60],[30+205*z,60+210*z]],'#2462ea',13);line(c,[[235,60],[235-205*z,60+210*z]],'#2462ea',13);c.restore();}}
  if(phase===1){for(let j=0;j<9;j++){let r=Q(t,9.65,10.06);const a=j>3?(1-r):1;rect(c,60+(j>3?j*15*r:0),260+j*47,650+(j%3)*80,15,7,j>3?'#b7c9e8':'#91b4ff');c.globalAlpha=a;}c.globalAlpha=1;const age=t-9.72;if(age>0&&age<.22){c.fillStyle='#fff';c.fillRect(40,400,W-80,30);}}
  if(phase===2){const rot=(t-10.54)*TAU*.8;c.strokeStyle=B;c.lineWidth=22;c.beginPath();c.arc(535,410,148,-2.2+rot,2.1+rot);c.stroke();c.save();c.translate(535+148*Math.cos(2.1+rot),410+148*Math.sin(2.1+rot));c.rotate(2.1+rot);c.fillStyle=B;c.beginPath();c.moveTo(-30,-25);c.lineTo(35,0);c.lineTo(-30,25);c.fill();c.restore();label(c,'回到起點',535,665,64,B,800,'center');}
 }
 function limits(t){c.clearRect(0,0,W,H);if(t>=13.29)return;label(c,'COMPUTE LIMIT',44,76,30,'#7b8aa4');for(let j=0;j<6;j++){const x=70+j*140,h=200+j*45;rect(c,x,630-h,90,h,15,j<3?'#d9e4f8':'#abc6ff');}line(c,[[55,180],[905,180]],B,9);label(c,'瓶頸',480,780,68,B,800,'center');}
 function memory(t){
  c.clearRect(0,0,W,H);rect(c,0,0,W,H,30,'#101d3a');
  // Source 01-B split/curved-join grammar, retimed as an explicitly new variant.
  const time=t-14.11,focus=[W*.54,H*.48];
  for(let i=0;i<20;i++){const k=C((time-.6-i*.1)/1.8),angle=i*2.399,dist=250+hash(i)*200;
   const from=[focus[0]+Math.cos(angle)*dist,focus[1]+Math.sin(angle)*dist*.85];
   const xy=MOTION.bezier(from,[from[0],from[1]-150],[focus[0]+170*Math.sin(angle),focus[1]+80],focus,EZ.inout(k));
   const scale=L(1,.12,k);c.save();c.translate(...xy);c.rotate((i%3-1)*.13*(1-k));c.scale(scale,scale);c.globalAlpha=1-Q(k,.85,1);
   if(i%3===0){strip(c,-65,-48,130,96,'#456cbc',i);}else{rect(c,-57,-62,114,124,11,'#e6efff');label(c,i%2?'{ }':'</>',0,9,40,B,800,'center');for(let j=0;j<3;j++)rect(c,-39,25+j*9,65-j*9,3,1,'#91afe5');}c.restore();}
  const z=Q(t,14.7,15.0),pulse=.5+.5*Math.sin(time*3);c.save();c.translate(...focus);c.rotate(-.04+.025*Math.sin(time));
  for(let j=3;j>=0;j--)rect(c,-135+j*13,-145+j*15,270,290,28,['#3678fa','#2b5ccc','#244a9e','#1e3982'][j],'#80aaff');
  label(c,'MEMORY',0,-52,28,'#c6daff',600,'center');label(c,E.diagramMemoryLabel||'10M',0,70,106,'#fff',850,'center');line(c,[[-85,110],[85,110]],'#a3f2d6',5);c.restore();
  if(t>=17.0){const p=Q(t,17,17.22);c.globalAlpha=p;label(c,'代碼庫 + 百部電影',480,760,51,'#dae6ff',650,'center');c.globalAlpha=1;}
 }
 function project3(p,turn=0){const [x,y,z]=p,xx=x*Math.cos(turn)+z*Math.sin(turn),zz=-x*Math.sin(turn)+z*Math.cos(turn),yy=y*.91-zz*.35,depth=1/(1+zz/1300);return [480+xx*depth,500+yy*depth,depth];}
 function physics(t){c.clearRect(0,0,W,H);rect(c,0,0,W,H,30,'#eaf1ff');const u=t-19.17,turn=-.18+.2*Q(t,19.17,23.1);
  // Perspective floor plus moving shadow/reflection; a physics concept visual.
  for(let i=-4;i<=4;i++){let a=project3([i*100,210,-380],turn),b=project3([i*100,210,380],turn);line(c,[a.slice(0,2),b.slice(0,2)],'#b9cfed',2);a=project3([-400,210,i*95],turn);b=project3([400,210,i*95],turn);line(c,[a.slice(0,2),b.slice(0,2)],'#b9cfed',2);}
  const bx=130*Math.sin(u*1.25),height=230*Math.abs(Math.sin(u*2.6)),by=118-height,p=project3([bx,by,0],turn),shadow=project3([bx,205,0],turn);
  c.save();c.translate(shadow[0],shadow[1]);c.scale(1,.3);const g=c.createRadialGradient(0,0,0,0,0,125);g.addColorStop(0,'#1a4caa55');g.addColorStop(1,'#1a4caa00');circle(c,0,0,125,g);c.restore();
  let r=85*p[2],s=c.createRadialGradient(p[0]-r*.4,p[1]-r*.45,2,p[0],p[1],r);s.addColorStop(0,'#d7eaff');s.addColorStop(.28,'#69a2ff');s.addColorStop(.68,'#2462ea');s.addColorStop(1,'#0c2d7a');circle(c,p[0],p[1],r,s);circle(c,p[0]-r*.32,p[1]-r*.4,r*.16,'#ffffff88');
  if(t<22.31){label(c,'光影',70,115,44,B);line(c,[[70,150],[255,150]],B,4);}
  // A shaded fluid mesh replaces the ball as the spoken concept changes.
  const a=Q(t,22.31,22.55);if(a>0){c.save();c.globalAlpha=a;c.fillStyle='#eaf1ff';c.fillRect(0,0,W,H);const n=22,m=12;
   const wave=(x,z)=>{let d=Math.sqrt((x+70)**2+(z-50)**2),v=Math.sin(d*.022-u*5.5)*30*Math.exp(-d/600);return project3([x,100+v,z],turn);};
   for(let j=m-1;j>=0;j--)for(let i=0;i<n;i++){const x=-410+i*820/n,z=-300+j*600/m,pts=[wave(x,z),wave(x+820/n,z),wave(x+820/n,z+600/m),wave(x,z+600/m)],light=140+Math.round(42*Math.sin(i*.32+j*.55-u*3));c.beginPath();pts.forEach((p,k)=>k?c.lineTo(p[0],p[1]):c.moveTo(p[0],p[1]));c.closePath();c.fillStyle=`rgb(36,${light},235)`;c.fill();c.strokeStyle='#b8e1ff66';c.lineWidth=1;c.stroke();}
   label(c,'流體',70,115,44,B);line(c,[[70,150],[255,150]],B,4);c.restore();}
  label(c,'光影 / 材質 / 運動',480,808,37,'#536f9d',600,'center');
 }
 function swarm(t,p){c.clearRect(0,0,W,H);const split=Q(t,24.74,25.05),local=t-23.27;const center=[500,390],ends=[[245,230],[740,230],[245,640],[740,640]];
  c.globalAlpha=.6;for(let i=0;i<4;i++){const xy=[L(center[0],ends[i][0],split),L(center[1],ends[i][1],split)];line(c,[center,xy],'#accbff',3);const z=((local*.65+i*.22)%1);circle(c,L(center[0],xy[0],z),L(center[1],xy[1],z),6,'#fff');}c.globalAlpha=1;
  for(let i=0;i<4;i++){const xy=[L(center[0],ends[i][0],split),L(center[1],ends[i][1],split)];const pop=Q(t,24.74+i*.06,24.98+i*.06);c.save();c.translate(...xy);c.rotate((i-1.5)*.08*(1-pop));c.scale(.75+.25*pop,.75+.25*pop);rect(c,-133,-104,266,208,28,'#f3f7ff','#a5c3ff');icon(c,i,0,-25,1.15,B);const namesAt=[27.27,27.68,28.1,28.5][i];if(t>=namesAt)label(c,roles[i],0,73,46,B,800,'center');c.restore();}
  circle(c,...center,54,'#111e42','#b1ceff');label(c,'1',... [center[0],center[1]+23],63,'#fff',800,'center');
  if(split<.02){rect(c,center[0]-155,center[1]-130,310,260,28,'#fff');label(c,'AI',center[0],center[1]+34,100,B,800,'center');}
 }
 function ending(t){c.clearRect(0,0,W,H);if(t<36.38){for(let i=0;i<4;i++)icon(c,i,180+i*200,760,.7,B);}else{
   const p=Q(t,39.48,39.8);for(let i=0;i<3;i++){const z=C(p-i*.14);c.globalAlpha=.35*(1-z);c.strokeStyle=B;c.lineWidth=3;c.beginPath();c.arc(500,450,70+z*330,0,TAU);c.stroke();}c.globalAlpha=1;
   // Same four channels resolve into one output boundary.
   for(let j=0;j<4;j++)rect(c,75,100+j*175,810,70,14,['#2462ea','#7665d7','#6ca7d0','#a0b6d6'][j]);
  }}
 function titles(t){
  layers.forEach(e=>paint(e,0));
  if(t<.87){paint(hook,1,0,0,1+.035*(1-Q(t,0,.22)));paint(hookTag,1);}
  else if(t<1.96){enter(know,t,.87,.22,{zoom:.13});paint(hookTag,1);}
  else if(t<3.1){enter(zero,t,1.96,.22,{zoom:.11});paint(hookTag,1);if(t>2.62)paint(zero,1,0,0,1+.025*Math.exp(-(t-2.62)*15));}
  else if(t<5.41){enter(chatH,t,3.1);alpha(bubble,t,4.78,5.25,.12);}
  else if(t<6.24)enter(era,t,5.41,.2,{dx:110,zoom:0});
  else if(t<7.68){enter(gem,t,6.24,.24,{zoom:.14});if(t>6.92)enter(breakH,t,6.92,.2,{dx:-120,zoom:0});}
  else if(t<12.01){paint(oldAI,1);if(t<9.26)enter(painA,t,7.68,.22,{zoom:.08});else if(t<10.54)enter(painB,t,9.26,.18,{dx:100});else enter(painC,t,10.54,.2,{dx:-110});}
  else if(t<13.29)enter(limitH,t,12.01);
  else if(t<14.11)enter(smash,t,13.29,.19,{zoom:.2});
  else if(t<19.17){paint(memN,1);enter(memH,t,14.11,.22);if(t>=14.7)enter(memNum,t,14.7,.2,{zoom:.13});}
  else if(t<23.27){paint(physN,1);enter(physH,t,19.17,.22,{dx:100,zoom:0});}
  else if(t<29.06){paint(swarmN,1);if(t<24.74)enter(singleH,t,23.27);else enter(swarmH,t,24.74,.23,{zoom:.08});if(t>=26.14)enter(cmd,t,26.14,.2);}
  else if(t<31.48){paint(swarmN,1);enter(deliveryH,t,29.06,.23,{zoom:.12});}
  else if(t<33.16)enter(team,t,31.48,.22,{dx:-65,zoom:0});
  else if(t<34.38)enter(upgrade,t,33.16,.2,{zoom:.1});
  else if(t<36.38)enter(life,t,34.38,.22,{zoom:.1});
  else{enter(finalGem,t,36.38,.22,{zoom:.08});if(t>=36.98)enter(world,t,36.98);if(t>=38.6)enter(next,t,38.6,.2);if(t>=39.48)enter(now,t,39.48,.18,{zoom:.12});}
 }
 function sceneCamera(t){let dx=0,dy=0,z=1,blur=0;const cuts=[3.1,5.41,7.68,9.26,10.54,14.11,19.17,23.27,29.06,31.48,36.38];
  for(let i=0;i<cuts.length;i++){const age=t-cuts[i];if(age>=0&&age<.22){const u=age/.22;dx=(i%2?1:-1)*92*(1-EZ.out5(u));blur=6*(1-u);z=1+.035*(1-u);}}
  const hit=[2.62,6.92,8.53,13.29,14.7,24.74,31.48,34.38,39.48].find(a=>t>=a&&t<a+.22);
  if(hit!=null){let age=t-hit;z+=.035*Math.exp(-age*19);}
  $('camera').style.transform=`translate(${dx}px,${dy}px) scale(${z})`;$('camera').style.filter=blur?`blur(${blur}px)`:'';
 }
 window.renderAt=async t=>{
  const outputT=Math.min(CONFIG.end-1/60,Math.max(0,Math.floor(t*60+1e-6)/60));window.EPISODE_OUTPUT_T=outputT;t=E.toVisual(outputT);const blue=t>=5.41&&t<7.68||t>=23.27&&t<31.48,dark=t>=14.11&&t<19.17;
  background(t,dark,blue);presenter(t);titles(t);sceneCamera(t);
  const p=keyPose(carrierKeys,t);Object.assign(carrier.style,{left:p.x+'px',top:p.y+'px',width:p.w+'px',height:p.h+'px',borderRadius:p.r+'px',opacity:t>=13.29&&t<14.11?'0':t>=31.48&&t<36.38?'.4':t>=36.38?'.18':'1',background:blue?B:dark?'#101d3a':'#fff',borderColor:blue?'#a6c6ff':dark?'#4c75b7':'#aac1ed'});
  if(t<3.1)opening(t);else if(t<5.41)chat(t);else if(t<7.68)breakthrough(t);else if(t<12.01)pain(t);else if(t<14.11)limits(t);else if(t<19.17)memory(t);else if(t<23.27)physics(t);else if(t<29.06)swarm(t,p);else if(t<31.48){c.clearRect(0,0,W,H);timeline(c,t);}else ending(t);
  const sub=SUBS.find(s=>outputT>=s.t0&&outputT<s.t1);$('caption').textContent=sub?.zh||'';$('caption').dataset.cue=sub?.id||'';
  const color=dark||blue?'#e7efff':INK;$('brand').style.color=color;$('disclosure').style.color=color;$('progress').style.background=dark||blue?'#b9d1ff':B;$('progress').style.transform=`scaleX(${outputT/CONFIG.end})`;
  diagnostic.t=t;diagnostic.outputTime=outputT;diagnostic.scene=t<3.1?'hook':t<5.41?'chat':t<7.68?'breakthrough':t<12.01?'pain':t<14.11?'shatter':t<19.17?'memory':t<23.27?'physics':t<29.06?'swarm':t<31.48?'delivery':t<36.38?'creator':'final';diagnostic.carrier=p;
  window.V03_STATE=diagnostic;
 };
 window.END=CONFIG.end;
 window.V03_ACTOR_KEYS=actorKeys;
 const cues=[
 [0,'intro',.16,0],[.23,'click',.15,-.1],[.87,'snap',.2,-.15],[1.96,'snap',.2,0],[2.62,'reset',.29,0],
 [3.05,'whip',.28,.6],[4,'typing',.15,.4],[5.25,'reverse',.22,0],[5.41,'impact',.34,0],[6.24,'bass',.25,0],[6.92,'fracture',.28,0],
 [7.64,'whip',.25,-.6],[8.53,'reject',.22,-.3],[9.23,'glitch',.24,.35],[10.50,'rewind',.23,-.4],
 [12.0,'riser',.18,0],[13.29,'shatter',.35,0],[14.08,'whip',.25,.5],[14.7,'impact',.26,0],
 [15.3,'data',.14,-.6],[15.7,'data',.13,.5],[16.15,'data',.13,-.4],[16.7,'data',.15,.5],[17.4,'data',.13,-.6],[18.2,'lock',.2,0],
 [19.12,'whip',.24,-.5],[19.62,'glass',.22,.2],[20.34,'bounce',.17,-.2],[21.55,'bounce',.14,.15],[22.31,'water',.23,.35],
 [23.2,'reverse',.17,0],[23.27,'impact',.28,0],[24.74,'split',.24,.2],[26.14,'typing',.15,-.2],
 [27.27,'node',.17,-.65],[27.68,'node',.16,.65],[28.1,'node',.17,-.4],[28.5,'node',.17,.4],
 [29.00,'whip',.26,0],[30.5,'success',.22,0],[31.48,'impact',.31,0],[33.16,'snap',.16,0],[34.38,'power',.26,0],[36.38,'whip',.23,-.35],[38.6,'riser',.16,.1],[39.48,'success',.3,0]
 ];
 cues.forEach(([t,type,g,p])=>S(E.toOutput(t),type,g,p,{eventId:'v03-'+t+'-'+type,sceneInstanceId:'v03-episode'}));
 window.READY=(async()=>{await document.fonts.ready;await renderAt(0);await imgWait();document.title='done';})();
})();
