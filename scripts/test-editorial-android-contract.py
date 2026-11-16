#!/usr/bin/env python3
"""Validate the embedded Android editorial contract without synthetic stories in APK."""
from pathlib import Path
p=Path("app/src/main/java/br/com/helper/reels/EditorialQueue.java")
s=p.read_text(encoding="utf-8")
for required in ("editorial-approved.json","review_approved","review_required","reviewer","reviewed_at","source","confirmation","assets","license","attribution","historia_real","ciencia_natureza","misterios_documentados","cotidiano"):
 assert required in s,required
assert "return null;" in s, "Absent approved story must not be fabricated"
assert "Pauta ainda não aprovada" in s
assert "is_reused_social_video" in s
assert "Fontes do mesmo publicador" in s
assert "Fontes do mesmo publicador" in s
print("Android editorial queue contract PASS")

main=Path("app/src/main/java/br/com/helper/reels/MainActivity.java").read_text(encoding="utf-8")
assert "Pauta editorial obrigatória" in main
assert "choice=EditorialQueue.load(getApplicationContext())" in main
assert "Pauta editorial obrigatória" in main
print("Public generation gate PASS")

builder=Path("app/src/main/java/br/com/helper/reels/ScriptBuilder.java").read_text(encoding="utf-8")
assert 'f.key.startsWith("editorial:") ? f.fact' in builder, "Approved narration must not be rewritten"
print("Reviewed narration preservation PASS")

assert 'exported_editorial_keys' in main
assert 'exported.contains(choice.fact.key)' in main
assert 'Esta história já foi exportada' in main
assert main.index('getContentResolver().update(uri,ok,null,null);') < main.index('putStringSet("exported_editorial_keys"')
print("Editorial duplicate-export guard PASS")

assert 'payload.optJSONArray("stories")' in s
assert 'queue.length()>30' in s
assert 'exported.contains(candidateKey)' in s
assert 'Todas as histórias da fila já foram exportadas' in s
print("Multi-story editorial queue selection contract PASS")

assert 'new java.io.File(context.getFilesDir(),"editorial-approved.json")' in s
assert 'ACTION_OPEN_DOCUMENT' in main
assert 'startActivityForResult(pick,7421)' in main
assert 'EditorialQueue.load(getApplicationContext())' in main
assert 'editorial-backup.json' in main
assert 'Importação rejeitada' in main
print("Android editorial JSON import and rollback contract PASS")

assert 'titles.add(candidateKey)' in s
assert 'Fila contém pauta sem aprovação editorial' in s
assert 'if(obj==null && !exported.contains(candidateKey))obj=candidate;' in s
print("Editorial queue duplicate and approval scan PASS")

assert 'Fila contém pauta incompleta' in s
assert 'Fila contém mídia não validada' in s
assert 'for(int j=0;j<candidateMedia.length();j++)' in s
assert 'Fila contém fontes sem independência' in s
print("Full editorial queue validation contract PASS")

assert 'out.size()>1048576' in s, "Editorial queue reader must support up to 1 MiB"
assert 'total>1048576' in main, "Android import must match queue reader size cap"
assert 'application/octet-stream' in main and 'text/plain' in main
assert 'JSON excede 1 MB' in main
print("Thirty-story import capacity and JSON MIME support PASS")
