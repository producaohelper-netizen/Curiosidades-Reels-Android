#!/usr/bin/env python3
from pathlib import Path
p=Path("app/src/main/java/br/com/helper/reels/MainActivity.java")
s=p.read_text(encoding="utf-8")
old='''        final int width=fullHd.isChecked()?1080:(testMode?540:720);'''
new='''        final int width=fullHd.isChecked()?1080:(testMode?288:720);'''
assert old in s, "test width marker missing"
s=s.replace(old,new)
old='''                NarrationEngine.PcmAudio voice=NarrationEngine.synthesize(getApplicationContext(),story.narration);'''
new='''                NarrationEngine.PcmAudio voice;
                if(testMode && android.os.BuildConfig.DEBUG){ // isolated codec smoke test, not a user voice
                    final int hz=24000, n=hz*6;
                    byte[] samples=new byte[n*2];
                    for(int i=0;i<n;i++){
                        double t=i/(double)hz;
                        double window=Math.min(1.0,t/0.18)*Math.min(1.0,(6-t)/0.18);
                        int v=(int)(window*5000*(Math.sin(2*Math.PI*440*t)+0.55*Math.sin(2*Math.PI*660*t)));
                        samples[i*2]=(byte)(v & 255);
                        samples[i*2+1]=(byte)((v>>8)&255);
                    }
                    voice=new NarrationEngine.PcmAudio(samples,hz,1,
                        CaptionTimeline.build(story.narration,java.util.Collections.emptyList(),hz,6));
                    android.util.Log.i("HelperReels","CI codec smoke: audio de teste não é narração TTS");
                } else {
                    voice=NarrationEngine.synthesize(getApplicationContext(),story.narration);
                }'''
assert old in s,"voice marker missing"
s=s.replace(old,new)
# This is a debug test only, production always uses TTS.
p.write_text(s,encoding="utf-8")
print("TEST_GENERATION codec smoke ativado")
