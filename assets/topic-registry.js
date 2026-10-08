/* Declarative topic configuration: no topic may own shared core types. */
(function(root){
"use strict";
const topics=[
 {id:"euromaidan",title:"Euromaidan",views:["timeline","sources"],capabilities:["provenance","revisions","semantic-navigation"]},
 {id:"attacks",title:"Attacchi contro l’Ucraina",views:["map","timeline","archive"],capabilities:["provenance","revisions","temporal-filter","live-signals"],dataset:"ukraine-attacks"},
 {id:"economy",title:"Economia ucraina",views:["chart","sources"],capabilities:["provenance","semantic-navigation"]}
];
const registry=root.UbikCore.createRegistry(topics);
root.UBIK_TOPIC_REGISTRY=registry;
root.UBIK_TOPICS=Object.freeze(Object.fromEntries(registry.list().map(t=>[t.id,t])));
root.UBIK_CORE=Object.freeze({schemaVersion:root.UbikCore.schemaVersion,sharedObjects:root.UbikCore.types,sharedCapabilities:root.UbikCore.commonCapabilities,optionalViews:root.UbikCore.views});
})(typeof globalThis!=="undefined"?globalThis:this);
