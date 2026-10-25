"""Single Sonnet generation authentication probe; no event corpus and no secret logging."""
import os,json,urllib.request,urllib.error,sys
key=os.environ.get("OPENROUTER_API_KEY","")
payload={"model":"anthropic/claude-sonnet-5.5","messages":[{"role":"user","content":"Reply with the single word OK."}],"max_tokens":20}
out={"secret_present":bool(key.strip()),"model":payload["model"]}
if not key.strip():print(json.dumps(out));sys.exit(1)
req=urllib.request.Request("https://openrouter.ai/api/v1/chat/completions",data=json.dumps(payload).encode(),headers={"Authorization":"Bearer "+key,"Content-Type":"application/json"},method="POST")
try:
 with urllib.request.urlopen(req,timeout=90) as resp:
  body=json.loads(resp.read());out["http_status"]=resp.status;out["has_choices"]=bool(body.get("choices"));out["usage"]=body.get("usage",{})
except urllib.error.HTTPError as e:
 out["http_status"]=e.code
 try:
  err=json.loads(e.read(8192)).get("error",{})
  out["provider_error_code"]=err.get("code")
  out["provider_error_message"]=str(err.get("message",""))[:250]
 except Exception:pass
except Exception as e:out["transport_error"]=type(e).__name__
print(json.dumps(out))
if out.get("http_status")!=200 or not out.get("has_choices"):sys.exit(1)
