const assert=require("node:assert/strict");
const core=require("../assets/ubik-core.js");
const registry=core.createRegistry([
 {id:"attacks",title:"Attacchi",views:["map","timeline"],capabilities:["temporal-filter"]},
 {id:"research",title:"Ricerca",views:["sources"],capabilities:[]}
]);
assert.equal(registry.supports("attacks","map"),true);
assert.equal(registry.supports("research","map"),false);
assert.equal(registry.hasCapability("research","provenance"),true);
assert.equal(registry.hasCapability("attacks","temporal-filter"),true);
assert.equal(registry.get("unknown"),null);
assert.throws(()=>core.createRegistry([{id:"x",title:"X",views:["invented"]}]),/Unknown view/);
assert.throws(()=>core.createRegistry([{id:"x",title:"X"},{id:"x",title:"X"}]),/Duplicate/);
const original={id:"e1",date:"2026-10-07",sources:[{publisher:"Reuters",url:"https://reuters.com/example"}]};
const projected=core.projectEvent(original);
assert.equal(projected.kind,"event");
assert.equal(projected.schemaVersion,1);
assert.deepEqual(projected.sourceIds,["https://reuters.com/example"]);
assert.equal(original.kind,undefined);
console.log("Ubik Core contracts: 11 assertions passed");
