#!/usr/bin/env python3
import importlib.util
from datetime import date
s=importlib.util.spec_from_file_location("editorial","scripts/editorial-30dias.py")
m=importlib.util.module_from_spec(s);s.loader.exec_module(m)
assert sum(m.allocation().values())==30
assert m.allocation()=={"historia_real":10,"ciencia_natureza":9,"misterios_documentados":6,"cotidiano":5}
sample={"title":"Uma história documentada","pillar":"historia_real","source_primary":"https://example.org/primary","source_confirmation":"https://example.net/confirm","facts":["Um fato"],"hook":"O que aconteceu?","reveal":"Aqui está a resposta","cta":"Compartilhe","confidence":"high","claim_status":"documented"}
assert m.validate(sample,set())[0]
assert not m.validate(sample,{"uma historia documentada"})[0]
assert not m.validate(dict(sample,source_confirmation=sample["source_primary"]),set())[0]
assert not m.validate(dict(sample,is_sensitive=True),set())[0]
result=m.plan([sample],days=30,start=date(2026,11,15))
assert len(result["scheduled"])==30
assert sum(x["status"]=="ready_for_editorial_review" for x in result["scheduled"])==1
assert sum(x["status"]=="needs_verified_story" for x in result["scheduled"])==29
assert result["scheduled"][0]["date"]=="2026-11-15"
print("Editorial scheduler tests PASS")
