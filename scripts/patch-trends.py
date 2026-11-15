#!/usr/bin/env python3
"""Prefer real Google Trends RSS matches; never label catalog fallback as trending."""
from pathlib import Path
p=Path("app/src/main/java/br/com/helper/reels/FactCatalog.java")
s=p.read_text(encoding="utf-8")
start=s.index('        // Rotate through verified trends when available.')
end=s.index('    static boolean matches(',start)
replacement='''        // Google Trends RSS is ranked. Pick the highest ranked verified topic
        // every time; do not silently replace two out of three trends with a
        // generic catalog fact. Only rotate within equally eligible matches
        // when their RSS titles are genuinely distinct.
        if(!matched.isEmpty())
            return matched.get(0);
        // No safe semantic match: use a verified fallback, clearly NOT a trend.
        Fact next=FACTS[Math.floorMod(historyCounter+3,FACTS.length)];
        return new Selection(next,"",false);
    }
'''
s=s[:start]+replacement+s[end:]
old='''            if(text.contains(normalized))return true;'''
new='''            // Whole words/phrases only: "sol" must not match "consolidação".
            String pattern="(?:^|\\\\s)"+java.util.regex.Pattern.quote(normalized)+"(?:$|\\\\s)";
            if(java.util.regex.Pattern.compile(pattern).matcher(text).find())return true;'''
assert old in s
s=s.replace(old,new)
p.write_text(s,encoding="utf-8")
print("TREND FIX: ranked verified RSS match first, strict token boundaries, honest fallback")
