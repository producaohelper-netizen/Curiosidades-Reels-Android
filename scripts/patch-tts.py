#!/usr/bin/env python3
from pathlib import Path

p=Path("app/src/main/java/br/com/helper/reels/NarrationEngine.java")
s=p.read_text(encoding="utf-8")
old='''        TextToSpeech tts=new TextToSpeech(context,code->{initCode.set(code);init.countDown();});
        try{
            if(!init.await(25,TimeUnit.SECONDS)||initCode.get()!=TextToSpeech.SUCCESS)
                throw new Exception("Ative o mecanismo de voz do Android nas configurações do celular.");'''
new='''        // Create the TTS engine on the main looper; synthesize from the worker thread.
        AtomicReference<TextToSpeech> engine=new AtomicReference<>();
        CountDownLatch constructed=new CountDownLatch(1);
        new android.os.Handler(android.os.Looper.getMainLooper()).post(()->{
            try{
                engine.set(new TextToSpeech(context.getApplicationContext(),code->{
                    initCode.set(code);init.countDown();
                }));
            }catch(Exception e){
                failure.set("Falha ao iniciar serviço de voz: "+e.getMessage());
                init.countDown();
            }finally{constructed.countDown();}
        });
        if(!constructed.await(60,TimeUnit.SECONDS))
            throw new Exception("O Android não conseguiu abrir o serviço de voz.");
        TextToSpeech tts=engine.get();
        if(tts==null)throw new Exception("Serviço de voz não instalado: "+failure.get());
        try{
            if(!init.await(110,TimeUnit.SECONDS))
                throw new Exception("Tempo limite ao iniciar a voz do Android. Tente novamente ou instale Speech Services by Google.");
            if(initCode.get()!=TextToSpeech.SUCCESS)
                throw new Exception("O mecanismo de voz retornou falha "+initCode.get()+". Confira as vozes pt-BR instaladas.");'''
assert old in s, "TTS original not found"
s=s.replace(old,new)
s=s.replace('if(!done.await(110,TimeUnit.SECONDS))', 'if(!done.await(190,TimeUnit.SECONDS))')
p.write_text(s,encoding="utf-8")

p=Path("app/src/main/java/br/com/helper/reels/MainActivity.java")
s=p.read_text(encoding="utf-8")
old='''                getContentResolver().update(uri,ok,null,null);
                Uri result=uri;'''
new='''                getContentResolver().update(uri,ok,null,null);
                android.util.Log.i("HelperReels","MP4GERADO com sucesso: "+uri);
                Uri result=uri;'''
assert old in s,"MainActivity insertion not found"
s=s.replace(old,new)
p.write_text(s,encoding="utf-8")
print("Patches de voz Android e diagnóstico aplicados")
