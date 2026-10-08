/* Shared provenance presentation. No dependency on attack-specific records. */
(function(root){
"use strict";
function list(value){return Array.isArray(value)?value:[]}
function summarizeClaims(claims){
 const items=list(claims);
 return {claims:items.length,lines:items.reduce((n,c)=>n+list(c.evidence_lines).length,0),
 dependencies:items.reduce((n,c)=>n+list(c.dependencies).length,0),
 unknown:items.some(c=>list(c.evidence_lines).some(l=>!l.independence||l.independence==="unknown"))};
}
function label(value){return String(value||"").replace(/_/g," ")}
function element(tag,className,text){const e=document.createElement(tag);if(className)e.className=className;if(text!==undefined)e.textContent=String(text);return e}
function safeSourceLink(url){try{const u=new URL(url);return ["https:","http:"].includes(u.protocol)?u.href:null}catch{return null}}
function appendClaims(parent,record){
 const claims=list(record&&record.claims);if(!claims.length)return null;
 const summary=summarizeClaims(claims);
 const btn=element("button","provbtn","PROVENIENZA · "+summary.claims+" "+(summary.claims===1?"AFFERMAZIONE":"AFFERMAZIONI")+" · "+summary.lines+" "+(summary.lines===1?"LINEA":"LINEE")+(summary.unknown?" · INDIPENDENZA DA RICOSTRUIRE":summary.dependencies?" · DIPENDENZE PRESENTI":""));
 btn.type="button";btn.setAttribute("aria-expanded","false");
 const panel=element("div","provenance");panel.hidden=true;
 const id="ubik-provenance-"+(++appendClaims.serial);panel.id=id;btn.setAttribute("aria-controls",id);
 for(const claim of claims){
  const section=element("section","provclaim-group");
  section.appendChild(element("div","provclaim",claim.text||"Affermazione senza testo"));
  const origins=list(claim.origins),lines=list(claim.evidence_lines);
  const stats=element("div","provstats");
  for(const text of [lines.length+" linee informative",origins.length+" origini",list(claim.republications).length+" riprese",list(claim.revisions).length+" revisioni"])stats.appendChild(element("span","",text));
  section.appendChild(stats);
  for(const line of lines){
   const row=element("div","provline"+(!line.independence||line.independence==="unknown"?" provunknown":""));
   const originNames=list(line.origin_ids).map(id=>origins.find(o=>o.id===id)?.label||id);
   row.appendChild(element("b","",originNames.join(" + ")||"Origine non identificata"));
   row.appendChild(document.createTextNode(" · "+label(line.type||"evidenza")+" · "+(line.independence==="unknown"||!line.independence?"indipendenza non accertata":label(line.independence))));
   section.appendChild(row);
  }
  for(const origin of origins){
   const url=safeSourceLink(origin.url);if(!url)continue;
   const row=element("div","provline");const link=element("a","",origin.label||"Fonte originale");link.href=url;link.target="_blank";link.rel="noopener noreferrer";row.appendChild(link);section.appendChild(row);
  }
  for(const dep of list(claim.dependencies)){
   const from=origins.find(o=>o.id===dep.from)?.label||dep.from||"Origine sconosciuta";
   const to=origins.find(o=>o.id===dep.to)?.label||dep.to||"Origine sconosciuta";
   section.appendChild(element("div","provline","DIPENDENZA · "+from+" → "+to+" · "+label(dep.relation||"dipende da")));
  }
  for(const revision of list(claim.revisions)){
   section.appendChild(element("div","provline","REVISIONE · "+(revision.date||revision.at||"data non specificata")+" · "+label(revision.reason||revision.note||revision.description||"aggiornamento registrato")));
  }
  panel.appendChild(section);
 }
 btn.addEventListener("click",()=>{const open=btn.getAttribute("aria-expanded")!=="true";btn.setAttribute("aria-expanded",String(open));panel.hidden=!open;panel.classList.toggle("on",open)});
 parent.append(btn,panel);return panel;
}
appendClaims.serial=0;
root.UbikProvenance=Object.freeze({summarizeClaims,appendClaims,safeSourceLink});
if(typeof module!=="undefined"&&module.exports)module.exports=root.UbikProvenance;
})(typeof globalThis!=="undefined"?globalThis:this);
