"""Minimal safe OpenRouter authentication probe. Never log key or response body."""
import os,json,urllib.request,urllib.error,sys
key=os.environ.get("OPENROUTER_API_KEY","")
result={"secret_present":bool(key),"secret_nonempty":bool(key.strip()),"http_status":None}
if not key.strip():
 print(json.dumps(result));sys.exit(1)
req=urllib.request.Request("https://openrouter.ai/api/v1/auth/key",headers={"Authorization":"Bearer "+key},method="GET")
try:
 with urllib.request.urlopen(req,timeout=30) as resp:result["http_status"]=resp.status
except urllib.error.HTTPError as e:result["http_status"]=e.code
except Exception as e:result["transport_error"]=type(e).__name__
print(json.dumps(result))
if result["http_status"]!=200:sys.exit(1)
