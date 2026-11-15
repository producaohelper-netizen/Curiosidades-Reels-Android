#!/usr/bin/env python3
"""Strict trending mode: never use offline catalog, persist used topics, fail closed."""
from pathlib import Path
catalog=Path("app/src/main/java/br/com/helper/reels/FactCatalog.java")
s=catalog.read_text(encoding="utf-8")
anchor='    static boolean matches(Fact fact,String text){'
assert anchor in s
addition='''    // Strict mode: only verified RSS matches that were never generated before.
    // Return null rather than inventing a trending topic.
    public static Selection chooseFresh(List<String> trends, java.util.Set<String> used){
        if(trends==null)return null;
        for(String t:trends){
            String clean=fold(t);
            Fact best=null;int score=0;
            for(Fact f:FACTS){
                if(used!=null && used.contains(f.key))continue;
                int value=matchScore(f,clean);
                if(value>score){best=f;score=value;}
            }
            if(best!=null)return new Selection(best,t,true);
        }
        return null;
    }
'''
s=s.replace(anchor,addition+anchor,1)
catalog.write_text(s,encoding="utf-8")
p=Path("app/src/main/java/br/com/helper/reels/MainActivity.java")
s=p.read_text(encoding="utf-8")
old='''                    }catch(Exception e){feedNote="Trends indisponível; catálogo verificado offline";}
'''
new='''                    }catch(Exception e){
                        throw new Exception("Não foi possível consultar o Google Trends Brasil: "+e.getMessage()+". Verifique a internet e tente novamente.");
                    }
'''
assert old in s
s=s.replace(old,new)
old='''                FactCatalog.Selection choice=FactCatalog.choose(titles,sequence,requested);
'''
new='''                String usedRaw=getPreferences(0).getString("used_trend_fact_keys","");
                java.util.Set<String> usedKeys=new java.util.HashSet<>();
                for(String key:usedRaw.split(";"))if(!key.isEmpty())usedKeys.add(key);
                FactCatalog.Selection choice=(fetchTrends&&requested.isEmpty())
                    ?FactCatalog.chooseFresh(titles,usedKeys)
                    :FactCatalog.choose(titles,sequence,requested);
                if(fetchTrends&&requested.isEmpty()&&choice==null)
                    throw new Exception("Nenhum assunto em alta disponível com roteiro verificado e ainda não utilizado. Nenhum vídeo genérico será gerado.");
'''
assert old in s
s=s.replace(old,new)
old='''                getPreferences(0).edit().putInt("generated_count",sequence+1).apply();
'''
new='''                android.content.SharedPreferences.Editor prefs=getPreferences(0).edit().putInt("generated_count",sequence+1);
                if(choice.trending)prefs.putString("used_trend_fact_keys",usedRaw+choice.fact.key+";");
                prefs.apply();
'''
assert old in s
s=s.replace(old,new)
s=s.replace('Sem dados recentes do Trends, o app usa outro tema previamente verificado.',
            'No modo Trends, sem tendência verificada ou inédita, o app não gera vídeo. Desmarque para usar o catálogo.')
s=s.replace('trends.setText("Priorizar assuntos em alta no Google Trends Brasil")',
            'trends.setText("Somente tendências reais e inéditas do Google Trends Brasil")')
p.write_text(s,encoding="utf-8")
print("Strict Trends: no catalog fallback, no repeated topic keys, explicit feed errors")
