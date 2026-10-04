const { put, list } = require("@vercel/blob");
const API="https://api.openai.com/v1/responses";
const model=()=>process.env.OPENAI_MODEL||"gpt-6-luna";
function output(d){return d.output_text||d.output?.flatMap(x=>x.content||[]).map(x=>x.text||"").join("")||""}
function json(s){const a=s.indexOf("{"),b=s.lastIndexOf("}");if(a<0||b<a)throw Error("INVALID_JSON");return JSON.parse(s.slice(a,b+1))}
async function ask(input,web=false){
 const r=await fetch(API,{method:"POST",headers:{Authorization:"Bearer "+process.env.openai_api_key,"Content-Type":"application/json"},body:JSON.stringify({model:model(),tools:web?[{type:"web_search"}]:undefined,input})});
 const d=await r.json();if(!r.ok)throw Error(d?.error?.message||"MODEL_ERROR");return json(output(d))
}
function slug(s){return s.toLowerCase().normalize("NFD").replace(/[\u0300-\u036f]/g,"").replace(/[^a-z0-9]+/g,"-").replace(/^-|-$/g,"").slice(0,120)}
async function cached(question){const key="questions/"+slug(question)+"/latest.json";const x=await list({prefix:key,limit:1});if(!x.blobs?.length)return null;const r=await fetch(x.blobs[0].url,{headers:{Authorization:"Bearer "+process.env.BLOB_READ_WRITE_TOKEN}});if(!r.ok)return null;return r.json()}
async function persist(q,question){const id=slug(q.normalized_question||question);const now=new Date().toISOString();const record={...q,id,requested_question:question,updated_at:now,version:1};await put("questions/"+id+"/latest.json",JSON.stringify(record),{access:"private",addRandomSuffix:false,allowOverwrite:true,contentType:"application/json"});await put("questions/"+id+"/versions/"+Date.now()+".json",JSON.stringify(record),{access:"private",addRandomSuffix:false,contentType:"application/json"});return record}
function gate(q){
 const errors=[],warnings=[];const claims=q.claims||[];
 if(!claims.length)errors.push("NO_CLAIMS");
 for(const c of claims){if(!c.text)errors.push("CLAIM_WITHOUT_TEXT");if(!(c.evidence||[]).length)errors.push("CLAIM_WITHOUT_EVIDENCE");for(const e of c.evidence||[]){if(!e.source_title||!e.url)errors.push("EVIDENCE_WITHOUT_SOURCE");if(!e.statement)errors.push("EMPTY_EVIDENCE")}}
 if(!q.audit?.counterevidence_searched)errors.push("COUNTEREVIDENCE_NOT_SEARCHED");
 if(!q.audit?.independence_checked)warnings.push("INDEPENDENCE_NOT_CONFIRMED");
 if(!q.inference_boundaries?.length)warnings.push("NO_INFERENCE_BOUNDARIES");
 const causal=claims.filter(c=>c.kind==="causal");for(const c of causal)if(!c.causal_identification)warnings.push("CAUSAL_IDENTIFICATION_MISSING");
 return {outcome:errors.length?"HOLD_FOR_REVIEW":warnings.length?"PASS_WITH_QUALIFICATIONS":"PASS",errors:[...new Set(errors)],warnings:[...new Set(warnings)]}
}
module.exports=async function handler(req,res){
 if(req.method!=="POST")return res.status(405).json({error:"METHOD_NOT_ALLOWED"});
 let body=req.body||{};if(typeof body==="string"){try{body=JSON.parse(body)}catch{}}
 const question=(body.question||"").trim();if(question.length<8)return res.status(400).json({error:"QUESTION_TOO_SHORT"});
 if(!process.env.openai_api_key)return res.status(503).json({error:"RESEARCH_ENGINE_NOT_CONFIGURED"});
 try{
  const hit=await cached(question);if(hit)return res.status(200).json({...hit,cache:{hit:true,scope:"persistent"}});
  const research=await ask(`You are Ubik Researcher. Research: ${question}
Return JSON only: {"normalized_question":"","scope":"","sources":[{"title":"","url":"","source_type":"","origin_family":"","finding":"","limitations":""}],"counterevidence":[{"title":"","url":"","finding":""}]}.
Prefer primary sources, systematic reviews, official datasets. Seek evidence both for and against. Do not synthesize a verdict yet.`,true);
  const map=await ask(`You are Ubik Cartographer. Convert this research corpus into an epistemic map. SOURCE IS NOT EVIDENCE. AI IS NEVER A SOURCE.
Question: ${question}
Corpus: ${JSON.stringify(research)}
Return JSON only: {"normalized_question":"","claims":[{"id":"","text":"","kind":"descriptive|causal|predictive|interpretive|normative","status":"","causal_identification":"","evidence":[{"statement":"","source_title":"","url":"","source_type":"","origin_family":"","relation":"supports|contradicts|qualifies|contextualizes","limitations":""}]}],"tensions":[],"inference_boundaries":[]}.
Do not count multiple reports of one origin family as independent confirmation.`);
  const critique=await ask(`You are Ubik Critic. Adversarially audit this map and search the web for counterevidence or missing qualifications.
Question: ${question}
Map: ${JSON.stringify(map)}
Return JSON only: {"critic_findings":[],"counterevidence_searched":true,"independence_checked":true,"citation_entailment_checked":true,"state":"","required_changes":[]}.
State must describe what evidence supports and what remains uncertain. Never turn association into causation or model output into observed fact.`,true);
  const q={...map,state:critique.state||"",audit:critique,method:{pipeline:["Researcher","Cartographer","Critic","Deterministic Gate"],model:model()}};
  q.publication_gate=gate(q);if(q.publication_gate.outcome!=="HOLD_FOR_REVIEW"){const saved=await persist(q,question);return res.status(200).json({...saved,cache:{hit:false,scope:"persistent"}})}return res.status(200).json(q);
 }catch(e){console.error("UBIK_RESEARCH_ERROR",e.message);return res.status(502).json({error:"RESEARCH_PIPELINE_FAILED",detail:e.message})}
};