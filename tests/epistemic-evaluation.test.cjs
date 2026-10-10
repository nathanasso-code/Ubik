const assert=require("node:assert/strict");
const {score}=require("../assets/epistemic-evaluation.cjs");
const data=[
 {id:"a",title:"Release",url:"https://a.example/1",topicId:"ai",eventKey:"release"},
 {id:"b",title:"Syndicated release",url:"https://b.example/1",topicId:"ai",eventKey:"release",originId:"a"},
 {id:"c",title:"Different event",url:"https://c.example/1",topicId:"ai",eventKey:"benchmark"},
 {id:"d",title:"Benchmark follow-up",url:"https://d.example/1",topicId:"ai",eventKey:"benchmark"}
];
const expected=[["a","b"],["c","d"]];
const perfect=score(data,expected,[{id:"n1",clusterIds:["cluster:ai:benchmark"],state:"published",debate:"disabled"}]);
assert.equal(perfect.falseMerges,0);
assert.equal(perfect.missedMerges,0);
assert.equal(perfect.pairPrecision,1);
assert.equal(perfect.pairRecall,1);
assert.deepEqual(perfect.missingProvenance,[]);
assert.equal(perfect.nucleiCreated,0);
assert.equal(perfect.nucleusIdentityPreserved,true);
const bad=score(data.map(x=>x.id==="c"?{...x,eventKey:"release"}:x),expected);
assert.equal(bad.falseMerges,2);
assert.equal(bad.missedMerges,1);
assert.equal(bad.pairPrecision,1/3);
assert.equal(bad.pairRecall,1/2);
assert.deepEqual(bad.falseMergePairs,[["a","c"],["b","c"]]);
assert.deepEqual(bad.missedMergePairs,[["c","d"]]);
assert.throws(()=>score(data,[["a","b"],["c"]]),/cover/);
assert.throws(()=>score(data,[["a","b"],["b","c","d"]]),/duplicate/);
assert.throws(()=>score(data,[["a","b"],["c","unknown"]]),/Invalid/);
console.log("Epistemic clustering evaluation checks passed");
