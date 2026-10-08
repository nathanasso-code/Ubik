/* Ubik Core v1: dependency-free contracts; no DOM or topic-specific assumptions. */
(function(root){
"use strict";
const TYPES=Object.freeze(["topic","claim","event","source","evidence","relation","revision","contribution"]);
const VIEWS=Object.freeze(["map","timeline","chart","comparison","archive","sources","evidence","discussion"]);
const COMMON=Object.freeze(["search","semantic-navigation","provenance","revisions"]);
function assert(condition,message){if(!condition)throw new TypeError(message)}
function normalizeTopic(input){
 assert(input&&typeof input==="object","Topic must be an object");
 assert(typeof input.id==="string"&&/^[a-z][a-z0-9-]*$/.test(input.id),"Invalid topic id");
 assert(typeof input.title==="string"&&input.title.trim(),"Missing topic title");
 const views=[...new Set(input.views||[])],capabilities=[...new Set(input.capabilities||[])];
 assert(views.every(x=>VIEWS.includes(x)),"Unknown view");
 assert(capabilities.every(x=>typeof x==="string"&&x.length>0),"Invalid capability");
 return Object.freeze({id:input.id,title:input.title,views:Object.freeze(views),capabilities:Object.freeze(capabilities),dataset:input.dataset||null});
}
function createRegistry(topics){
 const byId=new Map();
 for(const item of topics){const topic=normalizeTopic(item);assert(!byId.has(topic.id),"Duplicate topic id: "+topic.id);byId.set(topic.id,topic)}
 return Object.freeze({
  get(id){return byId.get(id)||null},
  list(){return [...byId.values()]},
  supports(id,view){const t=byId.get(id);return !!t&&t.views.includes(view)},
  hasCapability(id,capability){const t=byId.get(id);return !!t&&(COMMON.includes(capability)||t.capabilities.includes(capability))}
 });
}
function makeRecord(kind,data){
 assert(TYPES.includes(kind),"Unknown record kind");
 assert(data&&typeof data==="object"&&!Array.isArray(data),"Record must be an object");
 assert(typeof data.id==="string"&&data.id.trim(),"Record needs a stable id");
 return Object.freeze({...data,kind,schemaVersion:data.schemaVersion||1});
}
function projectEvent(event){
 assert(event&&typeof event==="object","Invalid event");
 return makeRecord("event",{...event,sourceIds:(event.sources||[]).map(s=>s.id||s.url).filter(Boolean)});
}
const api=Object.freeze({schemaVersion:1,types:TYPES,views:VIEWS,commonCapabilities:COMMON,normalizeTopic,createRegistry,makeRecord,projectEvent});
root.UbikCore=api;
if(typeof module!=="undefined"&&module.exports)module.exports=api;
})(typeof globalThis!=="undefined"?globalThis:this);
