const CACHE='wanderlore-shell-v21';
const ASSETS=['/','/index.html','/style.css','/scene.css','/scene.js','/sunset-forest.png','/app.js','/api.js','/map.js','/woodland.png','/icon.svg','/manifest.webmanifest','/silence.wav'];
self.addEventListener('install',event=>{event.waitUntil(caches.open(CACHE).then(cache=>cache.addAll(ASSETS)));self.skipWaiting()});
self.addEventListener('activate',event=>event.waitUntil(caches.keys().then(keys=>Promise.all(keys.filter(k=>k!==CACHE).map(k=>caches.delete(k)))).then(()=>self.clients.claim())));
self.addEventListener('fetch',event=>{const url=new URL(event.request.url);if(url.origin!==location.origin||url.pathname.startsWith('/api/')||url.pathname.startsWith('/audio/')||event.request.method!=='GET')return;event.respondWith(fetch(event.request).catch(()=>caches.match(event.request).then(r=>r||caches.match('/'))))});
