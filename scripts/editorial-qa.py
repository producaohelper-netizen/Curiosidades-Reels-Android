#!/usr/bin/env python3
"""Release gate: validate actual MP4, source attribution and publication assets."""
import json, subprocess, sys
from pathlib import Path
base=Path("produced")
meta=json.loads((base/"latest.json").read_text(encoding="utf-8"))
post=json.loads((base/"instagram-post.json").read_text(encoding="utf-8"))
probe=json.loads(subprocess.check_output(["ffprobe","-v","error","-show_entries","format=duration","-show_entries","stream=codec_type,codec_name,width,height","-of","json",str(base/"latest.mp4")],text=True))
streams=probe.get("streams",[])
duration=float(probe["format"]["duration"])
checks={
 "MP4 9:16 720x1280":any(s.get("codec_type")=="video" and s.get("width")==720 and s.get("height")==1280 for s in streams),
 "H264":any(s.get("codec_name")=="h264" for s in streams),
 "AAC":any(s.get("codec_name")=="aac" for s in streams),
 "duration 15-35s":15<=duration<=35,
 "metadata duration matches video":abs(duration-float(meta["duration_s"]))<1,
 "fact sources present":len(meta.get("fact_sources",[]))>=1,
 "caption includes account": "@curiosidades.infinitas.nv" in post.get("caption",""),
 "caption and title present":bool(post.get("caption") and post.get("cover_title")),
 "non-generic opening":not post.get("caption","").strip().lower().startswith(("você sabia?","voce sabia?","sabia disso?")),
 "no spelling mistake": "sabiá disso" not in post.get("caption","").lower(),
 "sources internal only": not any(x in post.get("caption","").lower() for x in ("mit news","universidade de rochester","fontes:")),
 "relevant action request":any(x in post.get("caption","").lower() for x in ("envie","salve","comente","comentários")),
 "focused hashtags": 2<=len(post.get("hashtags",[]))<=6,
}
result={"checks":checks,"duration_s":duration,"approved":all(checks.values()),"note":"Automated checks do not replace human review of accuracy, imagery, licensing or natural narration."}
(base/"editorial-qa.json").write_text(json.dumps(result,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
for k,v in checks.items():print(("PASS" if v else "FAIL"),k)
if not result["approved"]:
 print("NOT APPROVED: reel does not meet release requirements",file=sys.stderr)
 sys.exit(1)
