const assert=require("node:assert/strict");
const {evaluate}=require("../assets/epistemic-pilot.cjs");
const observations=[
 {id:"s1",title:"Announcement",url:"https://lab.example/new",topicId:"ai",eventKey:"release-1"},
 {id:"s2",title:"Same announcement",url:"https://news.example/release",topicId:"ai",eventKey:"release-1",originId:"s1"},
 {id:"s3",title:"Different benchmark study",url:"https://research.example/bench",topicId:"ai",eventKey:"benchmark-study"},
 {id:"s4",title:"Similar topic, different release",url:"https://lab.example/other",topicId:"ai",eventKey:"release-2"}
];
const old={id:"n1",topicId:"ai",question:"How reliable are benchmarks?",clusterIds:["cluster:ai:benchmark-study"],state:"published",debate:"disabled"};
const result=evaluate(observations,[old]);
assert.equal(result.metrics.sourceObservations,4);
assert.equal(result.metrics.clusters,3);
assert.equal(result.metrics.cards,3);
assert.equal(result.metrics.nucleiCreated,0);
assert.deepEqual(result.clusters.find(x=>x.id==="cluster:ai:release-1").sourceIds,["s1","s2"]);
assert.equal(result.cards.every(x=>x.validation==="not_assessed"),true);
assert.equal(result.nuclei[0].id,"n1");
assert.equal(result.nuclei[0].debate,"disabled");
const next=evaluate([...observations,{id:"s5",title:"Follow-up",url:"https://followup.example/1",topicId:"ai",eventKey:"release-1"}],[old]);
assert.equal(next.nuclei[0].id,"n1");
assert.equal(next.clusters.length,3);
assert.equal(next.clusters.find(x=>x.id==="cluster:ai:release-1").sourceIds.length,3);
assert.equal(old.clusterIds.length,1);
assert.throws(()=>evaluate([{...observations[0],eventKey:""}]),/eventKey/);
assert.throws(()=>evaluate([{...observations[0],id:"s1",url:"https://a.example"},{...observations[0],id:"s1",url:"https://b.example"}]),/collision/);
console.log("Epistemic offline fixture checks passed");
