# Fluxo de aprovação de pautas — Fatos Que Parecem Mentira

A versão editorial aceita somente histórias revisadas. O aplicativo atual ainda
não ativa automaticamente esta fila; o componente Android já compila.

## Entrada
- Arquivo JSON de pauta com título, pilar, gancho, contexto, 2–5 fatos,
  revelação, CTA, duas fontes HTTPS de publicadores diferentes,
  notas de checagem, status de evidência e confiança.
- Revisão humana explícita: `review_approved: true`, `reviewer` e `reviewed_at`.
- Arquivo JSON de mídias: lista de cenas com `license`, `scene_text`,
  `description`; quando aplicável, `source_url` e `attribution`.

## Empacotamento
```bash
python3 scripts/empacotar-pauta-android.py --brief pauta.json --assets midias.json --output app/src/main/assets/editorial-approved.json
```

**Importante:** o empacotador confere campos e consistência formal, mas não
faz pesquisa independente nem comprova que as fontes sustentam as afirmações.
A pessoa revisora deve abrir as fontes e confirmar os fatos e os direitos das mídias.

## Critérios antes de substituir a interface antiga
1. Usar uma história real com revisão e evidências registradas.
2. Embutir o pacote aprovado no APK.
3. Integrar `EditorialQueue.load()` ao caminho de produção de MP4.
4. Validar no emulador o MP4 completo com áudio, duração e legendas.
5. Só então remover Google Trends, entrada livre e catálogo aleatório.
6. Manter versão anterior instalável em paralelo durante a transição.

Não publicar nem testar conteúdo sintético como se fosse uma história real.
