#!/usr/bin/env python3
"""Validate the embedded Android editorial contract without synthetic stories in APK."""
from pathlib import Path
p=Path("app/src/main/java/br/com/helper/reels/EditorialQueue.java")
s=p.read_text(encoding="utf-8")
for required in ("editorial-approved.json","review_approved","review_required","reviewer","reviewed_at","source","confirmation","assets","license","attribution","historia_real","ciencia_natureza","misterios_documentados","cotidiano"):
 assert required in s,required
assert "return null;" in s, "Absent approved story must not be fabricated"
assert "Pauta ainda não aprovada" in s
assert "Fontes do mesmo publicador" in s
print("Android editorial queue contract PASS")
