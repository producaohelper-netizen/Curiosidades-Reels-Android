#!/usr/bin/env python3
"""14-day editorial experiment. Planning only: never auto-post to Instagram."""
import csv
from datetime import date,timedelta
from pathlib import Path
topics=[
 ("ESPAÇO","A Lua se afasta da Terra","Envie para quem ama astronomia"),
 ("CIÊNCIA","Por que o céu muda de cor?","Salve para explicar depois"),
 ("ESPAÇO","O planeta mais quente não é Mercúrio","Qual planeta você achava que era?"),
 ("CIÊNCIA","Por que sentimos eletricidade estática?","Já aconteceu com você?"),
 ("ESPAÇO","Por que o espaço é silencioso?","Envie para alguém curioso"),
 ("CIÊNCIA","Por que o arco-íris tem cores?","Salve esta explicação"),
 ("ESPAÇO","Como acontecem os eclipses?","Você já viu um eclipse?"),
 ("CIÊNCIA","Por que o trovão vem depois do raio?","Envie para alguém que ama tempestades"),
 ("ESPAÇO","O que são estrelas cadentes?","Qual foi a última vez que viu uma?"),
 ("CIÊNCIA","Por que as estrelas parecem piscar?","Salve para lembrar"),
 ("ESPAÇO","Por que Júpiter tem uma mancha gigante?","Você já sabia disso?"),
 ("CIÊNCIA","Por que a bola faz curva?","Envie para quem gosta de futebol"),
 ("ESPAÇO","O que aconteceria sem a Lua?","Quer uma parte 2?"),
 ("CIÊNCIA","Por que os vulcões entram em erupção?","Qual fato mais surpreendeu você?")
]
out=Path("planning");out.mkdir(exist_ok=True)
with (out/"plano-14-dias.csv").open("w",newline="",encoding="utf-8-sig") as f:
 w=csv.writer(f,delimiter=";")
 w.writerow(["dia","data_sugerida","horario_local_BRT","pilar","tema_proposto","cta","status","views_48h","retencao_3s","tempo_medio","compartilhamentos","salvamentos","seguidores_novos","observacoes"])
 for i,(pillar,topic,cta) in enumerate(topics):
  w.writerow([i+1,(date.today()+timedelta(days=i)).isoformat(),["12:00","18:00","21:00"][i//3%3],pillar,topic,cta,"PENDENTE","","","","","","",""])
print("14-day editorial plan created; one proposed publication per day, manual approval required")
