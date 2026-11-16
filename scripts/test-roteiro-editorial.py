#!/usr/bin/env python3
import importlib.util
from pathlib import Path
p=Path("scripts/roteiro-editorial.py")
spec=importlib.util.spec_from_file_location("script_editor",p);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
item={"title":"A descoberta documentada","pillar":"historia_real","source_primary":"https://example.org/one","source_confirmation":"https://example.net/two","confidence":"high","claim_status":"documented","review_approved":True,"hook":"Um detalhe pequeno mudou a investigação de forma inesperada.","context":"O episódio foi registrado e analisado por pesquisadores em documentos públicos.","facts":["O primeiro documento apresenta a cronologia dos acontecimentos e identifica os envolvidos.","O segundo registro confirma a sequência principal e explica como o erro foi identificado.","Uma análise posterior compara os registros e mostra por que a conclusão inicial estava incompleta."],"reveal":"A conclusão foi corrigida quando os documentos foram comparados diretamente.","cta":"Você conhecia essa história? Compartilhe com alguém que gosta de fatos históricos.","source_notes":"As duas fontes independentes precisam ser lidas e verificadas por um editor antes da publicação."}
result=m.produce(item)
assert result["word_count"]>=58
assert result["review_approved"] is True
assert len(result["sources"])==2
assert result["segments"]["hook"]==item["hook"]
try:m.produce(dict(item,review_approved=False))
except ValueError:pass
else:raise AssertionError("unreviewed story accepted")
try:m.produce(dict(item,source_confirmation=item["source_primary"]))
except ValueError:pass
else:raise AssertionError("duplicate source accepted")
try:m.produce(dict(item,pillar="misterios_documentados"))
except ValueError:pass
else:raise AssertionError("mystery without distinctions accepted")
print("Story script editorial tests PASS")
