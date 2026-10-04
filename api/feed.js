const { list }=require("@vercel/blob");
async function read(url){const r=await fetch(url,{headers:{Authorization:"Bearer "+process.env.BLOB_READ_WRITE_TOKEN}});return r.ok?r.json():null}
module.exports=async function(req,res){
 if(req.method!=="GET")return res.status(405).json({error:"METHOD_NOT_ALLOWED"});
 try{
  let cursor,blobs=[];do{const x=await list({prefix:"questions/",limit:100,cursor});blobs.push(...(x.blobs||[]).filter(b=>b.pathname.endsWith("/latest.json")));cursor=x.hasMore?x.cursor:null}while(cursor&&blobs.length<500);
  const docs=(await Promise.all(blobs.map(b=>read(b.url)))).filter(Boolean).sort((a,b)=>new Date(b.updated_at)-new Date(a.updated_at));
  const questions=docs.map(d=>({id:d.id,question:d.normalized_question||d.requested_question,state:d.state,outcome:d.publication_gate?.outcome,updated_at:d.updated_at,version:d.version,claim_count:d.claims?.length||0}));
  const pulse=docs.filter(d=>d.pulse?.material_change).map(d=>({question_id:d.id,question:d.normalized_question||d.requested_question,...d.pulse})).sort((a,b)=>new Date(b.created_at)-new Date(a.created_at));
  res.setHeader("Cache-Control","s-maxage=60, stale-while-revalidate=300");return res.status(200).json({questions,pulse,count:questions.length});
 }catch(e){return res.status(500).json({error:"FEED_FAILED",detail:e.message})}
};