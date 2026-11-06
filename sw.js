const C="trek-202611062c096b",FONTS="trek-fonts";
const ASSETS=["./","index.html","manifest.webmanifest","icon-192.png","icon-512.png","icon-maskable.png","apple-touch-icon.png","plans/1734c0361639c9b6332c.enc","plans/61a22679c0f365a6aed9.enc"];
self.addEventListener("install",e=>{e.waitUntil(caches.open(C).then(c=>c.addAll(ASSETS)).then(()=>self.skipWaiting()))});
self.addEventListener("activate",e=>{e.waitUntil(caches.keys().then(ks=>Promise.all(ks.filter(k=>k!==C&&k!==FONTS).map(k=>caches.delete(k)))).then(()=>self.clients.claim()))});
function fromNet(req){return fetch(req).then(r=>{if(r.ok){const cp=r.clone();caches.open(C).then(c=>c.put(req,cp))}return r})}
self.addEventListener("fetch",e=>{
  const req=e.request;if(req.method!=="GET")return;const u=new URL(req.url);
  if(u.origin===location.origin){
    // сначала сеть (чтобы обновления приходили), без сети или при медленной сети — сохранённая копия
    e.respondWith(new Promise(resolve=>{
      let done=false;const fallback=()=>caches.match(req,{ignoreSearch:true}).then(r=>r||(req.mode==="navigate"?caches.match("index.html"):null));
      const t=setTimeout(()=>{fallback().then(r=>{if(r&&!done){done=true;resolve(r)}})},4000);
      fromNet(req).then(r=>{clearTimeout(t);if(!done){done=true;resolve(r)}}).catch(()=>{clearTimeout(t);fallback().then(r=>{if(!done){done=true;resolve(r||Response.error())}})});
    }));
    return;
  }
  if(u.hostname==="fonts.googleapis.com"||u.hostname==="fonts.gstatic.com"){
    e.respondWith(caches.open(FONTS).then(c=>c.match(req).then(r=>r||fetch(req).then(n=>{c.put(req,n.clone());return n}))));
  }
});
