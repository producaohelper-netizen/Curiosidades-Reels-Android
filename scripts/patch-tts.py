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
# Some on-device TTS engines write a complete WAV but omit onAudioAvailable callbacks.
# Use the actual WAV samples as a standards-compliant fallback; never synthesize fake narration.
s=s.replace(
    'if(bytes.length<5000)throw new Exception("A voz não produziu áudio. Atualize a voz do sistema.");',
    """if(bytes.length<5000 && wav.length()>48){
                    byte[] raw=java.nio.file.Files.readAllBytes(wav.toPath());
                    if(raw.length>48 && raw[0]=='R' && raw[1]=='I' && raw[2]=='F' && raw[3]=='F'
                       && raw[8]=='W' && raw[9]=='A' && raw[10]=='V' && raw[11]=='E'){
                        java.nio.ByteBuffer bb=java.nio.ByteBuffer.wrap(raw).order(java.nio.ByteOrder.LITTLE_ENDIAN);
                        int offset=12, fmt=0, bits=0, nch=0, hz=0, dataPos=0, dataLen=0;
                        while(offset+8<=raw.length){
                            int tag=bb.getInt(offset), len=bb.getInt(offset+4);
                            if(len<0||offset+8L+len>raw.length)break;
                            if(tag==0x20746d66 && len>=16){
                                fmt=bb.getShort(offset+8)&65535;
                                nch=bb.getShort(offset+10)&65535;
                                hz=bb.getInt(offset+12);
                                bits=bb.getShort(offset+22)&65535;
                            }else if(tag==0x61746164){
                                dataPos=offset+8;dataLen=len;
                            }
                            offset+=8+len+(len&1);
                        }
                        if(fmt==1 && bits==16 && nch>0 && nch<=2 && hz>=8000 && dataLen>=5000){
                            bytes=java.util.Arrays.copyOfRange(raw,dataPos,dataPos+dataLen);
                            channels.set(nch);rate.set(hz);
                            encoding.set(AudioFormat.ENCODING_PCM_16BIT);
                        }
                    }
                }
                if(bytes.length<5000)throw new Exception("A voz não produziu áudio. Atualize a voz do sistema.");"""
)
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
