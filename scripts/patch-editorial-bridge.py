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
        java.io.File imported=new java.io.File(context.getFilesDir(),"editorial-approved.json");
        if(imported.isFile()){
            in=new java.io.FileInputStream(imported);
        }else{
            try { in=context.getAssets().open("editorial-approved.json"); }
            catch(java.io.IOException e){return null;}
        }
        try(in;ByteArrayOutputStream out=new ByteArrayOutputStream()){
            byte[] buf=new byte[4096];int n;
            while((n=in.read(buf))!=-1){
                out.write(buf,0,n);
                if(out.size()>32000)throw new Exception("Pauta editorial excede tamanho permitido");
            }
            JSONObject payload=new JSONObject(out.toString("UTF-8"));
            JSONObject obj=payload;
            org.json.JSONArray queue=payload.optJSONArray("stories");
            if(queue!=null){
                if(queue.length()==0 || queue.length()>30)
                    throw new Exception("Fila editorial deve conter de 1 a 30 histórias");
                java.util.Set<String> exported=context.getSharedPreferences(
                    "MainActivity",Context.MODE_PRIVATE).getStringSet(
                        "exported_editorial_keys",java.util.Collections.emptySet());
                obj=null;
                for(int i=0;i<queue.length();i++){
                    JSONObject candidate=queue.getJSONObject(i);
                    String candidateTitle=candidate.optString("title","");
                    String candidateKey="editorial:"+FactCatalog.fold(candidateTitle);
                    if(!exported.contains(candidateKey)){obj=candidate;break;}
                }
                if(obj==null)throw new Exception("Todas as histórias da fila já foram exportadas");
            }
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
                if(scene.optBoolean("is_reused_social_video",false))
                    throw new Exception("Vídeo reutilizado de rede social não permitido");
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
                    .setPositiveButton("Importar JSON", (dialog,which)->{
                        android.content.Intent pick=new android.content.Intent(
                            android.content.Intent.ACTION_OPEN_DOCUMENT);
                        pick.addCategory(android.content.Intent.CATEGORY_OPENABLE);
                        pick.setType("application/json");
                        startActivityForResult(pick,7421);
                    })
                    .setNegativeButton("Cancelar",null).show();
                return;
            }
        }
"""
s=s.replace(needle,guard,1)
# Import into app-private storage; do not silently accept a package that fails
# the same editorial validation used for bundled assets.
activity_result="""    @Override
    protected void onActivityResult(int requestCode,int resultCode,android.content.Intent data){
        super.onActivityResult(requestCode,resultCode,data);
        if(requestCode!=7421 || resultCode!=RESULT_OK || data==null || data.getData()==null)return;
        java.io.File target=new java.io.File(getFilesDir(),"editorial-approved.json");
        java.io.File temporary=new java.io.File(getFilesDir(),"editorial-pending.json");
        try(java.io.InputStream input=getContentResolver().openInputStream(data.getData());
            java.io.FileOutputStream output=new java.io.FileOutputStream(temporary)){
            if(input==null)throw new Exception("Arquivo indisponível");
            byte[] buf=new byte[4096];int n,total=0;
            while((n=input.read(buf))!=-1){
                total+=n;
                if(total>32000)throw new Exception("JSON excede 32 KB");
                output.write(buf,0,n);
            }
            output.flush();
            // Temporarily stage the imported package under the production name
            // and roll back if validation fails.
            java.io.File backup=new java.io.File(getFilesDir(),"editorial-backup.json");
            if(backup.exists())backup.delete();
            boolean hadOld=target.exists();
            if(hadOld && !target.renameTo(backup))
                throw new Exception("Não foi possível preservar a fila anterior");
            try{
                if(!temporary.renameTo(target))throw new Exception("Falha ao salvar pacote");
                FactCatalog.Selection selected=EditorialQueue.load(getApplicationContext());
                if(selected==null)throw new Exception("Pacote sem pauta disponível");
                if(backup.exists())backup.delete();
                new android.app.AlertDialog.Builder(this)
                    .setTitle("Fila editorial importada")
                    .setMessage("Próxima história: "+selected.fact.title)
                    .setPositiveButton("OK",null).show();
            }catch(Exception invalid){
                target.delete();
                if(hadOld)backup.renameTo(target);
                throw invalid;
            }
        }catch(Exception e){
            temporary.delete();
            new android.app.AlertDialog.Builder(this)
                .setTitle("Importação rejeitada")
                .setMessage(e.getMessage())
                .setPositiveButton("OK",null).show();
        }
    }
"""
s=s.replace(needle,activity_result+guard,1)
# Remove misleading legacy controls from the public-facing interface. Test
# actions still set the same fields programmatically for emulator coverage.
s=s.replace('trends.setText("Somente tendências reais e inéditas do Google Trends Brasil")',
            'trends.setText("Histórias revisadas — sem tendências automáticas")')
s=s.replace('        if(!smoke){','        if(!smoke){',1)
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
                    java.util.Set<String> exported=getPreferences(0)
                        .getStringSet("exported_editorial_keys",java.util.Collections.emptySet());
                    if(exported.contains(choice.fact.key))
                        throw new Exception("Esta história já foi exportada. Carregue uma nova pauta revisada.");
                }''',1)
# Ensure an approved story can be selected even when the legacy catalog has no match.
# This is a textual substitution, not a broad regex over the Java method.
guard_text="if(candidate==null)throw new Exception"
assert s.count(guard_text)==1, "Legacy candidate guard changed"
s=s.replace(guard_text,'''if(candidate==null && ("br.com.helper.reels.TEST_DYNAMIC_VIDEO".equals(getIntent().getAction())
                    || "br.com.helper.reels.TEST_GENERATION".equals(getIntent().getAction())))throw new Exception''',1)
# Record the editorial ID only after a successful MediaStore publication.
# A failed render must never consume a reviewed story.
published='                getContentResolver().update(uri,ok,null,null);'
assert published in s, "MP4 publication marker changed"
s=s.replace(published,published+'''
                if(choice.fact.key.startsWith("editorial:")){
                    java.util.Set<String> exported=new java.util.HashSet<>(
                        getPreferences(0).getStringSet("exported_editorial_keys",
                            java.util.Collections.emptySet()));
                    exported.add(choice.fact.key);
                    getPreferences(0).edit().putStringSet("exported_editorial_keys",exported).apply();
                }''',1)
p.write_text(s,encoding="utf-8")
# Editorial scripts already contain a reviewed hook, reveal and CTA. Do not
# append the legacy generic hook and CTA a second time.
builder=root/"ScriptBuilder.java"
story=builder.read_text(encoding="utf-8")
marker='String narration=hook+" "+f.fact+" "+callToAction;'
assert story.count(marker)==1, "Legacy narration builder changed"
story=story.replace(marker,'String narration=f.key.startsWith("editorial:") ? f.fact : hook+" "+f.fact+" "+callToAction;',1)
builder.write_text(story,encoding="utf-8")
print("Production generation gated on editorial approval; reviewed narration preserved")

