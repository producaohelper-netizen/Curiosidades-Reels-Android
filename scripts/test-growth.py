#!/usr/bin/env python3
"""Static regression checks for the Reels growth patch, runnable without Android SDK."""
from pathlib import Path
p=Path("scripts/patch-growth.py")
s=p.read_text(encoding="utf-8")
assert "s.count(old)==1" in s
assert "HOOKS[Math.floorMod(sequence,HOOKS.length)]" in s
assert "f.fact" in s
assert "Siga para descobrir mais curiosidades" in s
workflow=Path(".github/workflows/gerar-apk.yml").read_text(encoding="utf-8")
assert "python3 scripts/patch-growth.py" in workflow
print("Growth patch wiring: OK")
