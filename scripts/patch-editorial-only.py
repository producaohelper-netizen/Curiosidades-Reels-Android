#!/usr/bin/env python3
"""Editorial-only migration safety check.
Legacy video modes are not approved for the new product; do not silently
disable all rendering. This migration remains opt-in until verified stories
are connected to the Android renderer and end-to-end smoke tests are updated.
"""
from pathlib import Path
p=Path("app/src/main/java/br/com/helper/reels/MainActivity.java")
s=p.read_text(encoding="utf-8")
assert "private void generate()" in s, "Generation entry point changed"
assert "DynamicTopic.choose" in s, "Legacy selection path changed"
print("Editorial migration prerequisite checked; legacy app unchanged pending replacement")
