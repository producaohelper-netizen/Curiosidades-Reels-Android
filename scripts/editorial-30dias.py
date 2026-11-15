#!/usr/bin/env python3
"""30-day editorial scheduler for Fatos Que Parecem Mentira. Standard library only."""
import argparse,csv,json,re,unicodedata
from collections import Counter
from datetime import date,timedelta
from pathlib import Path
PILLARS=[
 ("historia_real",35,"Histórias reais que parecem ficção"),
 ("ciencia_natureza",30,"O lado estranho da ciência"),
 ("misterios_documentados",20,"Mistérios com documentos"),
 ("cotidiano",15,"Origens inesperadas"),
]
def key(value):
 s=unicodedata.normalize("NFKD",str(value).lower())
 return re.sub(r"[^a-z0-9]+"," ", "".join(c for c in s if not unicodedata.combining(c))).strip()
def validate(item,used):
 required=("title","pillar","source_primary","source_confirmation","facts","hook","reveal","cta")
 missing=[k for k in required if not item.get(k)]
 if missing:return False,"missing:"+",".join(missing)
 if item["pillar"] not in {p[0] for p in PILLARS}:return False,"invalid_pillar"
 if key(item["title"]) in used:return False,"duplicate_title"
 if item["source_primary"].strip()==item["source_confirmation"].strip():return False,"same_source"
 if not all(str(item[x]).startswith("https://") for x in ("source_primary","source_confirmation")):return False,"invalid_source_url"
 if item.get("confidence") not in ("high","medium"):return False,"confidence_not_verified"
 if item.get("claim_status") not in ("documented","scientifically_supported"):return False,"unsupported_claim"
 if item.get("is_sensitive") and not item.get("human_review"):return False,"sensitive_requires_review"
 return True,"approved"
def allocation(days=30):
 # Hamilton largest remainder, deterministic and sums to days.
 raw=[days*p[1]/100 for p in PILLARS]
 base=[int(n) for n in raw]
 for i in sorted(range(len(raw)),key=lambda i:(-(raw[i]-base[i]),i))[:days-sum(base)]:base[i]+=1
 return dict(zip((p[0] for p in PILLARS),base))
def plan(items,used=None,days=30,start=None):
 used=set(key(x) for x in (used or []));approved=[];rejected=[]
 for item in items:
  ok,why=validate(item,used)
  if ok:approved.append(item);used.add(key(item["title"]))
  else:rejected.append({"title":item.get("title",""),"reason":why})
 targets=allocation(days);remaining=targets.copy();schedule=[]
 for day in range(days):
  eligible=[i for i in approved if remaining.get(i["pillar"],0)>0]
  if not eligible:
   schedule.append({"day":day+1,"date":str((start or date.today())+timedelta(days=day)),"status":"needs_verified_story","pillar":max(remaining,key=remaining.get)})
   remaining[max(remaining,key=remaining.get)]-=1
   continue
  # Deficit balancing prevents large runs of one pillar.
  pillar=max((p for p in remaining if remaining[p]>0 and any(x["pillar"]==p for x in eligible)),key=lambda p:(remaining[p]/max(targets[p],1),remaining[p]))
  item=next(x for x in approved if x["pillar"]==pillar)
  approved.remove(item);remaining[pillar]-=1
  schedule.append({"day":day+1,"date":str((start or date.today())+timedelta(days=day)),"status":"ready_for_editorial_review","pillar":pillar,"title":item["title"],"hook":item["hook"],"reveal":item["reveal"],"source_primary":item["source_primary"],"source_confirmation":item["source_confirmation"],"target_seconds":35})
 return {"brand":"Fatos Que Parecem Mentira","targets":targets,"scheduled":schedule,"rejected":rejected}
def main():
 ap=argparse.ArgumentParser();ap.add_argument("--input",default="planning/pautas-verificadas.json");ap.add_argument("--history",default="planning/publicados.json");ap.add_argument("--output",default="planning/plano-editorial-30dias.json");a=ap.parse_args()
 src=Path(a.input);items=json.loads(src.read_text()) if src.exists() else []
 h=Path(a.history);history=json.loads(h.read_text()) if h.exists() else []
 result=plan(items,history);out=Path(a.output);out.parent.mkdir(parents=True,exist_ok=True)
 out.write_text(json.dumps(result,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
 with out.with_suffix(".csv").open("w",newline="",encoding="utf-8-sig") as fp:
  fields=["day","date","status","pillar","title","hook","reveal","source_primary","source_confirmation","target_seconds"]
  w=csv.DictWriter(fp,fieldnames=fields,extrasaction="ignore");w.writeheader();w.writerows(result["scheduled"])
 print("Editorial plan:",len(result["scheduled"]),"days; ready:",sum(x["status"]=="ready_for_editorial_review" for x in result["scheduled"]),"rejected:",len(result["rejected"]))
if __name__=="__main__":main()
