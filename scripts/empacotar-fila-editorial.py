#!/usr/bin/env python3
"""Build a reviewed multi-story Android queue. Never ships synthetic content."""
import argparse
import importlib.util
import json
from pathlib import Path

def load_packager():
    p=Path(__file__).with_name("empacotar-pauta-android.py")
    spec=importlib.util.spec_from_file_location("editorial_packager",p)
    module=importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module

def build(manifest):
    if not isinstance(manifest,list) or not 1<=len(manifest)<=30:
        raise ValueError("A fila deve conter entre 1 e 30 pautas")
    pack=load_packager()
    stories=[]
    keys=set()
    for index,item in enumerate(manifest):
        if not isinstance(item,dict) or not isinstance(item.get("brief"),dict) or not isinstance(item.get("assets"),list):
            raise ValueError(f"Pauta {index+1}: brief e assets obrigatórios")
        story=pack.package(item["brief"],item["assets"])
        key=story["title"].strip().casefold()
        if key in keys:
            raise ValueError("Título duplicado na fila editorial")
        keys.add(key)
        stories.append(story)
    return {"schema_version":1,"stories":stories}

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("manifest",help="JSON list of {brief, assets} entries")
    parser.add_argument("--output",default="app/src/main/assets/editorial-approved.json")
    args=parser.parse_args()
    result=build(json.loads(Path(args.manifest).read_text(encoding="utf-8")))
    output=Path(args.output)
    output.parent.mkdir(parents=True,exist_ok=True)
    output.write_text(json.dumps(result,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print(f"Fila editorial: {len(result['stories'])} histórias aprovadas")
if __name__=="__main__":
    main()
