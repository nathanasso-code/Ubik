/* Offline evaluation only. Explicit event keys are fixture labels, not inferred facts. */
"use strict";
const knowledge=require("./knowledge-pipeline.js");
function requireString(value,label){if(typeof value!=="string"||!value.trim())throw new TypeError(label+" required");return value.trim()}
function evaluate(observations, previousNuclei=[]){
 if(!Array.isArray(observations)||!Array.isArray(previousNuclei))throw new TypeError("Arrays required");
 const sources=new Map(), groups=new Map(), seen=new Set();
 for(const item of observations){
  const source=knowledge.normalizeSource(item);
  const topicId=requireString(item.topicId,"topicId");
  const eventKey=requireString(item.eventKey,"eventKey");
  const identity=topicId+"\u0000"+eventKey;
  if(seen.has(source.id)&&sources.get(source.id).url!==source.url)throw new TypeError("Source id collision");
  seen.add(source.id);sources.set(source.id,source);
  if(!groups.has(identity))groups.set(identity,{topicId,eventKey,sourceIds:[]});
  groups.get(identity).sourceIds.push(source.id);
 }
 const clusters=[...groups.values()].map(g=>knowledge.makeCluster({
  id:"cluster:"+encodeURIComponent(g.topicId)+":"+encodeURIComponent(g.eventKey),
  topicId:g.topicId,sourceIds:g.sourceIds
 }));
 const cards=clusters.map(c=>Object.freeze({id:"card:"+c.id,clusterId:c.id,topicId:c.topicId,sourceIds:c.sourceIds,kind:"epistemic-card",validation:"not_assessed"}));
 const nuclei=previousNuclei.map(n=>{
  if(!n||typeof n.id!=="string"||!n.id||!Array.isArray(n.clusterIds))throw new TypeError("Invalid existing nucleus");
  return Object.freeze({...n,clusterIds:Object.freeze([...n.clusterIds])});
 });
 return Object.freeze({sources:Object.freeze([...sources.values()]),clusters:Object.freeze(clusters),cards:Object.freeze(cards),nuclei:Object.freeze(nuclei),metrics:Object.freeze({sourceObservations:observations.length,uniqueSourceIds:sources.size,clusters:clusters.length,cards:cards.length,nucleiCreated:0})});
}
module.exports=Object.freeze({evaluate});
