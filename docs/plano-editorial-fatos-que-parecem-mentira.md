# Fatos Que Parecem Mentira — especificação editorial v1

## Promessa
Histórias reais, mistérios documentados e curiosidades surpreendentes, narrados em menos de 1 minuto. Público leigo, português do Brasil. Facebook prioritário, Instagram secundário.

## Quatro pilares (30 dias)
História real 35%; ciência e natureza 30%; mistérios documentados 20%; cotidiano 15%. Para 30 vídeos, arredondamento determinístico: 11, 9, 6, 4, respectivamente. O aplicativo deve permitir ajustar a distribuição depois de medir retenção e compartilhamentos.

## Pipeline obrigatório antes de exportar
1. Descobrir pauta em tendência ou fila editorial. Tema livre só entra se for verificável e apropriado ao perfil.
2. Bloquear repetição por título normalizado, entidade e similaridade semântica. A versão atual só implementa título normalizado no planejador; similaridade semântica está pendente.
3. Pesquisar pelo menos duas fontes independentes para histórias importantes, registrar links, data/local, fato versus hipótese e confiança. Wikipédia sozinha não prova notícia recente.
4. Gerar roteiro original com gancho (0–2s), contexto (2–6s), desenvolvimento, revelação e CTA. Não alegar um fato não encontrado nas fontes.
5. Validar que há ao menos três elementos de retenção (pergunta, promessa, contradição, revelação etc.) sem clickbait.
6. Escolher imagens/vídeos diretamente pertinentes a cada cena e registrar licença/atribuição. Se não houver mídia adequada, usar ilustrações próprias identificadas, nunca imagem factual falsa.
7. Gerar narração clara, legendas sincronizadas, 9:16, duração-alvo 25–45s, sem introdução com logo.
8. Verificar áudio, duração, fontes, licença, conformidade editorial e exportar. A publicação exige aprovação editorial para alegações sensíveis.
9. Salvar vídeo, legenda, 3–5 hashtags e ficha de fontes. Não publicar automaticamente apenas porque a renderização foi bem-sucedida.
10. Registrar desempenho após 24, 48 e 72 horas: alcance, retenção, compartilhamentos, salvamentos, seguidores por vídeo.

## Estado técnico
- Android: consulta dinâmica de resumo enciclopédico e exportação MP4 testadas para um assunto fora do catálogo.
- Planejador em `scripts/editorial-30dias.py`: distribuição, links distintos, bloqueio de título repetido, checagem de confiança, rejeição de pautas incompletas. Gera `planning/plano-editorial-30dias.json` e CSV.
- **Não implementado**: duas fontes efetivamente verificadas por conteúdo (o planejador só verifica campos/URLs), notícias em tempo real, checagem automática de afirmações, classificação semântica, mídias licenciadas por cena, análise de métricas conectada ao Facebook.
- Se faltar pauta validada, registrar `needs_verified_story`; não inventar histórias para preencher calendário.

## Regra de aprovação
Nenhum vídeo pode ser rotulado 'história real verificada' com uma única fonte enciclopédica. Conteúdos de mistério devem distinguir comprovado, hipótese e desconhecido.

## Decisão de escopo — edição exclusiva (15/11/2026)
O usuário determinou que **somente as regras deste plano** podem orientar a nova edição. Recursos antigos podem ser removidos. A migração deverá substituir, não simplesmente esconder, o fluxo anterior:
- REMOVER da nova interface: opção de gerar sobre qualquer tema, botão de Google Trends irrestrito, rotação aleatória do catálogo, roteiros genéricos e geração sem fontes suficientes.
- MANTER por necessidade do plano: renderizador MP4 9:16, narração, legendas sincronizadas, exportação e histórico antirrepetição.
- ADICIONAR: fila de pautas editoriais verificadas, quatro pilares e pesos, ficha de duas fontes, gancho-contexto-desenvolvimento-revelação-CTA, controle de duração, registro de licenças de mídia, métricas 24/48/72h.
- O teste de vídeo dinâmico anterior permanece **legado** e não comprova o novo produto.
- **Critério para desativar o legado:** uma pauta aprovada deve ser renderizada em MP4 no emulador com fontes e roteiro editorial; então remover opções antigas e alterar o teste de CI para usar a nova pauta. Até isso ocorrer, não distribuir uma edição anunciada como pronta.
