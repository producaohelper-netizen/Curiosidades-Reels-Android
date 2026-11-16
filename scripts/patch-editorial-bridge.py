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
            if(obj.optString("reviewer","").trim().isEmpty() || obj.optString("reviewed_at","").trim().isEmpty())
                throw new Exception("Revisão editorial sem responsável e data");
            org.json.JSONArray media=obj.optJSONArray("assets");
            if(media==null||media.length()==0)throw new Exception("Pauta sem mídia revisada");
            for(int i=0;i<media.length();i++){
                JSONObject scene=media.getJSONObject(i);
                String license=scene.optString("license","");
                if(!java.util.Arrays.asList("original","public_domain","cc0","cc_by","licensed").contains(license)
                    ||scene.optString("scene_text","").isEmpty()
                    ||scene.optString("description","").isEmpty())
                    throw new Exception("Cena sem licença ou descrição");
                if(!"original".equals(license)&&!scene.optString("source_url","").startsWith("https://"))
                    throw new Exception("Cena sem origem da mídia");
                if("cc_by".equals(license)&&scene.optString("attribution","").isEmpty())
                    throw new Exception("Crédito obrigatório da mídia ausente");
            }
            java.net.URI first=new java.net.URI(source),second=new java.net.URI(confirmation);
            if(first.getHost()==null||second.getHost()==null||first.getHost().equalsIgnoreCase(second.getHost()))
                throw new Exception("Fontes devem ter origens diferentes");
            String pillar=obj.optString("pillar","");
            if(!java.util.Arrays.asList("historia_real","ciencia_natureza","misterios_documentados","cotidiano").contains(pillar))
                throw new Exception("Pilar fora do plano");
            String hostA=first.getHost().toLowerCase(java.util.Locale.ROOT);
            String hostB=second.getHost().toLowerCase(java.util.Locale.ROOT);
            String[] aParts=hostA.split("\\.");
            String[] bParts=hostB.split("\\.");
            if(aParts.length>=2 && bParts.length>=2){
                String publisherA=aParts[aParts.length-2]+"."+aParts[aParts.length-1];
                String publisherB=bParts[bParts.length-2]+"."+bParts[bParts.length-1];
                if(publisherA.equals(publisherB))throw new Exception("Fontes do mesmo publicador");
            }
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
p=root/"MainActivity.java"
s=p.read_text(encoding="utf-8")
needle="    private void generate(){"
assert needle in s, "Android generation entry point changed"
guard="""    private void generate(){
        // Production must never create a video from trends or arbitrary prompts.
        // Existing emulator smoke actions are isolated codec/network tests.
        String action=getIntent()==null?"":getIntent().getAction();
        boolean smoke="br.com.helper.reels.TEST_DYNAMIC_VIDEO".equals(action)
            ||"br.com.helper.reels.TEST_GENERATION".equals(action);
        if(!smoke){
            try{
                FactCatalog.Selection approved=EditorialQueue.load(getApplicationContext());
                if(approved==null)throw new Exception("Importe uma história revisada antes de gerar.");
                // Story is approved; the worker below must use this exact selection.
            }catch(Exception e){
                new android.app.AlertDialog.Builder(this)
                    .setTitle("Pauta editorial obrigatória")
                    .setMessage(e.getMessage())
                    .setPositiveButton("Entendi",null).show();
                return;
            }
        }
"""
s=s.replace(needle,guard,1)
# The approved story overrides the legacy catalog only for normal user generation.
# Smoke tests continue using the existing emulator path.
worker='                final FactCatalog.Selection choice=candidate;'
assert worker in s, "Legacy selection handoff changed"
s=s.replace(worker,'''                final FactCatalog.Selection choice;
                if("br.com.helper.reels.TEST_DYNAMIC_VIDEO".equals(getIntent().getAction())
                    ||"br.com.helper.reels.TEST_GENERATION".equals(getIntent().getAction())){
                    choice=candidate;
                }else{
                    choice=EditorialQueue.load(getApplicationContext());
                    if(choice==null)throw new Exception("Nenhuma pauta editorial aprovada disponível");
                }''',1)
# Ensure an approved story can be selected even when the legacy catalog has no match.
# This is a textual substitution, not a broad regex over the Java method.
guard_text="if(candidate==null)throw new Exception"
assert s.count(guard_text)==1, "Legacy candidate guard changed"
s=s.replace(guard_text,'''if(candidate==null && ("br.com.helper.reels.TEST_DYNAMIC_VIDEO".equals(getIntent().getAction())
                    || "br.com.helper.reels.TEST_GENERATION".equals(getIntent().getAction())))throw new Exception''',1)
p.write_text(s,encoding="utf-8")
print("Production generation gated on editorial approval; emulator smoke preserved")

