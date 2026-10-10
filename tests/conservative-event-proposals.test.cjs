const assert=require("node:assert/strict");
const {propose}=require("../assets/conservative-event-proposals.cjs");
const input=[
 {left_id:"a",right_id:"b",left_url:"https://a.example",right_url:"https://b.example",reason:"title_token_overlap",similarity_hint:0.82},
 {left_id:"a",right_id:"c",left_url:"https://a.example",right_url:"https://c.example",reason:"title_token_overlap",similarity_hint:0.33},
 {left_id:"d",right_id:"e",left_url:"https://same.example",right_url:"https://same.example",reason:"same_url",similarity_hint:1},
 {left_id:"b",right_id:"a",left_url:"https://b.example",right_url:"https://a.example",reason:"title_token_overlap",similarity_hint:0.82}
];
const result=propose(input);
assert.equal(result.candidates.length,1);
assert.equal(result.rejected.length,2);
assert.equal(result.automaticClusters,0);
assert.equal(result.automaticNuclei,0);
assert.equal(result.candidates[0].sameEvent,null);
assert.equal(result.candidates[0].validated,false);
assert.equal(result.rejected.find(x=>x.leftId==="d").reason,"same_url_not_independent");
assert.equal(propose(input,{minimumScore:0.9}).candidates.length,0);
assert.throws(()=>propose(input,{minimumScore:2}),/threshold/);
assert.throws(()=>propose([{...input[0],similarity_hint:NaN}]),/score/);
assert.throws(()=>propose([{...input[0],left_id:"b",right_id:"b"}]),/pair/);
console.log("Conservative event proposal checks passed");
