"""Single-source OpenRouter diagnostic: fail closed and redact response diagnostics."""
import json,os,urllib.request,urllib.error,hashlib,sys
from pathlib import Path
from ingestion.ubik_source_registry_v3 import SYSTEM
from ingestion.ubik_json_response import parse_json_response
def main():
 p=Path("data/taxonomy-pilot/fact-reference-pilot.json")
 items=json.loads(p.read_text())["items"]
 source="S433"
 news=[{"key":i["key"],"title":i["title"],"summary":i["summary"]} for i in items if i["source_id"]==source]
 assert news
 payload={"model":os.environ["UBIK_LLM_MODEL"],"messages":[{"role":"system","content":SYSTEM},{"role":"user","content":json.dumps({"source_id":source,"input_mode":"summaries","news":news},ensure_ascii=False)}],"response_format":{"type":"json_object"},"temperature":0}
 out={"model":payload["model"],"source_id":source,"status":"unattempted"}
 path=Path("data/taxonomy-pilot/sonnet-diagnostic.json")
 try:
  key=os.environ["UBIK_LLM_API_KEY"]
  req=urllib.request.Request(os.environ["UBIK_LLM_ENDPOINT"],data=json.dumps(payload).encode(),headers={"Authorization":"Bearer "+key,"Content-Type":"application/json"},method="POST")
  try:
   with urllib.request.urlopen(req,timeout=150) as resp:
    raw=resp.read(200000)
    out["http_status"]=resp.status
  except urllib.error.HTTPError as e:
   raw=e.read(20000)
   out["http_status"]=e.code
   try:
    err=json.loads(raw).get("error",{})
    out["provider_error"]={"code":str(err.get("code",""))[:100],"type":str(err.get("type",""))[:100],"message":str(err.get("message",""))[:350]}
   except Exception:out["provider_error"]={"body_sha256":hashlib.sha256(raw).hexdigest(),"body_length":len(raw)}
   raise RuntimeError("provider_http_error")
  out["response_bytes"]=len(raw)
  body=json.loads(raw)
  out["provider_top_keys"]=list(body)[:15]
  choice=body.get("choices",[{}])[0]
  msg=choice.get("message") or {}
  out["finish_reason"]=choice.get("finish_reason")
  out["message_keys"]=list(msg)
  content=msg.get("content")
  out["content_type"]=type(content).__name__
  out["content_length"]=len(content) if isinstance(content,str) else None
  out["content_sha256"]=hashlib.sha256(content.encode()).hexdigest() if isinstance(content,str) else None
  if not isinstance(content,str) or not content.strip():raise RuntimeError("empty_content")
  out["markdown_fence_detected"]=content.strip().startswith("```")
  parsed=parse_json_response(content)
  if not isinstance(parsed,dict) or "events" not in parsed or "assignments" not in parsed:raise RuntimeError("invalid_schema")
  out["status"]="success"
  out["events"]=len(parsed["events"])
  out["assignments"]=len(parsed["assignments"])
 except Exception as exc:
  out["status"]="failed"
  out["error_class"]=type(exc).__name__
  out["error_code"]=str(exc)[:120] if isinstance(exc,RuntimeError) else type(exc).__name__
 finally:
  path.parent.mkdir(parents=True,exist_ok=True)
  path.write_text(json.dumps(out,ensure_ascii=False,indent=2))
  print(json.dumps(out,ensure_ascii=False))
 if out["status"]!="success":sys.exit(1)
if __name__=="__main__":main()
