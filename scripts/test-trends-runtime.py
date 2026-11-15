#!/usr/bin/env python3
"""Compile and exercise the actual Android topic selector on the JVM."""
from pathlib import Path
import subprocess,tempfile
src=Path("app/src/main/java/br/com/helper/reels/FactCatalog.java")
with tempfile.TemporaryDirectory() as d:
 root=Path(d)
 test=root/"TrendSelectorTest.java"
 test.write_text("""package br.com.helper.reels;
import java.util.Arrays;
import java.util.Collections;
public class TrendSelectorTest {
  static void ok(boolean b,String m){if(!b)throw new AssertionError(m);}
  public static void main(String[] args){
    FactCatalog.Selection a=FactCatalog.choose(Arrays.asList("Campeonato de futebol","Eclipse solar","Lua cheia"),1,"");
    ok(a.trending,"A real trend must be selected on every press");
    ok(a.fact.key.equals("eclipse"),"Highest-ranked eligible trend must win");
    ok(a.trend.equals("Eclipse solar"),"Original RSS title must be retained");
    FactCatalog.Selection en=FactCatalog.choose(Arrays.asList("El Niño","Campeonato"),1,"");
    ok(en.trending && en.fact.key.equals("elnino"),"Relevant Brazilian climate trend must be selectable");
    FactCatalog.Selection b=FactCatalog.choose(Arrays.asList("Consolidação financeira"),3,"");
    ok(!b.trending,"Substring sol cannot be considered solar trend");
    FactCatalog.Selection c=FactCatalog.choose(Collections.emptyList(),5,"");
    ok(!c.trending,"Catalog fallback must not claim to be trending");
    ok(FactCatalog.choose(Collections.emptyList(),5,"assunto inexistente")==null,"Unverified requests must fail");
    System.out.println("TREND RUNTIME PASS: ranked match, strict words, fallback, unverified request");
  }
}
""",encoding="utf-8")
 subprocess.run(["javac","-d",d,str(src),str(test)],check=True)
 subprocess.run(["java","-cp",d,"br.com.helper.reels.TrendSelectorTest"],check=True)
