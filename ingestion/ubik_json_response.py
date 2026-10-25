"""Strict JSON or one fenced JSON object; no arbitrary substring extraction."""
import json,re
def parse_json_response(content):
 if not isinstance(content,str) or not content.strip():raise ValueError("empty model content")
 s=content.strip()
 if s.startswith("```"):
  m=re.fullmatch(r"```(?:json)?[ \t]*\r?\n([\s\S]*?)\r?\n```",s,flags=re.IGNORECASE)
  if not m:raise ValueError("invalid markdown JSON fence")
  s=m.group(1).strip()
 value=json.loads(s)
 if not isinstance(value,dict):raise ValueError("JSON response must be an object")
 return value
