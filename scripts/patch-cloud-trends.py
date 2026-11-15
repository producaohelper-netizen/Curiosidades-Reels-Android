#!/usr/bin/env python3
"""Curated, sourced explanations for science topics appearing in Brazilian trends."""
from pathlib import Path
p=Path("cloud/gerar_reel.py")
s=p.read_text(encoding="utf-8")
marker="if __name__=='__main__':asyncio.run(main())"
assert s.count(marker)==1
addition="""CATALOG['elnino'] = {
 'match':['el niño','el nino','elnino'],
 'title':'POR QUE O EL NIÑO MUDA O TEMPO?',
 'label':'CIÊNCIA DO CLIMA',
 'art':'globe',
 'sources':[{'name':'NOAA Climate.gov','url':'https://www.climate.gov/enso'}],
 'lines':[
  ['O El Niño pode mudar o tempo em vários países!','O CLIMA MUDA!','globe'],
  ['Tudo começa com águas mais quentes no Oceano Pacífico.','OCEANO MAIS QUENTE','globe'],
  ['Isso muda a circulação do ar e o caminho das chuvas.','VENTOS E CHUVAS','arrows'],
  ['Algumas regiões podem receber mais chuva que o normal.','MAIS CHUVA?','rain'],
  ['Outras podem enfrentar períodos mais secos.','MENOS CHUVA?','sun'],
  ['No Brasil, o efeito varia de uma região para outra.','DEPENDE DA REGIÃO','globe'],
  ['E cada evento pode ser diferente do anterior.','NÃO É SEMPRE IGUAL','sparkle'],
  ['Você já percebeu alguma mudança no clima da sua cidade?','CONTA AQUI!','globe']
 ]
}
"""
s=s.replace(marker,addition+"\n"+marker)
p.write_text(s,encoding="utf-8")
print("Cloud: sourced El Niño explanation added to curated trend library")
