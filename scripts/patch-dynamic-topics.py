#!/usr/bin/env python3
"""Dynamic topics from Google Trends + Wikipedia summary; no fabricated facts."""
from pathlib import Path
root=Path("app/src/main/java/br/com/helper/reels")
java=r'''package br.com.helper.reels;
import java.net.*;
import java.io.*;
import java.util.*;
import org.json.*;
public final class DynamicTopic {
    static String read(String url) throws Exception {
        HttpURLConnection c=(HttpURLConnection)new URL(url).openConnection();
        c.setConnectTimeout(9000);c.setReadTimeout(10000);
        c.setRequestProperty("User-Agent","HelperReels/4.0 (educational video; Android)");
        try {
            if(c.getResponseCode()!=200)throw new IOException("HTTP "+c.getResponseCode());
            try(InputStream in=c.getInputStream();ByteArrayOutputStream out=new ByteArrayOutputStream()){
                byte[] buf=new byte[4096];int n;
                while((n=in.read(buf))!=-1){out.write(buf,0,n);if(out.size()>250000)throw new IOException("Response too large");}
                return out.toString("UTF-8");
            }
        }finally{c.disconnect();}
    }
    static String normalize(String s){return FactCatalog.fold(s);}
    static String firstSentence(String s){
        if(s==null)return "";
        s=s.replaceAll("\\s+"," ").trim();
        int dot=s.indexOf(". ");
        return dot>55?s.substring(0,dot+1):s;
    }
    static FactCatalog.Selection choose(List<String> trends,Set<String> used){
        if(trends==null)return null;
        for(String title:trends){
            String key=normalize(title);
            if(key.length()<4||used.contains("trend:"+key))continue;
            try{
                String query=URLEncoder.encode(title,"UTF-8");
                JSONObject search=new JSONObject(read("https://pt.wikipedia.org/w/api.php?action=query&list=search&srsearch="+query+"&srlimit=1&format=json"));
                JSONArray results=search.getJSONObject("query").getJSONArray("search");
                if(results.length()==0)continue;
                String article=results.getJSONObject(0).getString("title");
                String a=normalize(article),t=normalize(title);
                // Require a meaningful relationship between the trending query and the source title.
                if(!(a.equals(t)||a.contains(t)||t.contains(a)))continue;
                String page=URLEncoder.encode(article.replace(' ','_'),"UTF-8");
                JSONObject summary=new JSONObject(read("https://pt.wikipedia.org/api/rest_v1/page/summary/"+page));
                String extract=summary.optString("extract","");
                if(extract.length()<110||extract.length()>4000)continue;
                if(summary.optString("type","").equals("disambiguation"))continue;
                String source=summary.optJSONObject("content_urls")!=null?
                    summary.getJSONObject("content_urls").getJSONObject("desktop").getString("page"):
                    "https://pt.wikipedia.org/wiki/"+page;
                String factual=extract.length()>650?extract.substring(0,650):extract;
                int stop=factual.lastIndexOf(". ");
                if(stop>180)factual=factual.substring(0,stop+1);
                String headline="ENTENDA: "+article.toUpperCase(Locale.ROOT);
                String script="Por que "+article+" está chamando atenção? "+factual+
                    " O que mais você gostaria de saber sobre esse assunto? Comente!";
                FactCatalog.Fact fact=new FactCatalog.Fact("trend:"+key,headline,key,script,
                    "Wikipédia (resumo enciclopédico; não confirma notícias recentes)",source,"earth");
                return new FactCatalog.Selection(fact,title,true);
            }catch(Exception ignored){android.util.Log.w("HelperTrends","Sem fonte enciclopédica adequada para: "+title);}
        }
        return null;
    }
    private DynamicTopic(){}
}
'''
(root/"DynamicTopic.java").write_text(java,encoding="utf-8")
p=root/"MainActivity.java";s=p.read_text(encoding="utf-8")
old='''                if(fetchTrends&&requested.isEmpty()&&choice==null)
                    throw new Exception("Nenhum assunto em alta disponível com roteiro verificado e ainda não utilizado. Nenhum vídeo genérico será gerado.");'''
new='''                if(fetchTrends&&requested.isEmpty()&&choice==null)
                    choice=DynamicTopic.choose(titles,usedKeys);
                if(fetchTrends&&requested.isEmpty()&&choice==null)
                    throw new Exception("Nenhuma tendência inédita pôde ser relacionada a uma fonte enciclopédica confiável. Não será criado vídeo genérico.");'''
assert old in s
s=s.replace(old,new)
s=s.replace('if(choice.trending)prefs.putString("used_trend_fact_keys",usedRaw+choice.fact.key+";");',
'''if(choice.trending)prefs.putString("used_trend_fact_keys",usedRaw+choice.fact.key+";");''')
s=s.replace('FactCatalog.Selection choice=(fetchTrends&&requested.isEmpty())','FactCatalog.Selection candidate=(fetchTrends&&requested.isEmpty())')
s=s.replace('&&choice==null)','&&candidate==null)')
s=s.replace('choice=DynamicTopic.choose(titles,usedKeys);','candidate=DynamicTopic.choose(titles,usedKeys);')
s=s.replace('if(choice==null)throw new Exception','if(candidate==null)throw new Exception')
s=s.replace('                final String explain=choice.trending?', '                final FactCatalog.Selection choice=candidate;\\n                final String explain=choice.trending?')
p.write_text(s,encoding="utf-8")
print("Dynamic topic selection: live trends -> reviewed catalog OR sourced encyclopedia summary; no fabricated news claims")
