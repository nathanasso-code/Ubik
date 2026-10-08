const assert=require("node:assert/strict");
const fs=require("node:fs");
const path=require("node:path");
const root=path.join(__dirname,"..");
const html=fs.readFileSync(path.join(root,"index.html"),"utf8");
const app=fs.readFileSync(path.join(root,"assets/app.js"),"utf8");
const scripts=[...html.matchAll(/<script[^>]+src="([^"]+)"/g)].map(x=>x[1]);
for(const name of ["ubik-core","topic-registry","provenance-view","temporal","map-view","app"]){
 assert.equal(scripts.filter(x=>x==="/assets/"+name+".js").length,1,"Script included exactly once: "+name);
}
const order=["ubik-core","topic-registry","provenance-view","temporal","map-view","app"].map(name=>scripts.indexOf("/assets/"+name+".js"));
assert.deepEqual(order,[...order].sort((a,b)=>a-b),"Dependency loading order");
assert.match(app,/UbikTemporal\.createTemporalState\(\)/);
assert.match(app,/UbikMap\.createMap\(/);
assert.match(app,/UbikProvenance\.appendClaims\(/);
assert.doesNotMatch(app,/let\s+attackMap\s*=\s*L\.map\(/);
assert.doesNotMatch(app,/\btimeFrom\s*=\s*["']/);
assert.doesNotMatch(app,/\btimeTo\s*=\s*["']/);
assert.match(html,/id="attackMap"/);
assert.match(html,/id="timelineBars"/);
assert.match(html,/id="globalSearch"/);
console.log("Static integration checks passed");
