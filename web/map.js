import {escape} from './api.js';
const sample=[[-.1582,51.5298],[-.1573,51.5306],[-.1564,51.5316],[-.1554,51.5321],[-.1542,51.5314],[-.1533,51.5307]];
export function mapMarkup(walk=null,pack=null){
 const demo=!walk||walk.mode==='sample';
 const positions=(walk?.positions||[]).map(p=>[p.lon,p.lat]);
 const all=demo?sample:positions;
 const points=all.length?all:[[0,0]];
 let minX=Math.min(...points.map(p=>p[0])),maxX=Math.max(...points.map(p=>p[0])),minY=Math.min(...points.map(p=>p[1])),maxY=Math.max(...points.map(p=>p[1]));
 const midY=(minY+maxY)/2,cos=Math.cos(midY*Math.PI/180);
 const span=Math.max((maxX-minX)*cos,(maxY-minY)*1.5,.0018);
 const midX=(minX+maxX)/2;
 const project=p=>[380+(p[0]-midX)*cos/span*570,250-(p[1]-midY)/span*570];
 const path=ps=>ps.map((p,i)=>`${i?'L':'M'}${project(p).map(x=>x.toFixed(1)).join(',')}`).join(' ');
 let features='';
 if(!demo&&pack)for(const f of pack.features||[]){const g=f.geometry,c=g.coordinates;
  if(g.type==='Point'){const [x,y]=project(c);if(x>=0&&x<=760&&y>=0&&y<=500)features+=`<circle cx="${x}" cy="${y}" r="3" fill="#84937b"/><text x="${x+8}" y="${y-7}" class="map-place">${escape(f.properties?.name||'')}</text>`}
  else {let lines=g.type==='LineString'?[c]:g.type==='Polygon'||g.type==='MultiLineString'?c:[]; for(const line of lines)features+=`<path d="${path(line)}" class="geo-line"/>`}
 }
 const route=demo?path(sample):path(positions);
 const markers=walk?.beats?.length?walk.beats.map(b=>({p:[b.position.lon,b.position.lat],n:b.number})):demo?[{p:sample[0],n:1},{p:sample[2],n:2},{p:sample[5],n:3}]:[];
 return `<div class="map-frame"><span class="map-heading">THE STORY SO FAR</span><svg class="route-map" viewBox="0 0 760 500" role="img" aria-label="${demo?'Illustrative sample route with fictional place names':'Your recorded route; not a navigation map'}"><defs><pattern id="grid" width="38" height="38" patternUnits="userSpaceOnUse"><path d="M38 0H0V38" fill="none" stroke="#adb7a5" stroke-width=".5" opacity=".35"/></pattern></defs><rect width="760" height="500" fill="var(--sage)"/><rect width="760" height="500" fill="url(#grid)"/>${demo?`<g class="contours"><path d="M-20 75Q110 150 230 30T580 100T800 50"/><path d="M-20 100Q120 180 255 55T580 130T800 85"/><path d="M-20 125Q110 205 260 80T600 160T800 110"/><path d="M-10 410Q110 285 230 370T480 420T800 350"/><path d="M-10 435Q110 310 240 395T500 445T800 375"/><path d="M-10 460Q110 335 240 420T500 470T800 400"/></g><path d="M345 -20C280 100 430 170 378 280S410 405 340 520" class="river"/><path d="M-10 220C170 300 100 80 260 130S490 280 780 215M90 510Q70 330 225 335T530 325T700 -10" class="trail"/><text x="92" y="204" class="map-place">Riverside</text><text x="92" y="223" class="map-place">Meadow</text><text x="462" y="125" class="map-place">Mossy Wood</text><text x="600" y="277" class="map-place">Old Stone</text><text x="600" y="296" class="map-place">Lane</text><text x="380" y="455" class="map-place">Willow Brook</text>`:features}
 ${route?`<path d="${route}" class="route-under"/><path d="${route}" class="route-path"/>`:''}${markers.map(({p,n})=>{const [x,y]=project(p);return `<circle cx="${x}" cy="${y}" r="14" fill="var(--ink)" stroke="var(--paper)" stroke-width="2"/><text x="${x}" y="${y+5}" text-anchor="middle" class="marker">${n}</text>`}).join('')}
 <g transform="translate(715 438)"><text y="-12" text-anchor="middle" class="map-place">N</text><path d="M0 0L-6 20L0 16L6 20Z" fill="none" stroke="var(--ink)" stroke-width="1.5"/></g></svg><div class="map-caption">${demo?'A sample path, ready to explore.':positions.length?'Your footsteps, one chapter at a time.':'Your route will appear as you walk.'}</div><span class="map-credit">${demo?'Illustrative route · Fictional places':pack?escape(pack.attribution||'Imported GeoJSON')+' · Route sketch':'Route sketch · No map pack loaded'}</span></div>`;
}
