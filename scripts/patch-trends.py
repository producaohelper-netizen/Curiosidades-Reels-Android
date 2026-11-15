#!/usr/bin/env python3
"""Pick highest ranked Google Trends topic with best verified semantic match."""
from pathlib import Path
p=Path("app/src/main/java/br/com/helper/reels/FactCatalog.java")
s=p.read_text(encoding="utf-8")
start=s.index('        if(requested != null && !requested.trim().isEmpty()){')
end=s.index('    private FactCatalog(){}',start)
replacement=r'''        if(requested != null && !requested.trim().isEmpty()){
            String needle=fold(requested);
            Fact best=null;int bestScore=0;
            for(Fact f:FACTS){
                int score=matchScore(f,needle);
                if(score>bestScore){best=f;bestScore=score;}
            }
            return best==null?null:new Selection(best,"",false);
        }
        // RSS items are ranked: use the first eligible trend. Within that item,
        // select the strongest phrase match rather than catalog declaration order.
        if(trends!=null)for(String t:trends){
            String clean=fold(t);
            Fact best=null;int bestScore=0;
            for(Fact f:FACTS){
                int score=matchScore(f,clean);
                if(score>bestScore){best=f;bestScore=score;}
            }
            if(best!=null)return new Selection(best,t,true);
        }
        // No verified relation to the live trends. Never claim a trend match.
        Fact fallback=FACTS[Math.floorMod(historyCounter+3,FACTS.length)];
        return new Selection(fallback,"",false);
    }
    static boolean matches(Fact fact,String text){return matchScore(fact,text)>0;}
    static int matchScore(Fact fact,String text){
        int best=0;
        for(String tag:fact.tags.split(";")){
            String normalized=fold(tag);
            if(normalized.length()<3)continue;
            String regex="(?:^|\\s)"+java.util.regex.Pattern.quote(normalized)+"(?:$|\\s)";
            if(java.util.regex.Pattern.compile(regex).matcher(text).find()){
                int score=normalized.length();
                if(normalized.equals(fact.key))score+=50;
                if(normalized.equals(text))score+=100;
                if(score>best)best=score;
            }
        }
        return best;
    }
'''
s=s[:start]+replacement+s[end:]
p.write_text(s,encoding="utf-8")
print("TREND FIX: highest ranked eligible RSS item, strongest fact match, no false labels")
