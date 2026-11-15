#!/usr/bin/env python3
"""Subject-specific opening, simple explanation and relevant one-line CTA."""
from pathlib import Path
p=Path("app/src/main/java/br/com/helper/reels/ScriptBuilder.java")
s=p.read_text(encoding="utf-8")
old='String narration=f.fact;'
assert s.count(old)==1,"Expected topic-only narration after captions patch"
new='''String hook=f.title.endsWith("?") ? f.title : f.title+"!";
        String callToAction;
        if("space".equals(f.scene)) callToAction="Envie para alguém que ama o espaço!";
        else if("ocean".equals(f.scene)) callToAction="Salve essa curiosidade do oceano!";
        else callToAction="Qual parte mais surpreendeu você? Conte nos comentários!";
        String narration=hook+" "+f.fact+" "+callToAction;'''
s=s.replace(old,new)
p.write_text(s,encoding="utf-8")
print("Growth: specific title hook, catalog fact and relevant CTA")
