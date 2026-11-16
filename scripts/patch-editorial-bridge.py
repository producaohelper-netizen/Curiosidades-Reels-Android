#!/usr/bin/env python3
"""Bridge approved editorial scripts to Android without inventing a default story."""
from pathlib import Path
root=Path("app/src/main/java/br/com/helper/reels")
java=r'''package br.com.helper.reels;
import android.content.Context;
import org.json.JSONObject;
import java.io.InputStream;
import java.io.ByteArrayOutputStream;
import java.nio.charset.StandardCharsets;
/** The renderer can only read a reviewed editorial package, never an arbitrary trend. */
public final class EditorialQueue {
    public static FactCatalog.Selection load(Context context) throws Exception {
        InputStream in;
        try { in=context.getAssets().open("editorial-approved.json"); }
        catch(java.io.IOException e){return null;}
        try(in;ByteArrayOutputStream out=new ByteArrayOutputStream()){
            byte[] buf=new byte[4096];int n;
            while((n=in.read(buf))!=-1){
                out.write(buf,0,n);
                if(out.size()>32000)throw new Exception("Pauta editorial excede tamanho permitido");
            }
            JSONObject obj=new JSONObject(out.toString("UTF-8"));
            if(!obj.optBoolean("review_approved",false) || obj.optBoolean("review_required",true))
                throw new Exception("Pauta ainda não aprovada");
            String title=obj.optString("title",""),script=obj.optString("script","");
            org.json.JSONArray sources=obj.optJSONArray("sources");
            if(title.length()<10||script.length()<180||sources==null||sources.length()<2)
                throw new Exception("Pauta sem roteiro completo ou fontes");
            String source=sources.getString(0),confirmation=sources.getString(1);
            if(!source.startsWith("https://")||!confirmation.startsWith("https://")||source.equals(confirmation))
                throw new Exception("Fontes inválidas");
            String pillar=obj.optString("pillar","");
            if(!java.util.Arrays.asList("historia_real","ciencia_natureza","misterios_documentados","cotidiano").contains(pillar))
                throw new Exception("Pilar fora do plano");
            FactCatalog.Fact fact=new FactCatalog.Fact(
                "editorial:"+FactCatalog.fold(title),title,FactCatalog.fold(title),
                script,"Pauta revisada: "+source+" | "+confirmation,source,"earth");
            return new FactCatalog.Selection(fact,"",false);
        }
    }
    private EditorialQueue(){}
}
'''
(root/"EditorialQueue.java").write_text(java,encoding="utf-8")
p=root/"MainActivity.java";s=p.read_text(encoding="utf-8")
needle='                final FactCatalog.Selection choice=candidate;'
assert needle in s,"Candidate finalization changed"
s=s.replace(needle,'''                // Only an approved editorial package may enter the new generation pipeline.
                candidate=EditorialQueue.load(getApplicationContext());
                if(candidate==null)
                    throw new Exception("Nenhuma história revisada na fila editorial. Importe uma pauta aprovada antes de gerar.");
                final FactCatalog.Selection choice=candidate;''',1)
# Ensure old arbitrary requests never enter the pipeline; a bundled reviewed story is the only input.
p.write_text(s,encoding="utf-8")
print("Android editorial queue bridge: only approved packaged story reaches renderer")
