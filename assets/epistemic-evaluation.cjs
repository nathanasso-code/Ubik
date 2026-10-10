/* Offline quality evaluation. Ground truth is explicitly provided by the fixture. */
"use strict";
const {evaluate}=require("./epistemic-pilot.cjs");
function key(a,b){return [a,b].sort().join("\u0000")}
function score(observations, expectedGroups, existingNuclei=[]){
 if(!Array.isArray(observations)||!Array.isArray(expectedGroups))throw new TypeError("Arrays required");
 const ids=observations.map(x=>x.id);
 if(ids.some(x=>typeof x!=="string"||!x))throw new TypeError("Source ids required");
 if(new Set(ids).size!==ids.length)throw new TypeError("Duplicate source ids in fixture");
 const all=new Set(ids), assigned=new Set(), expectedPairs=new Set();
 for(const group of expectedGroups){
  if(!Array.isArray(group)||!group.length)throw new TypeError("Nonempty expected group required");
  for(const id of group){
   if(!all.has(id)||assigned.has(id))throw new TypeError("Invalid or duplicate expected member");
   assigned.add(id);
  }
  for(let i=0;i<group.length;i++)for(let j=i+1;j<group.length;j++)expectedPairs.add(key(group[i],group[j]));
 }
 if(assigned.size!==all.size)throw new TypeError("Expected groups must cover all observations");
 const result=evaluate(observations,existingNuclei),actualPairs=new Set();
 for(const cluster of result.clusters){
  for(let i=0;i<cluster.sourceIds.length;i++)for(let j=i+1;j<cluster.sourceIds.length;j++)actualPairs.add(key(cluster.sourceIds[i],cluster.sourceIds[j]));
 }
 const falseMerges=[...actualPairs].filter(x=>!expectedPairs.has(x));
 const missedMerges=[...expectedPairs].filter(x=>!actualPairs.has(x));
 const tp=actualPairs.size-falseMerges.length;
 const precision=actualPairs.size?tp/actualPairs.size:1;
 const recall=expectedPairs.size?tp/expectedPairs.size:1;
 const missingProvenance=ids.filter(id=>!result.sources.some(x=>x.id===id));
 return Object.freeze({
  observations:ids.length,expectedClusters:expectedGroups.length,actualClusters:result.clusters.length,
  correctPairs:tp,falseMerges:falseMerges.length,missedMerges:missedMerges.length,
  pairPrecision:precision,pairRecall:recall,
  missingProvenance:Object.freeze(missingProvenance),
  nucleiCreated:result.metrics.nucleiCreated,
  nucleusIdentityPreserved:existingNuclei.every(n=>result.nuclei.some(x=>x.id===n.id)),
  falseMergePairs:Object.freeze(falseMerges.map(x=>x.split("\u0000"))),
  missedMergePairs:Object.freeze(missedMerges.map(x=>x.split("\u0000")))
 });
}
module.exports=Object.freeze({score});
