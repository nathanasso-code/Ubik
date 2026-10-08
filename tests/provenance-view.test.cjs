const assert=require("node:assert/strict");
const provenance=require("../assets/provenance-view.js");
const claims=[
 {id:"c1",evidence_lines:[{id:"l1",independence:"unknown"}],dependencies:[],origins:[{id:"o1",label:"Reuters"}]},
 {id:"c2",evidence_lines:[{id:"l2",independence:"dependent"},{id:"l3",independence:"unknown"}],dependencies:[{from:"o2",to:"o1"}]}
];
assert.deepEqual(provenance.summarizeClaims(claims),{claims:2,lines:3,dependencies:1,unknown:true});
assert.deepEqual(provenance.summarizeClaims([]),{claims:0,lines:0,dependencies:0,unknown:false});
assert.equal(provenance.safeSourceLink("javascript:alert(1)"),null);
assert.equal(provenance.safeSourceLink("https://example.org/path"),"https://example.org/path");
assert.equal(provenance.safeSourceLink("not-a-url"),null);
console.log("Provenance pure helpers: 5 assertions passed");
