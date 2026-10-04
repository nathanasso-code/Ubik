const catalog=require("../data/catalog.json");const {list}=require("@vercel/blob");
const norm=s=>String(s||"").toLowerCase().normalize("NFD").replace(/[\u0300-\u036f]/g,"");
const score=(q,s)=>{q=norm(q).split(/\s+/).filter(x=>x.length>2);s=norm(s);return q.reduce((n,w)=>n+(s.includes(w)?1:0),0)/Math.max(q.length,1)}
module.exports=async(req,res)=>{const q=String(req.query?.q||"").trim();if(q.length<2)return res.status(200).json({topics:[],questions:[],exact:false});
const topics=catalog.topics.map(t=>({...t,_score:score(q,t.title+" "+t.description+" "+t.questions.join(" "))})).filter(t=>t._score>0).sort((a,b)=>b._score-a._score).slice(0,6).map(({_score,...t})=>t);
let questions=[];try{const x=await list({prefix:"questions/",limit:100});questions=(x.blobs||[]).filter(b=>b.pathname.endsWith("/latest.json")).map(b=>({id:b.pathname.split("/")[1]}))}catch{}
res.setHeader("Cache-Control","s-maxage=60");res.json({query:q,topics,questions,exact:topics.some(t=>norm(t.title)===norm(q)),can_propose:true})};