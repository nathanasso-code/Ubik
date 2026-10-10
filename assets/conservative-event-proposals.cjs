/* Conservative offline proposals: never publish clusters or claim same-event truth. */
"use strict";
function propose(pairs, {minimumScore=0.65}={}){
 if(!Array.isArray(pairs))throw new TypeError("Pairs array required");
 if(typeof minimumScore!=="number"||!Number.isFinite(minimumScore)||minimumScore<0||minimumScore>1)throw new TypeError("Invalid threshold");
 const candidates=[],rejected=[],seen=new Set();
 for(const p of pairs){
  if(!p||typeof p.left_id!=="string"||typeof p.right_id!=="string"||!p.left_id||!p.right_id||p.left_id===p.right_id)throw new TypeError("Invalid pair");
  const id=[p.left_id,p.right_id].sort().join("\u0000");
  if(seen.has(id))continue;
  seen.add(id);
  const score=p.similarity_hint;
  if(typeof score!=="number"||!Number.isFinite(score)||score<0||score>1)throw new TypeError("Invalid score");
  const sameUrl=p.left_url&&p.right_url&&p.left_url===p.right_url;
  const eligible=!sameUrl&&p.reason==="title_token_overlap"&&score>=minimumScore;
  const record=Object.freeze({
   leftId:p.left_id,rightId:p.right_id,score,
   status:eligible?"review_candidate":"not_proposed",
   reason:sameUrl?"same_url_not_independent":eligible?"high_title_similarity_needs_event_review":"insufficient_evidence",
   sameEvent:null,validated:false
  });
  (eligible?candidates:rejected).push(record);
 }
 return Object.freeze({method:"conservative_unverified_title_candidates",threshold:minimumScore,
  candidates:Object.freeze(candidates),rejected:Object.freeze(rejected),automaticClusters:0,automaticNuclei:0});
}
module.exports=Object.freeze({propose});
