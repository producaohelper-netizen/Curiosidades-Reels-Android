#!/usr/bin/env python3
"""Build-time checks for the topic-specific growth and trend selection patches."""
from pathlib import Path
growth=Path("scripts/patch-growth.py").read_text(encoding="utf-8")
trends=Path("scripts/patch-trends.py").read_text(encoding="utf-8")
workflow=Path(".github/workflows/gerar-apk.yml").read_text(encoding="utf-8")
assert "f.title" in growth and "f.fact" in growth
assert "callToAction" in growth and "HOOKS[Math.floorMod" not in growth
assert "return matched.get(0)" in trends
assert "if(!matched.isEmpty())" in trends
assert "java.util.regex.Pattern.quote" in trends
assert "python3 scripts/patch-growth.py" in workflow
assert "python3 scripts/patch-trends.py" in workflow
print("Topic-specific growth and ranked trend selection: OK")
