#!/usr/bin/env python3
"""Package only explicitly reviewed stories for the Android editorial queue."""
import argparse,json,importlib.util
from pathlib import Path
def load_module(path,name):
 spec=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m
def package(brief,assets):
 root=Path(__file__).parent
 script=load_module(root/"roteiro-editorial.py","story_script").produce(brief)
 check=load_module(root/"validar-midias-editoriais.py","media_check")
 errors=check.validate_assets(script,assets)
 if errors:raise ValueError("Mídias rejeitadas: "+", ".join(errors))
 if not brief.get("reviewer") or not brief.get("reviewed_at"):
  raise ValueError("Revisor e data da revisão são obrigatórios")
 script["reviewer"]=brief["reviewer"]
 script["reviewed_at"]=brief["reviewed_at"]
 script["assets"]=assets
 return script
def main():
 p=argparse.ArgumentParser();p.add_argument("--brief",required=True);p.add_argument("--assets",required=True)
 p.add_argument("--output",default="app/src/main/assets/editorial-approved.json")
 a=p.parse_args()
 result=package(json.loads(Path(a.brief).read_text(encoding="utf-8")),json.loads(Path(a.assets).read_text(encoding="utf-8")))
 dest=Path(a.output);dest.parent.mkdir(parents=True,exist_ok=True)
 dest.write_text(json.dumps(result,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
 print("Pacote editorial pronto para Android:",result["title"])
if __name__=="__main__":main()
