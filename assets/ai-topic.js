/* AI topic presentation: uses existing .view/.topichead/.tagcloud/.story/.sources conventions. */
(async function(){
"use strict";
const host=document.getElementById("aiTopicFeed"),cloud=document.getElementById("aiTagCloud");
if(!host||!cloud)return;
let data;
try{const r=await fetch("/data/ai-topic.json");if(!r.ok)throw Error("HTTP "+r.status);data=await r.json()}
catch(e){host.textContent="Corpus AI non disponibile: "+e.message;return}
const el=(tag,cls,txt)=>{const n=document.createElement(tag);if(cls)n.className=cls;if(txt!==undefined)n.textContent=txt;return n};
const link=(url,label)=>{const a=el("a","",label);a.href=url;a.target="_blank";a.rel="noopener noreferrer";return a};
const count=new Map();for(const s of data.sources)for(const t of s.tags)count.set(t,(count.get(t)||0)+1);
let active="";
function render(){
cloud.replaceChildren();
const all=el("span","topiclink",active?"Tutti i tag":"Tutte le fonti");all.tabIndex=0;all.setAttribute("role","button");all.onclick=()=>{active="";render()};all.onkeydown=e=>{if(e.key==="Enter")all.click()};cloud.append(all);
for(const [tag,n] of [...count].sort((a,b)=>b[1]-a[1])){const t=el("span","topiclink",tag+" · "+n);t.style.fontSize=(14+Math.min(n,9))+"px";if(tag===active)t.style.color="#b9ffca";t.tabIndex=0;t.setAttribute("role","button");t.onclick=()=>{active=active===tag?"":tag;render()};t.onkeydown=e=>{if(e.key==="Enter")t.click()};cloud.append(t)}
host.replaceChildren();
const shown=data.sources.filter(s=>!active||s.tags.includes(active));
const intro=el("div","sourceintro");intro.append(el("div","eyebrow","CORPUS · "+shown.length+" / "+data.sources.length+" FONTI ORIGINALI"),el("h2","",active?"Tag: "+active:"Fonti originali e prospettive"),el("p","dek","Le discussioni sono associate alla fonte primaria; bot e rilanci non aumentano il numero delle conferme indipendenti."));host.append(intro);
for(const s of shown){
 const section=el("section","story");const typ=el("div","type",s.category.toUpperCase()+" · FONTE "+s.number+" / 30");const title=el("h2");title.append(link(s.url,s.title+" ↗"));const author=el("div","date",s.author);const summary=el("p","",s.summary);section.append(typ,title,author,summary);
 const tags=el("div","relations");for(const t of s.tags)tags.append(el("span","node",t));section.append(tags);
 if(s.posts.length){const b=el("button","action",s.posts.length+" contribut"+(s.posts.length===1?"o":"i")+" Bluesky · mostra");b.type="button";b.setAttribute("aria-expanded","false");const box=el("div","sources");for(const p of s.posts){const item=el("div","src");item.append(el("div","type",p.kind.toUpperCase()+" · "+p.author),el("p","",p.summary),link(p.url,"Post originale ↗"));box.append(item)}b.onclick=()=>{const open=box.classList.toggle("on");b.setAttribute("aria-expanded",String(open));b.textContent=(open?"Nascondi":"Mostra")+" contributi Bluesky · "+s.posts.length};section.append(b,box)}
 host.append(section);
}
if(!active){const h=el("div","sourceintro");h.append(el("div","eyebrow","PISTE EMERSE DA BLUESKY"),el("h2","","Tre possibili sviluppi autonomi"),el("p","dek","Non equivalgono a notizie validate: sono piste collegate da verificare sulle fonti primarie."));host.append(h);
for(const x of data.related_candidates){const sec=el("section","story");const title=el("h2");title.append(link(x.url,x.title+" ↗"));sec.append(el("div","type","PISTA · DA VERIFICARE · "+x.author),title,el("p","",x.summary),el("div","linkage","Collegamento semantico: Financing the AI Buildout"));host.append(sec)}}
}
render();
})();
