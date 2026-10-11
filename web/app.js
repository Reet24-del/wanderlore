import {sceneMarkup,mountScene,setSceneWeather} from './scene.js';
import {api,send,escape as e} from './api.js';
import {mapMarkup} from './map.js';
const app=document.querySelector('#app'),notice=document.querySelector('#notice'),audio=document.querySelector('#narrator'),dialog=document.querySelector('#setup-dialog');
const arrow='<svg class="arrow" viewBox="0 0 24 24" aria-hidden="true"><path d="M3 12h17M13 5l7 7-7 7"/></svg>';
let health=null,walk=null,pack=null,busy=false,watchId=null,fix=null,autoTimer=null,elapsedTimer=null,elapsed=0,wake=null,requestId=null,currentAudio=null,auto=false;
let startError='',pendingChoice=null;
let choices={genre:'folklore',minutes:20,weather:localStorage.getItem('wanderlore-weather')||'clear',mode:'gps',engine:'sample',voice:localStorage.getItem('wanderlore-voice')||'af_heart',pack_id:localStorage.getItem('wanderlore-pack')||null};
function message(text){notice.textContent=text;notice.hidden=!text}
function report(error){message(error.message||String(error))}
function label(value){return value.charAt(0).toUpperCase()+value.slice(1)}
function clock(seconds){return `${Math.floor(seconds/60)}:${String(Math.floor(seconds%60)).padStart(2,'0')}`}
function stopTimer(){clearTimeout(autoTimer);autoTimer=null}
async function refreshHealth(){health=await api('/health');return health}
function voiceNotice(){return (health?.online_narrator?'Online Gemma · Story context and nearby place names are sent to Google. Google’s free tier may use prompts to improve its products. ':'')+ choices.voice==='elevenlabs'?'Online voice · Chapter text, including place names, is sent to ElevenLabs.':'Local voice · Works offline after setup.'}
function disabled(){return busy?'disabled':''}
function home(){
 document.body.classList.add("landing");
 const resumeId=localStorage.getItem('wanderlore-active');
 app.innerHTML=`${sceneMarkup()}${resumeId?'<div class="resume-banner">Your unfinished story is saved.<button class="secondary" id="resume-saved">Return to walk</button></div>':''}${health?.temporary_storage?'<p class="resume-banner">Free hosted demo: saved walks and audio can reset when the server sleeps or restarts. Export your walk before leaving.</p>':''}<section id="prepare"><div class="prepare-intro"><span class="label">THE FIRST CHAPTER IS YOURS</span><h2 id="prepare-title" tabindex="-1">Where shall<br>we wander?</h2><p>A quiet mystery. A little folklore. Something wonderfully impossible.</p><p>Choose your mood, find your voice, and let the next chapter meet you along the way.</p><p class="chapter-mark">${health?.hosted?'A LITTLE CURIOSITY. A NEW STORY.':'NO SIGNAL NEEDED. JUST CURIOSITY.'}</p></div><div class="intro"><form class="walk-form" id="walk-form"><span class="label" id="genre-label">MAKE IT YOURS</span><div class="genres" role="group" aria-labelledby="genre-label">${['folklore','mystery','fantasy'].map(g=>`<button type="button" data-genre="${g}" class="${choices.genre===g?'selected':''}" aria-pressed="${choices.genre===g}">${label(g)}</button>`).join('')}</div><div class="select-row"><label><span class="select-label">Time to wander</span><select id="minutes">${[10,20,30].map(n=>`<option value="${n}" ${n===choices.minutes?'selected':''}>${n} minutes</option>`).join('')}</select></label><label><span class="select-label">Weather, as you see it</span><select id="weather">${Object.entries({clear:'Clear skies',cloudy:'Cloudy',rainy:'Rainy',windy:'Windy'}).map(([k,v])=>`<option value="${k}" ${choices.weather===k?'selected':''}>${v}</option>`).join('')}</select></label></div><p class="hint" id="weather-ambience" role="status" aria-live="polite"></p><div class="mode-options">${[['sample','Sample walk'],['gps','Use my location']].map(([value,text])=>`<label><input type="radio" name="mode" value="${value}" ${choices.mode===value?'checked':''}>${text}</label>`).join('')}</div>${choices.mode==='gps'?`<label class="pack-row"><span class="select-label">Offline places</span><select id="pack"><option value="">No pack · Observation-only story</option>${(health?.packs||[]).map(p=>`<option value="${e(p.id)}" ${choices.pack_id===p.id?'selected':''}>${e(p.name)}</option>`).join('')}</select></label>`:''}${choices.mode==='gps'?'<p class="hint">Each chapter uses your latest location and a named place within 100 m from the selected map pack. Import your area’s pack in Setup. Without one, the story uses general surroundings. Live location is required; Sample walk is available for laptop testing.</p>':''}<div id="start-error" role="alert" ${startError?'':'hidden'}><p>${e(startError)}</p>${choices.mode==='gps'?'<button type="button" class="secondary" id="try-sample">Try a sample walk</button>':''}</div><button class="primary wide" type="submit" ${disabled()}>${busy?'<span class="busy-dots">Opening your story…</span>':`Begin the walk ${arrow}`}</button><p class="hint center">${choices.mode==='sample'?'Sample route · No location needed':(health?.hosted?'Location is sent to your hosted Wanderlore server':'Location stays on your local devices')}</p><div class="engine-row"><label for="engine">Story</label><select id="engine"><option value="local" ${choices.engine==='local'?'selected':''} ${health?.model_ready&&(health?.voice_ready||choices.voice==='elevenlabs'&&health?.elevenlabs_ready)?'':'disabled'}>${health?.hosted?'Server AI':'Local AI'} · ${e(health?.model||'Ollama')}</option><option value="sample" ${choices.engine==='sample'?'selected':''}>Scripted preview</option></select></div><div class="engine-row"><label for="voice">Voice</label><select id="voice">${(health?.voices||[]).map(v=>`<option value="${e(v.id)}" ${choices.voice===v.id?'selected':''} ${v.available===false?'disabled':''}>${e(v.name)}${v.available===false?' · Set up first':''}</option>`).join('')}</select></div><div class="voice-preview"><button type="button" class="plain" id="preview-voice" ${(choices.voice==='elevenlabs'?health?.elevenlabs_ready:health?.voice_ready)?'':'disabled'}>Preview voice</button><span class="hint" id="voice-notice">${voiceNotice()}</span></div><audio id="voice-sample" controls hidden aria-label="Voice preview"></audio></form></div></section>`;
 mountScene(choices.weather);
 if(busy)app.querySelectorAll('#walk-form button,#walk-form input,#walk-form select').forEach(el=>el.disabled=true);
 app.querySelectorAll('[data-genre]').forEach(b=>b.onclick=()=>{choices.genre=b.dataset.genre;home()});
 app.querySelectorAll('[name=mode]').forEach(r=>r.onchange=()=>{choices.mode=r.value;startError='';home()});
 for(const id of ['minutes','weather','engine','voice','pack']){const el=document.getElementById(id);if(el)el.onchange=()=>{choices[id==='pack'?'pack_id':id]=id==='minutes'?Number(el.value):el.value||null;if(id==='voice'){localStorage.setItem('wanderlore-voice',choices.voice);home();return}if(id==='weather'){localStorage.setItem('wanderlore-weather',choices.weather);setSceneWeather(choices.weather)}if(id==='pack'){if(choices.pack_id)localStorage.setItem('wanderlore-pack',choices.pack_id);else localStorage.removeItem('wanderlore-pack')}}}
 document.querySelector('#preview-voice').onclick=async()=>{
  const button=document.querySelector('#preview-voice'),player=document.querySelector('#voice-sample');
  button.disabled=true;button.textContent='Preparing voice…';player.pause();
  try{const result=await send(`/voices/${choices.voice}/preview`,{});player.src=result.audio_url;player.hidden=false;await player.play()}
  catch(error){report(error)}
  finally{button.disabled=false;button.textContent='Preview voice'}
 };
 document.querySelector('#try-sample')?.addEventListener('click',()=>{choices.mode='sample';startError='';home();start().catch(report)});
 document.querySelector('#resume-saved')?.addEventListener('click',()=>resumeSaved(resumeId).catch(report));
 document.querySelector('#walk-form').onsubmit=event=>{event.preventDefault();start().catch(report)};
}
function locationError(code){
 const help=' On this Mac, check System Settings → Privacy & Security → Location Services and the browser’s location permission. If the in-app browser cannot provide a position, open this same address in Safari or Chrome.';
 if(code===1)return new Error('Location access was denied or blocked.'+help);
 if(code===3)return new Error('Location timed out before the browser could find your position. Retry with Wi-Fi enabled, or use Sample walk to test the story.'+help);
 return new Error('The browser could not determine your current position. The Lucknow map contains places, but cannot locate you. Enable Wi-Fi and Location Services, then retry.'+help);
}
async function getFix(){
 // Reuse only a recent, accurate real reading, including the initial fix.
 if(fix && fix.accuracy<=80 && Date.now()/1000-fix.timestamp>=0 && Date.now()/1000-fix.timestamp<15)return fix;
 if(!window.isSecureContext)throw new Error('Live location needs HTTPS on a phone, or localhost on this laptop. Open the HTTPS address or choose Sample walk.');
 if(!navigator.geolocation)throw new Error('This browser does not support location. Open this address in Safari or Chrome, or choose Sample walk.');
 const request=high=>new Promise((resolve,reject)=>navigator.geolocation.getCurrentPosition(p=>resolve({lat:p.coords.latitude,lon:p.coords.longitude,accuracy:p.coords.accuracy,timestamp:p.timestamp/1000}),reject,{enableHighAccuracy:high,maximumAge:0,timeout:15000}));
 try{return await request(true)}catch(err){
  if(err.code===1)throw locationError(1);
  // Some desktop providers work better without the high-accuracy preference.
  // The existing 80 m accuracy check still applies to this real position.
  try{return await request(false)}catch(retry){throw locationError(retry.code)}
 }
}

function stopTracking(){if(watchId!==null)navigator.geolocation.clearWatch(watchId);watchId=null}
function track(){
 stopTracking();if(walk?.mode!=='gps'||walk?.status!=='active')return;
 watchId=navigator.geolocation.watchPosition(p=>{fix={lat:p.coords.latitude,lon:p.coords.longitude,accuracy:p.coords.accuracy,timestamp:p.timestamp/1000};if(fix.accuracy<=80&&!busy)send(`/walks/${walk.id}/position`,fix).catch(report)},err=>message('Location paused. Keep the browser open and check location permission.'),{enableHighAccuracy:true,maximumAge:5000,timeout:20000});
}
async function lockScreen(){try{if('wakeLock'in navigator)wake=await navigator.wakeLock.request('screen')}catch{}}
function beginClock(){clearInterval(elapsedTimer);elapsedTimer=setInterval(()=>{if(walk?.status==='active'){elapsed++;const el=document.querySelector('#elapsed');if(el)el.textContent=clock(elapsed);if(elapsed%15===0&&!busy)send(`/walks/${walk.id}`,{duration_seconds:elapsed},'PATCH').catch(()=>{})}},1000)}
function unlockAudio(){audio.src='/silence.wav';audio.play().catch(()=>{})}
async function start(){
 if(busy)return;busy=true;startError='';message('');unlockAudio();home();
 try{
  await refreshHealth();
  if(choices.mode==='gps'){fix=await getFix();if(fix.accuracy>80)throw new Error('Location is not accurate enough yet. Try outside or use the sample route.')}
  walk=await send('/walks',choices);elapsed=0;pack=walk.pack_id?await api(`/packs/${walk.pack_id}`):null;
  localStorage.setItem('wanderlore-active',walk.id);currentAudio=null;auto=false;requestId=null;
  await lockScreen();track();beginClock();busy=false;renderWalk();document.querySelector('#walk-panel').scrollIntoView({block:'start'});await next();
 }catch(err){busy=false;if(walk?.status==='active'){renderWalk();throw err}else{startError=err.message||'The walk could not start. Please retry.';home();document.querySelector('#start-error').scrollIntoView({block:'center',behavior:'instant'})}}
}
function schedule(){
 stopTimer();if(!auto||walk?.status!=='active'||busy||walk?.beats.at(-1)?.final||walk?.beats.at(-1)?.choices?.length)return;
 const delay=audio.src&&!audio.ended&&!audio.paused?1000:50000;
 autoTimer=setTimeout(()=>{if(!auto||walk?.status!=='active')return;if(!audio.paused&&!audio.ended){schedule();return}next(true).catch(report)},delay);
}
async function next(automatic=false,closing=false,choiceId=null){
 if(busy||!walk||walk.status!=='active')return;busy=true;stopTimer();audio.pause();message('');renderWalk();
 try{
  if(walk.mode==='gps')fix=await getFix();
  if(!requestId){requestId=crypto.randomUUID();pendingChoice=choiceId}
  const result=await send(`/walks/${walk.id}/beats`,{request_id:requestId,choice_id:pendingChoice,fix:walk.mode==='gps'?fix:null,automatic,final:closing||elapsed>=walk.minutes*60,hour:new Date().getHours()});
  if(result.waiting){requestId=null;message(result.reason);busy=false;renderWalk();schedule();return}
  requestId=null;walk=result.walk;currentAudio=result.beat.audio_url;
  if(document.hidden){auto=false;walk=await send(`/walks/${walk.id}`,{status:'paused',duration_seconds:elapsed},'PATCH')}
  busy=false;renderWalk();
  if(currentAudio){audio.src=currentAudio;try{if(walk.status==='active')await audio.play()}catch{message('Your chapter is ready. Press play to listen.')}}
  else message('This is a read-along preview. Install the Kokoro voice in Setup for spoken chapters.');
  schedule();
 }catch(err){busy=false;auto=false;renderWalk();throw err}
}
function renderWalk(){
 document.body.classList.add("landing");
 if(!walk)return;const b=walk.beats.at(-1),finished=walk.status==='finished',paused=walk.status==='paused';
 const content=`<section class="active-grid"><div><p class="chapter-meta">${finished?'A WALK TO REMEMBER':`CHAPTER ${String(b?.number||1).padStart(2,'0')}`} · ${e(walk.genre)} · ${walk.engine==='local'?(health?.hosted?'SERVER AI':'LOCAL AI'):'SCRIPTED PREVIEW'}</p><h2 id="walk-title" tabindex="-1">${e(b?.title||'Your story is taking shape.')}</h2>${b?.sources?.length?`<details class="chapter-list"><summary>Place context sources</summary>${b.sources.map(source=>`<p>${e(source.text)} <a href="${e(source.source_url)}" target="_blank" rel="noopener noreferrer">Source</a></p>`).join('')}</details>`:''}${b?.decision?`<p class="chosen-path">You chose: ${e(b.decision.label)}</p>`:''}<p class="story-text">${b?e(b.text):'The path is quiet for a moment. Your first chapter is on its way.'}</p><div class="playback"><div class="player-slot" id="player-slot"></div><p class="hint">${b?`${b.feature?e(b.feature.name)+(walk.mode==='sample'?' · Fictional sample place':` · ${b.feature.distance_m} m away`):'No named place nearby · Observation-only chapter'}${b.audio_url?` · Ready in ${(b.generation_ms/1000).toFixed(1)} s`:''}`:''}</p>${!finished&&b?.choices?.length&&!b.final?`<fieldset class="story-choices" ${busy||paused?'disabled':''}><legend>What happens next?</legend><p class="hint">Choose a turn in the tale, or use Next chapter to leave it to the storyteller.</p>${b.choices.map(c=>`<button class="story-choice" data-choice="${e(c.id)}" type="button">${e(c.label)}<span aria-hidden="true">↗</span></button>`).join('')}</fieldset>`:''}${!finished?`<div class="actions"><button class="secondary" id="pause" ${disabled()}>${paused?'Resume walk':'Pause walk'}</button><button class="primary" id="next" ${busy||paused||b?.final?'disabled':''}>${busy?'<span class="busy-dots">Writing & voicing…</span>':`Next chapter ${arrow}`}</button></div><div class="walk-tools"><label class="auto"><input id="auto" type="checkbox" ${auto?'checked':''} ${disabled()}>Continue automatically</label><span class="timer" id="elapsed">${clock(elapsed)}</span></div><p class="hint">${auto?(b?.choices?.length?'Waiting for your choice. Select an option or press Next chapter.':'A new chapter follows after a quiet pause. Keep this tab visible.'):'Take your time. Continue whenever you’re ready.'}</p><div class="walk-tools"><button class="plain" id="closing" ${busy||paused||!b||b.final?'disabled':''}>Write the closing chapter</button><button class="plain" id="finish" ${disabled()}>Finish & save</button></div>`:`<div class="recap"><label class="label" for="notes">WHAT DID YOU NOTICE?</label><textarea class="notes" id="notes" placeholder="A sound, a detail, a moment worth keeping…">${e(walk.notes)}</textarea><div class="saved-note" id="note-status"></div><div class="actions"><button class="secondary" id="save-notes">Save reflection</button><a class="secondary" href="/api/walks/${walk.id}/export" download>Export walk</a></div></div>`}</div><details class="chapter-list"><summary>${walk.beats.length} ${walk.beats.length===1?'chapter':'chapters'} in this walk</summary>${walk.beats.map(x=>`<article class="chapter-item"><strong>${x.number}. ${e(x.title)}</strong>${x.decision?`<p class="chosen-path">You chose: ${e(x.decision.label)}</p>`:''}<p>${e(x.text)}</p>${x.audio_url?`<button class="plain" data-replay="${e(x.audio_url)}">Listen again</button>`:''}</article>`).join('')}</details><p class="privacy-note">${walk.mode==='sample'?'This walk uses a simulated route.':(health?.hosted?'GPS and stories are stored on your hosted Wanderlore server.':'GPS and story data stay on this laptop and your connected device.')} ${walk.voice==='elevenlabs'?'Chapter text is sent to ElevenLabs for narration.':''} The story is fiction.</p></div><div>${mapMarkup(walk,pack)}${finished?`<p class="hint">${clock(walk.duration_seconds)} spent wandering · ${walk.beats.length} chapters saved</p><button class="plain" id="new-walk">Start a new story ${arrow}</button>`:'<p class="hint">Let the world set the pace. The sketch records your walk; it does not give directions.</p>'}</div></section>`;
 if(!document.querySelector('.landing-scene'))app.innerHTML=sceneMarkup();
 document.querySelector('#prepare')?.remove();document.querySelector('.resume-banner')?.remove();
 let panel=document.querySelector('#walk-panel');
 if(!panel){panel=document.createElement('section');panel.id='walk-panel';panel.setAttribute('aria-label','Your walking story');app.append(panel)}
 panel.innerHTML=content;mountScene(walk.weather);
 panel.querySelectorAll('[data-choice]').forEach(button=>button.onclick=()=>{requestId=null;next(false,false,button.dataset.choice).catch(report)});
 audio.controls=true;audio.hidden=!currentAudio;document.querySelector('#player-slot').append(audio);
 document.querySelector('#pause')?.addEventListener('click',()=>togglePause().catch(report));
 document.querySelector('#next')?.addEventListener('click',()=>next().catch(report));
 document.querySelector('#closing')?.addEventListener('click',()=>next(false,true).catch(report));
 document.querySelector('#finish')?.addEventListener('click',()=>finish().catch(report));
 document.querySelector('#auto')?.addEventListener('change',event=>{auto=event.target.checked;schedule()});
 document.querySelector('#save-notes')?.addEventListener('click',async()=>{try{walk=await send(`/walks/${walk.id}`,{notes:document.querySelector('#notes').value},'PATCH');document.querySelector('#note-status').textContent='Reflection saved on this laptop.'}catch(err){report(err)}});
 document.querySelector('#new-walk')?.addEventListener('click',()=>{audio.pause();walk=null;currentAudio=null;message('');location.hash='#walk';home()});
 app.querySelectorAll('[data-replay]').forEach(el=>el.onclick=()=>{currentAudio=el.dataset.replay;audio.src=currentAudio;audio.hidden=false;audio.play().catch(()=>message('Press play to listen.'))});
}
async function togglePause(){
 const status=walk.status==='paused'?'active':'paused';
 if(status==='paused'){audio.pause();stopTimer();stopTracking();await wake?.release().catch(()=>{})}
 walk=await send(`/walks/${walk.id}`,{status,duration_seconds:elapsed},'PATCH');renderWalk();
 if(status==='active'){message('');track();lockScreen();if(!walk.beats.length){await next();return}if(currentAudio&&!audio.ended)audio.play().catch(()=>{});schedule()}
}
async function finish(){
 if(busy)return;audio.pause();stopTimer();stopTracking();clearInterval(elapsedTimer);auto=false;
 walk=await send(`/walks/${walk.id}`,{status:'finished',duration_seconds:elapsed},'PATCH');
 if(localStorage.getItem('wanderlore-active')===walk.id)localStorage.removeItem('wanderlore-active');
 await wake?.release().catch(()=>{});message('Your walk is saved. Leave yourself a small memory.');renderWalk();
}
async function resumeSaved(id){
 walk=await api(`/walks/${id}`);pack=walk.pack_id?await api(`/packs/${walk.pack_id}`):null;elapsed=walk.duration_seconds;currentAudio=walk.beats.at(-1)?.audio_url||null;
 if(currentAudio)audio.src=currentAudio;auto=false;
 if(walk.status==='active')walk=await send(`/walks/${id}`,{status:'paused'},'PATCH');
 if(walk.status==='finished'){if(localStorage.getItem('wanderlore-active')===walk.id)localStorage.removeItem('wanderlore-active')}
 else localStorage.setItem('wanderlore-active',walk.id);
 beginClock();renderWalk();document.querySelector('#walk-panel').scrollIntoView({block:'start'});
}
async function journal(){
 if(walk?.status==='active')await togglePause();audio.pause();stopTimer();
 document.body.classList.remove('landing');
 const walks=await api('/walks');
 app.innerHTML=`<section class="journal"><div class="journal-head"><h1>My walks</h1><a class="secondary" href="#walk">Your walk ${arrow}</a></div>${walks.length?walks.map(w=>`<a class="walk-row" href="#journal/${w.id}"><div><h3>${e(w.title)}</h3><p>${w.chapters} chapters · ${e(label(w.genre))} · ${w.mode==='sample'?'Sample route':'GPS walk'} · ${w.engine==='sample'?'Scripted preview':'Local AI'}</p><p>${e(new Date(w.created).toLocaleDateString(undefined,{day:'numeric',month:'short',year:'numeric'}))} · ${e(w.status)}</p></div>${arrow}</a>`).join(''):'<div class="empty"><h3>Your first story is still unwritten.</h3><p>Take a little walk. The places you notice and the chapters you hear will live here.</p><a class="primary" href="#walk">Begin a story '+arrow+'</a></div>'}</section>`;
}
async function route(){
 if(busy){history.replaceState(null,'','#walk');message('Let this chapter finish before switching pages.');return}
 message('');const hash=location.hash||'#walk';document.querySelector('#nav-walk').classList.toggle('active',hash==='#walk');document.querySelector('#nav-journal').classList.toggle('active',hash.startsWith('#journal'));
 if(hash==='#home'){
  if(walk?.status==='active')await togglePause();
  audio.pause();stopTimer();stopTracking();clearInterval(elapsedTimer);
  if(wake){await wake.release().catch(()=>{});wake=null}
  walk=null;home();window.scrollTo(0,0);
 }
 else if(hash.startsWith('#journal/')){if(walk?.status==='active')await togglePause();await resumeSaved(hash.split('/')[1])}
 else if(hash==='#journal')await journal();
 else if(walk)renderWalk();else home();
}
async function setup(){
 dialog.showModal();const content=document.querySelector('#setup-content');content.innerHTML='<p>Checking the local narrator…</p>';
 try{await refreshHealth();content.innerHTML=`<div class="setup-status"><div class="status-line"><span>Open-weight narrator</span><strong class="${health.model_ready?'ready':'not-ready'}">${e(health.model)} · ${health.model_ready?'Ready':'Not installed'}</strong></div><div class="status-line"><span>Kokoro voice</span><strong class="${health.voice_ready?'ready':'not-ready'}">${health.voice_ready?'Ready':'Not installed'}</strong></div><div class="status-line"><span>Saved map packs</span><strong>${health.packs.length}</strong></div></div><p class="setup-copy">For local setup, run <code>./scripts/setup.sh</code> in the project folder. Local voices work offline after download; ElevenLabs needs internet. Keep your Wanderlore server running.</p><h3>Connected services</h3><div class="setup-status">${Object.entries({'ElevenLabs voice':health.integrations?.elevenlabs?'Configured · select Online narration':'Not configured','Sentry traces':health.integrations?.sentry?'Enabled · timing and model metadata only':'Off','Tiger Data place context':health.integrations?.tiger_data?'Offline export loaded':'No export installed','Hosting':health.hosted?'Hosted mode':'Local mode'}).map(([name,status])=>`<div class="status-line"><span>${e(name)}</span><strong>${e(status)}</strong></div>`).join('')}</div><p class="setup-copy">Optional services are configured on the server. Never enter API keys in this page. Entire records development sessions separately. Configuration is not a connection test.</p><h3>Bring your own places</h3><p class="setup-copy">Import a GeoJSON FeatureCollection (up to 8 MB). OSM map packs can be prepared with <code>scripts/prepare_map.py</code>. No map requests happen during a walk.</p><label for="pack-file" class="select-label">Choose a GeoJSON map pack</label><input type="file" id="pack-file" accept=".json,.geojson,application/json"><p id="pack-status" class="setup-copy"></p><p class="setup-copy">Phone testing needs trusted HTTPS for location. Start with the sample walk on this laptop.</p>`;
 document.querySelector('#pack-file').onchange=async event=>{try{const file=event.target.files[0];if(!file)return;if(file.size>8_000_000)throw new Error('Choose a pack smaller than 8 MB.');const data=JSON.parse(await file.text());const added=await send('/packs',{name:file.name.replace(/\.(geo)?json$/,''),geojson:data});await refreshHealth();document.querySelector('#pack-status').textContent=`${added.features} places imported. Choose the pack under Use my location.`;if(!walk)home()}catch(err){document.querySelector('#pack-status').textContent=err.message}};
 }catch(err){content.innerHTML=`<p>${e(err.message)}</p><form id="pair-form"><label for="pair-code">Private access code</label><input id="pair-code" type="password" required autocomplete="off"><p class="hint">For hosted access, use the server’s WANDERLORE_PAIR_CODE. For local access, read data/pairing-code on your laptop.</p><button class="primary">Pair device</button></form>`;document.querySelector('#pair-form').onsubmit=async event=>{event.preventDefault();try{await send('/pair',{code:document.querySelector('#pair-code').value});dialog.close();await init()}catch(err){report(err)}}}
}
window.addEventListener('hashchange',()=>route().catch(report));
window.addEventListener('pagehide',()=>{if(walk?.status==='active')fetch(`/api/walks/${walk.id}`,{method:'PATCH',headers:{'Content-Type':'application/json'},body:JSON.stringify({status:'paused',duration_seconds:elapsed}),keepalive:true}).catch(()=>{})});
document.addEventListener('visibilitychange',()=>{if(document.hidden&&walk?.status==='active'){auto=false;stopTimer();audio.pause();togglePause().then(()=>message('Walk paused while the page was hidden. Resume when you’re ready.')).catch(report)}});
document.querySelector('#setup-button').onclick=()=>setup().catch(report);dialog.querySelector('.close').onclick=()=>dialog.close();
audio.addEventListener('ended',schedule);
audio.addEventListener('error',()=>{if(currentAudio)message('Audio could not load. Keep the laptop connected, then press Listen again.')});
async function init(){
 app.innerHTML='<p class="loading">Finding the beginning…</p>';
 try{await refreshHealth();if(!health.voices?.some(v=>v.id===choices.voice&&v.available!==false))choices.voice=health.voices?.find(v=>v.available!==false)?.id||'af_heart';choices.engine=health.model_ready&&(health.voice_ready||choices.voice==='elevenlabs'&&health.elevenlabs_ready)?'local':'sample';await route()}
 catch(err){home();report(err)}
 if('serviceWorker'in navigator)navigator.serviceWorker.register('/sw.js').catch(()=>{});
}
init();
