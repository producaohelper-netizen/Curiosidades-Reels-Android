#!/usr/bin/env python3
"""Validate the embedded Android editorial contract without synthetic stories in APK."""
from pathlib import Path
p=Path("app/src/main/java/br/com/helper/reels/EditorialQueue.java")
s=p.read_text(encoding="utf-8")
for required in ("editorial-approved.json","review_approved","review_required","reviewer","reviewed_at","source","confirmation","assets","license","attribution","historia_real","ciencia_natureza","misterios_documentados","cotidiano"):
 assert required in s,required
assert "return null;" in s, "Absent approved story must not be fabricated"
assert "Pauta ainda não aprovada" in s
assert "is_reused_social_video" in s
assert "Fontes do mesmo publicador" in s
assert "Fontes do mesmo publicador" in s
print("Android editorial queue contract PASS")

main=Path("app/src/main/java/br/com/helper/reels/MainActivity.java").read_text(encoding="utf-8")
assert "Pauta editorial obrigatória" in main
assert "choice=EditorialQueue.load(getApplicationContext())" in main
assert "Pauta editorial obrigatória" in main
print("Public generation gate PASS")

builder=Path("app/src/main/java/br/com/helper/reels/ScriptBuilder.java").read_text(encoding="utf-8")
assert 'f.key.startsWith("editorial:") ? f.fact' in builder, "Approved narration must not be rewritten"
print("Reviewed narration preservation PASS")
