#!/usr/bin/env python3
"""Create Instagram publishing assets from a rendered Reel without fabricating performance data."""
import json, re, unicodedata
from pathlib import Path

ROOT=Path("produced")
meta=json.loads((ROOT/"latest.json").read_text(encoding="utf-8"))
title=meta["title"].strip().rstrip("?! .")
category=meta.get("category","CURIOSIDADES")
sources=meta.get("fact_sources",[])
duration=float(meta.get("duration_s",0))
def norm(s):
    s=unicodedata.normalize("NFKD",s.lower())
    return re.sub(r"[^a-z0-9]+","", "".join(c for c in s if not unicodedata.combining(c)))
def pillar(s):
    x=norm(s)
    if any(w in x for w in ("universo","astronomia","espaco","lua","planeta","cosmo")):return "Universo em 30 segundos"
    if any(w in x for w in ("historia","historico","antiguidade")):return "História que parece mentira"
    if any(w in x for w in ("ciencia","fisica","quimica","tempo","meteorologia")):return "Ciência sem complicação"
    return "Você sabia?"
series=pillar(category+" "+title)
keywords=[w.lower() for w in re.findall(r"\w+",title,flags=re.UNICODE) if len(w)>3][:5]
tags=["#curiosidades","#ciencia"]
if series.startswith("Universo"):tags+=["#universo","#astronomia"]
elif series.startswith("História"):tags+=["#historia","#fatoshistoricos"]
elif series.startswith("Ciência"):tags+=["#cienciaexplicada","#aprendizado"]
else:tags+=["#voceSabia","#fatos"]
description=(f"{title.capitalize()}? Descubra a explicação neste Reel.\n\n"
    f"Você já sabia? Conte nos comentários, salve para lembrar e compartilhe com alguém curioso. "
    f"Siga @curiosidades.infinitas.nv para descobrir algo novo todos os dias.\n\n"
    + " ".join(tags))
assets={"series":series,"cover_title":meta["title"],"caption":description,
        "keywords":keywords,"hashtags":tags,"duration_s":duration,
        "recommended_duration_s":[15,35],
        "duration_within_target":15<=duration<=35,
        "sources":sources,"manual_review_required":True,
        "note":"Revise o roteiro, os direitos da mídia e a exatidão do fato antes de publicar. Não há publicação automática."}
(ROOT/"instagram-post.json").write_text(json.dumps(assets,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
(ROOT/"instagram-legenda.txt").write_text(description+"\n",encoding="utf-8")
print("Instagram assets generated; duration within target:",assets["duration_within_target"])
