module.exports = async function handler(req,res){
  if(req.method!=="POST") return res.status(405).json({error:"METHOD_NOT_ALLOWED"});
  let body=req.body||{}; if(typeof body==="string"){try{body=JSON.parse(body)}catch{}}
  const question=(body.question||"").trim();
  if(question.length<8) return res.status(400).json({error:"QUESTION_TOO_SHORT"});
  if(!process.env.openai_api_key) return res.status(503).json({error:"RESEARCH_ENGINE_NOT_CONFIGURED"});
  try{
    const response=await fetch("https://api.openai.com/v1/responses",{
      method:"POST",
      headers:{"Authorization":"Bearer "+process.env.openai_api_key,"Content-Type":"application/json"},
      body:JSON.stringify({
        model:process.env.OPENAI_MODEL||"gpt-6-luna",
        tools:[{type:"web_search"}],
        input:"Research this question for Ubik: "+question+"\nReturn only JSON with normalized_question, state, claims, tensions, inference_boundaries, audit. Each claim must contain text, status, and evidence. Each evidence item must contain statement, source_title, url, source_type, relation, limitations. Prefer primary sources and deliberately seek counterevidence. Distinguish source from evidence, association from causation, exposure from outcome, and scenario from forecast."
      })
    });
    const data=await response.json();
    if(!response.ok){const msg=data?.error?.message||"OpenAI API error";console.error("OPENAI_ERROR",response.status,msg);return res.status(502).json({error:"MODEL_ERROR",detail:msg});}
    const out=data.output_text||data.output?.flatMap(x=>x.content||[]).map(x=>x.text||"").join("")||"";
    let parsed; try{parsed=JSON.parse(out.replace(/^```json\s*|```$/g,""))}catch{return res.status(502).json({error:"INVALID_RESEARCH_OBJECT"})}
    return res.status(200).json(parsed);
  }catch(e){return res.status(500).json({error:"RESEARCH_FAILED"})}
};