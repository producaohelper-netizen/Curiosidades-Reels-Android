#!/usr/bin/env python3
"""Synthetic fixtures test validation only; never shipped as factual videos."""
import importlib.util
from pathlib import Path
p=Path("scripts/empacotar-pauta-android.py")
spec=importlib.util.spec_from_file_location("pack",p);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
brief={"title":"Exemplo sintético para teste","pillar":"historia_real","source_primary":"https://example.org/a","source_confirmation":"https://example.net/b","confidence":"high","claim_status":"documented","review_approved":True,"reviewer":"Editor de teste","reviewed_at":"2026-11-15","source_notes":"Exemplo fictício para validar o código, não deve ser publicado como fato.","hook":"Uma descoberta inesperada mudou tudo naquele momento.","context":"Este texto é apenas um teste de software e não descreve acontecimentos reais.","facts":["O primeiro trecho serve apenas para testar a estrutura do roteiro sem afirmar qualquer fato histórico.","O segundo trecho é igualmente fictício e existe para conferir a montagem do pacote editorial.","O terceiro trecho verifica o comprimento do texto e não deve ser publicado como notícia."],"reveal":"A revelação é que todos os elementos deste exemplo são dados sintéticos.","cta":"Este é um teste automatizado e não um vídeo para publicação."}
assets=[{"license":"original","scene_text":"Cena de teste","description":"Imagem criada para teste do software"}]
obj=m.package(brief,assets)
assert obj["review_approved"] is True and len(obj["assets"])==1
for changed in (dict(brief,review_approved=False),dict(brief,reviewer=""),dict(brief,source_confirmation="https://other.example.org/b")):
 try:m.package(changed,assets)
 except ValueError:pass
 else:raise AssertionError("Unapproved or unverified story packaged")
try:m.package(brief,[dict(assets[0],license="unknown")])
except ValueError:pass
else:raise AssertionError("Unlicensed scene packaged")
print("Android editorial package tests PASS")
