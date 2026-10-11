// Original browser-synthesized ambience. No network or microphone access.
let context, master, wind, birds, muted=localStorage.getItem('wanderlore-muted')==='true';
let ducked=false, weather='clear', breezeGain, rainGain;
const weatherNames={clear:'Clear skies',cloudy:'Cloudy hush',rainy:'Light drizzle',windy:'Wind through the pines'};
export function setSceneWeather(value){
 weather=Object.hasOwn(weatherNames,value)?value:'clear';
 const scene=document.querySelector('.landing-scene');
 if(scene)scene.dataset.weather=weather;
 const status=document.querySelector('#weather-ambience');
 if(status)status.textContent=weatherNames[weather]+' · Background ambience';
 if(context){
  breezeGain.gain.setTargetAtTime({clear:.7,cloudy:.45,rainy:.25,windy:1.8}[weather],context.currentTime,.8);
  rainGain.gain.setTargetAtTime(weather==='rainy'?1.05:0,context.currentTime,.8);
 }
 label();
}

const reduced=matchMedia('(prefers-reduced-motion: reduce)');
function level(){
 if(!master)return;
 const home=document.body.classList.contains('landing');
 master.gain.setTargetAtTime(!muted&&home&&!document.hidden?(ducked?0.008:0.07):0,context.currentTime,0.5);
}
function label(){
 const button=document.querySelector('#scene-sound');if(!button)return;
 const on=!muted&&context?.state==='running';
 button.setAttribute('aria-pressed',String(on));
 button.innerHTML=`<span aria-hidden="true">${on?'◖))':'◖×'}</span> ${on?'Sound on':muted?'Sound off':'Enable sound'}`;
}
function chirp(){
 if(weather!=='clear'||!context||muted||document.hidden||!document.body.classList.contains('landing'))return;
 const t=context.currentTime;
 for(let i=0;i<3;i++){
  const o=context.createOscillator(),g=context.createGain();
  o.type='sine';o.frequency.setValueAtTime(1550+i*170,t+i*.18);o.frequency.exponentialRampToValueAtTime(2600-i*170,t+i*.18+.07);o.frequency.exponentialRampToValueAtTime(1800,t+i*.18+.13);
  g.gain.setValueAtTime(0,t+i*.18);g.gain.linearRampToValueAtTime(.12,t+i*.18+.025);g.gain.exponentialRampToValueAtTime(.001,t+i*.18+.15);
  o.connect(g).connect(master);o.start(t+i*.18);o.stop(t+i*.18+.16);
 }
}
async function enable(){
 if(muted)return;
 try{
  if(!context){
   context=new AudioContext();master=context.createGain();master.gain.value=0;master.connect(context.destination);
   const buffer=context.createBuffer(1,context.sampleRate*8,context.sampleRate),data=buffer.getChannelData(0);let last=0;
   for(let i=0;i<data.length;i++){last=(last+Math.random()*.035-.0175)/1.018;data[i]=last*6}
   wind=context.createBufferSource();wind.buffer=buffer;wind.loop=true;
   const filter=context.createBiquadFilter();filter.type='lowpass';filter.frequency.value=650;breezeGain=context.createGain();wind.connect(filter).connect(breezeGain).connect(master);wind.start();
   const rainBuffer=context.createBuffer(2,context.sampleRate*12,context.sampleRate);
   for(let channel=0;channel<2;channel++){
    const drops=rainBuffer.getChannelData(channel);
    for(let i=0;i<drops.length;i++)drops[i]=(Math.random()*2-1)*.3;
    // Tiny, scattered impacts over a soft stereo wash: drizzle rather than a storm.
    for(let n=0;n<500;n++){
     const start=Math.floor(Math.random()*(drops.length-1600));
     for(let j=0;j<1600;j++)drops[start+j]+=(Math.random()*2-1)*.22*Math.exp(-j/180);
    }
   }
   const rain=context.createBufferSource();rain.buffer=rainBuffer;rain.loop=true;
   const rainFilter=context.createBiquadFilter();rainFilter.type='lowpass';rainFilter.frequency.value=4800;
   rainGain=context.createGain();rainGain.gain.value=0;rain.connect(rainFilter).connect(rainGain).connect(master);rain.start();
   const gust=context.createOscillator(),gustDepth=context.createGain();gust.frequency.value=.13;gustDepth.gain.value=.16;gust.connect(gustDepth).connect(breezeGain.gain);gust.start();
   setSceneWeather(weather);
   birds=setInterval(chirp,11000);
   context.onstatechange=label;
  }
  await context.resume();level();label();
 }catch{label()}
}
export function sceneMarkup(){return `<section class="landing-scene" aria-labelledby="scene-title"><div class="scene-landscape" role="img" aria-label="Illustrated sunset over a pine forest, winding river, and distant mountain lookout"></div><div class="scene-motes" aria-hidden="true">${Array.from({length:14},(_,i)=>`<i class="mote mote-${i}"></i>`).join('')}</div><div class="scene-weather" aria-hidden="true"><div class="scene-clouds"></div><div class="scene-rain">${Array.from({length:110},(_,i)=>`<i class="raindrop-${i}"></i>`).join('')}</div></div><div class="scene-copy"><p class="scene-eyebrow">A LITTLE WONDER. A LONGER WAY HOME.</p><h1 id="scene-title">Every path<br>has a story.</h1><p class="scene-description">Step outside the ordinary.<br>Let the world become your story.</p><button class="scene-enter" id="enter-story">Find your story <span aria-hidden="true">↗</span></button></div><div class="lantern-stage" aria-hidden="true"><div class="lantern"><div class="lantern-handle"></div><div class="lantern-roof"></div><div class="lantern-glass front"></div><div class="lantern-glass side"></div><div class="lantern-flame"></div><div class="lantern-base"></div></div></div><div class="scene-bottom"><p><span>01 / THE BEGINNING</span>Somewhere, a story is waiting for you.</p><button id="scene-sound" class="sound-toggle" aria-pressed="false">Enable sound</button></div><button class="scene-scroll" id="explore-options" aria-label="Choose your walking story">SCROLL TO WANDER <span aria-hidden="true">↓</span></button></section>`}
export function mountScene(selectedWeather=weather){
 const scene=document.querySelector('.landing-scene');if(!scene)return;
 setSceneWeather(selectedWeather);level();
 const enter=()=>{enable();const target=document.querySelector('#walk-panel')||document.querySelector('#prepare');target?.scrollIntoView({behavior:reduced.matches?'instant':'smooth'});(document.querySelector('#walk-title')||document.querySelector('#prepare-title'))?.focus({preventScroll:true})};
 if(document.querySelector('#walk-panel')){document.querySelector('#enter-story').innerHTML='Return to your story <span aria-hidden="true">↗</span>';document.querySelector('#explore-options').setAttribute('aria-label','Return to your walking story')}
 document.querySelector('#enter-story').onclick=enter;document.querySelector('#explore-options').onclick=enter;
 document.querySelector('#scene-sound').onclick=async()=>{muted=context?.state==='running'&&!muted;localStorage.setItem('wanderlore-muted',String(muted));if(!muted)await enable();level();label()};
 scene.onpointermove=event=>{if(reduced.matches||event.pointerType==='touch')return;const rect=scene.getBoundingClientRect();scene.style.setProperty('--px',`${(event.clientX/rect.width-.5)*14}px`);scene.style.setProperty('--py',`${((event.clientY-rect.top)/rect.height-.5)*10}px`)};
 scene.onpointerleave=()=>{scene.style.setProperty('--px','0px');scene.style.setProperty('--py','0px')};
}
document.addEventListener('pointerdown',event=>{if(event.target.closest('#scene-sound'))return;if(document.body.classList.contains('landing')&&!muted)enable()});
document.addEventListener('keydown',event=>{if((event.key==='Enter'||event.key===' ')&&!muted&&document.body.classList.contains('landing')&&!event.target.closest('#scene-sound'))enable()});
document.addEventListener('play',event=>{if(event.target instanceof HTMLMediaElement){ducked=true;level()}},true);
for(const name of ['pause','ended'])document.addEventListener(name,()=>{ducked=Array.from(document.querySelectorAll('audio')).some(a=>!a.paused&&!a.ended);level()},true);
document.addEventListener('visibilitychange',()=>{level();if(document.hidden)context?.suspend();else if(context&&!muted)context.resume().catch(()=>{})});
new MutationObserver(level).observe(document.body,{attributes:true,attributeFilter:['class']});
