#!/usr/bin/env python3
from pathlib import Path
p=Path("app/src/main/java/br/com/helper/reels/ReelRenderer.java")
s=p.read_text(encoding="utf-8")
i=s.index("    public void draw(Canvas c,double time,double duration){")
j=s.index("    private void ambient(Canvas c,float t,int accent,int scene){",i)
new_draw="""    /** Export only the topic and storytelling: no brand, badge, scene counter or production metadata. */
    public void draw(Canvas c,double time,double duration){
        float t=(float)time;
        int stage=Math.min(4,Math.max(0,(int)(time/Math.max(1,duration)*5)));
        int accent=accents[stage];
        color(0xFF101225);
        p.setShader(new LinearGradient(0,0,w,h,
                stage%2==0?0xFF081528:0xFF19112E,
                stage%2==0?0xFF251341:0xFF0C2A32,Shader.TileMode.CLAMP));
        c.drawRect(0,0,w,h,p);p.setShader(null);
        if(photo!=null){
            color(0xAAFFFFFF);p.setAlpha(90);
            float fit=Math.max(w/(float)photo.getWidth(),h/(float)photo.getHeight());
            float zoom=fit*(1.12f+0.03f*(float)Math.sin(t*0.18));
            float dw=photo.getWidth()*zoom,dh=photo.getHeight()*zoom;
            float dx=v(16)*(float)Math.sin(t*.22f);
            c.drawBitmap(photo,null,new RectF((w-dw)/2+dx,(h-dh)/2,(w+dw)/2+dx,(h+dh)/2),p);
            color(0xBC071023);c.drawRect(0,0,w,h,p);
        }
        ambient(c,t,accent,stage);
        // Upper third contains the title OF THE TOPIC, not the producer's name.
        List<String> headline=wrap(story.title,884,66);
        float font=headline.size()>2?57:66;
        float start=headline.size()>2?272:312;
        for(int i=0;i<Math.min(3,headline.size());i++){
            text(c,headline.get(i),540,start+i*(font+17),font,Color.WHITE,true);
        }
        drawSubject(c,t,stage,accent);
        drawKaraoke(c,time);
    }
"""
s=s[:i]+new_draw+s[j:]
# Remove on-screen production/creation metadata.
count=s.count('''        rect(c,155,1202,925,1244,20,0xAA142339);
        text(c,String.format(Locale.ROOT,"CENA %02d / 05",scene+1),540,1233,25,accent,true);
''')
assert count==1, "scene label not found"
s=s.replace('''        rect(c,155,1202,925,1244,20,0xAA142339);
        text(c,String.format(Locale.ROOT,"CENA %02d / 05",scene+1),540,1233,25,accent,true);
''','')
i=s.index("    private void drawKaraoke(Canvas c,double seconds,int accent){")
s=s[:i]+"""    /**
     * Captions never stretch horizontally. Width is measured with the very same
     * font/size used for drawing, so words cannot collide or concatenate.
     */
    private void drawKaraoke(Canvas c,double seconds){
        if(timed==null||timed.words.isEmpty())return;
        int current=timed.currentIndex(seconds);
        if(current<0)return;
        List<CaptionTimeline.Word> words=timed.words;
        final int perCard=4;
        int start=(current/perCard)*perCard;
        int end=Math.min(words.size(),start+perCard);
        int split=start+Math.min(2,end-start);
        // Subtitle-safe band above Instagram's lower controls.
        rect(c,58,1308,1022,1530,34,0xDB091122);
        renderSubtitleLine(c,words,start,split,1398,current);
        renderSubtitleLine(c,words,split,end,1481,current);
    }
    private void renderSubtitleLine(Canvas c,List<CaptionTimeline.Word> words,
                                    int from,int to,float y,int active){
        if(to<=from)return;
        final Typeface face=Typeface.create("sans-serif-black",Typeface.BOLD);
        final float space=v(18);
        float size=70;
        float total;
        while(true){
            p.reset();p.setAntiAlias(true);p.setTypeface(face);p.setTextSize(v(size));
            total=0;
            for(int i=from;i<to;i++) total+=p.measureText(words.get(i).text);
            total+=space*(to-from-1);
            if(total<=v(874)||size<=48)break;
            size-=2;
        }
        float x=(w-total)/2f;
        for(int i=from;i<to;i++){
            String token=words.get(i).text;
            p.reset();p.setAntiAlias(true);p.setTypeface(face);
            p.setTextSize(v(size));p.setTextAlign(Paint.Align.LEFT);
            float tw=p.measureText(token);
            // Dark outline guarantees visibility on moving images, without blur.
            p.setColor(0xFF091225);p.setStrokeWidth(v(7));
            p.setStrokeJoin(Paint.Join.ROUND);p.setStyle(Paint.Style.STROKE);
            c.drawText(token,x,v(y),p);
            p.setStyle(Paint.Style.FILL);
            p.setColor(i==active?0xFFFFDD83:0xFFF7FAFF);
            c.drawText(token,x,v(y),p);
            x+=tw+space;
        }
    }
}
"""
p.write_text(s,encoding="utf-8")

p=Path("app/src/main/java/br/com/helper/reels/ScriptBuilder.java")
s=p.read_text(encoding="utf-8")
old='''        String narration=HOOKS[Math.floorMod(sequence,HOOKS.length)] + " " +f.fact+ " " +
                  OUTROS[Math.floorMod(sequence+2,OUTROS.length)];'''
assert old in s, "Script text marker not found"
s=s.replace(old,'''        // The voice stays on the subject; no generic follow/like/share prompts.
        String narration=f.fact;''')
p.write_text(s,encoding="utf-8")
print("Clean topic-only frames + measured karaoke captions + subject-only narration")
