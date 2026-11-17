import { LIB } from '../templates/motion_styles/library.mjs';
import path from 'node:path';
const root=path.resolve('templates/motion_styles/moves');
const mods=[...new Set(LIB.map(x=>x.module.split('#')[0]))];
const ch={form:'standard',bodyTop:333,bodyBot:640,ground:900,K:1.5,hipY:610,legL:300,sh:[120,430],armL:250,handX:120,hipW:13};
const issues=[]; let styles=0,samples=0;
function scan(v,p,issue){if(typeof v==='number'&&!Number.isFinite(v))issue(p+' non-finite'); else if(Array.isArray(v))v.forEach((x,i)=>scan(x,p+'['+i+']',issue)); else if(v&&typeof v==='object')Object.entries(v).forEach(([k,x])=>scan(x,p+'.'+k,issue));}
for(const mn of mods){let mod;try{mod=await import(path.toNamespacedPath(path.join(root,mn+'.mjs')))}catch(e){issues.push({module:mn,err:'import '+e.message});continue;}
 let exs=[['default',mod.default],...Object.entries(mod).filter(([k,v])=>k!=='default'&&v&&Array.isArray(v.styles)).map(([k,v])=>[k,v])];
 for(const [ex,v] of exs){if(!v||!Array.isArray(v.styles))continue;for(const st of v.styles){styles++;for(const t of [0,.033,.1,(v.dur||6)*.25,(v.dur||6)*.5,(v.dur||6)*.75,(v.dur||6)-.033,v.dur||6]){samples++;try{const p=st.pose(t,ch);const bad=[];scan(p,st.key,(s)=>bad.push(s));if(!p||typeof p!=='object')issues.push({module:mn,style:st.key,t,err:'non-object pose'});if(p&&p.view&&!['side','front','34','back'].includes(p.view))issues.push({module:mn,style:st.key,t,err:'invalid view '+p.view});if(bad.length)issues.push({module:mn,style:st.key,t,err:bad.slice(0,5).join(', ')});if(p&&p.feet){for(const [i,ft] of p.feet.entries()){if(typeof ft.x!=='number'||typeof ft.lift!=='number'&&ft.lift!==undefined)issues.push({module:mn,style:st.key,t,err:`foot ${i} malformed`});}}}catch(e){issues.push({module:mn,style:st.key,t,err:e.message});}}}}
}
console.log(JSON.stringify({modules:mods.length,libraryEntries:LIB.length,styles,samples,issues:issues.length,first:issues.slice(0,40)},null,2));
