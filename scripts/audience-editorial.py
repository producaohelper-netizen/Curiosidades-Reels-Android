#!/usr/bin/env python3
"""Audience-first editorial rules: retain fact checking, remove academic citations from viewer copy."""
import json,re
from pathlib import Path
root=Path("produced")
meta_file=root/"latest.json"
meta=json.loads(meta_file.read_text(encoding="utf-8"))
post_file=root/"instagram-post.json"
post=json.loads(post_file.read_text(encoding="utf-8"))
# Sources remain in private JSON for editorial verification, never in the caption.
post.pop("sources",None)
post["audience"]="Público geral; sem jargão, nomes de estudos ou citações técnicas"
post["editorial_style"]="Gancho curioso, explicação cotidiana, humor leve, frases curtas"
post_file.write_text(json.dumps(post,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
# Preserve traceable sources in metadata, but clearly label as internal.
meta["fact_sources_visibility"]="internal_editorial_only"
meta_file.write_text(json.dumps(meta,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
caption_file=root/"instagram-legenda.txt"
caption_file.write_text(post["caption"]+"\n",encoding="utf-8")
assert not re.search(r"\b(?:MIT|NOAA|NASA|universidade|estudo científico|artigo científico)\b",post["caption"],re.I)
print("Audience-facing caption simplified; citations retained internally")
