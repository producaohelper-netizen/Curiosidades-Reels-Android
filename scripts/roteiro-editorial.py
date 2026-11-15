#!/usr/bin/env python3
"""Render an original, short Portuguese narrative from an editorially approved brief."""
import argparse,json,re
from pathlib import Path
from importlib.util import module_from_spec,spec_from_file_location
spec=spec_from_file_location("editorial",Path(__file__).with_name("editorial-30dias.py"))
ed=module_from_spec(spec);spec.loader.exec_module(ed)
def words(s):return len(re.findall(r"\b[\wÀ-ÿ]+\b",s))
def produce(brief):
 ok,why=ed.validate(brief,set())
 if not ok:raise ValueError("Pauta rejeitada: "+why)
 facts=brief["facts"]
 if not isinstance(facts,list) or not 2<=len(facts)<=5 or not all(isinstance(x,str) and len(x.strip())>20 for x in facts):
  raise ValueError("Informe de 2 a 5 fatos substanciais, sustentados pelas fontes")
 for field in ("hook","reveal","cta"):
  if not isinstance(brief[field],str) or not 12<=len(brief[field])<=180:
   raise ValueError(field+" precisa ter de 12 a 180 caracteres")
 if not brief.get("source_notes") or len(brief["source_notes"])<40:
  raise ValueError("Notas de checagem das duas fontes são obrigatórias")
 if brief["pillar"]=="misterios_documentados" and not all(brief.get(x) for x in ("documented","hypothesis","unknown")):
  raise ValueError("Mistério exige comprovado, hipótese e desconhecido")
 # Use only supplied, reviewed assertions. Do not invent dates, names, or causes.
 context=brief.get("context","").strip()
 middle=" ".join(x.strip() for x in facts)
 text=" ".join(x for x in (brief["hook"].strip(),context,middle,brief["reveal"].strip(),brief["cta"].strip()) if x)
 count=words(text)
 # Rough 2.3-3.2 words/sec; no fake precision about TTS speed.
 if not 58<=count<=125:raise ValueError("Roteiro fora da faixa 25–45s: "+str(count)+" palavras")
 return {"title":brief["title"],"pillar":brief["pillar"],"script":text,"word_count":count,"duration_estimate_seconds":[round(count/3.2),round(count/2.3)],"sources":[brief["source_primary"],brief["source_confirmation"]],"source_notes":brief["source_notes"],"confidence":brief["confidence"],"review_required":True,"segments":{"hook":brief["hook"],"context":context,"development":facts,"reveal":brief["reveal"],"cta":brief["cta"]}}
def main():
 p=argparse.ArgumentParser();p.add_argument("input");p.add_argument("--output",default="planning/roteiro-aprovacao.json");a=p.parse_args()
 data=json.loads(Path(a.input).read_text(encoding="utf-8"))
 result=produce(data);dest=Path(a.output);dest.parent.mkdir(parents=True,exist_ok=True)
 dest.write_text(json.dumps(result,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
 print("Roteiro para revisão editorial:",result["word_count"],"palavras")
if __name__=="__main__":main()
