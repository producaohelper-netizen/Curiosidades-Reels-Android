#!/usr/bin/env python3
"""Adds a short-form storytelling hook and a restrained follow CTA to the existing Android pipeline."""
from pathlib import Path
p=Path("app/src/main/java/br/com/helper/reels/ScriptBuilder.java")
s=p.read_text(encoding="utf-8")
old='String narration=f.fact;'
assert s.count(old)==1, "Expected subject-only narration from patch-captions-v4.py"
new='''String narration=HOOKS[Math.floorMod(sequence,HOOKS.length)] + " " + f.fact
                + " Você já sabia? Siga para descobrir mais curiosidades.";'''
s=s.replace(old,new)
p.write_text(s,encoding="utf-8")
print("Growth narration: opening hook + verified catalog fact + one CTA")
