/* Ubik knowledge pipeline v0: deterministic proposals, never automatic truth claims. */
(function(root){
"use strict";
function check(x,m){if(!x)throw new TypeError(m)}
function unique(xs){return [...new Set(xs)]}
function normalizeSource(x){
 check(x&&typeof x==="object","Source required");
 check(typeof x.id==="string"&&x.id.trim(),"Source id required");
 check(typeof x.title==="string"&&x.title.trim(),"Source title required");
 check(typeof x.url==="string"&&/^https?:\/\//i.test(x.url),"Source URL required");
 return Object.freeze({id:x.id,title:x.title,url:x.url,publisher:x.publisher||null,publishedAt:x.publishedAt||null,originId:x.originId||null,topicIds:Object.freeze(unique(x.topicIds||[])),kind:x.kind||"article",primary:!!x.primary});
}
function makeCluster(x){
 check(x&&typeof x.id==="string"&&x.id,"Cluster id required");
 check(typeof x.topicId==="string"&&x.topicId,"Topic id required");
 check(Array.isArray(x.sourceIds)&&x.sourceIds.length,"Cluster sources required");
 return Object.freeze({id:x.id,topicId:x.topicId,sourceIds:Object.freeze(unique(x.sourceIds)),state:"provisional",summary:null,review:"not_requested"});
}
function proposeNucleus(x){
 check(x&&typeof x.id==="string"&&x.id,"Nucleus id required");
 check(typeof x.topicId==="string"&&x.topicId,"Topic id required");
 check(typeof x.question==="string"&&x.question.trim(),"Question required");
 check(Array.isArray(x.clusterIds)&&x.clusterIds.length,"Linked clusters required");
 return Object.freeze({id:x.id,topicId:x.topicId,question:x.question.trim(),clusterIds:Object.freeze(unique(x.clusterIds)),state:"candidate",debate:"disabled",reason:x.reason||null});
}
const transitions=Object.freeze({candidate:["reviewed"],reviewed:["published","candidate"],published:["archived"],archived:["published"]});
function transitionNucleus(nucleus,next){
 check(nucleus&&transitions[nucleus.state],"Invalid nucleus");
 check(transitions[nucleus.state].includes(next),"Invalid nucleus transition");
 return Object.freeze({...nucleus,state:next});
}
function enableDebate(nucleus){
 check(nucleus&&nucleus.state==="published","Only published nuclei can host debates");
 return Object.freeze({...nucleus,debate:"enabled"});
}
function linkCluster(nucleus,cluster){
 check(nucleus&&cluster&&nucleus.topicId===cluster.topicId,"Topic mismatch");
 return Object.freeze({...nucleus,clusterIds:Object.freeze(unique([...nucleus.clusterIds,cluster.id]))});
}
const api=Object.freeze({schemaVersion:1,normalizeSource,makeCluster,proposeNucleus,transitionNucleus,enableDebate,linkCluster});
root.UbikKnowledge=api;
if(typeof module!=="undefined"&&module.exports)module.exports=api;
})(typeof globalThis!=="undefined"?globalThis:this);
