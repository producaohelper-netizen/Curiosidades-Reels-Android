#!/usr/bin/env python3
"""Bring completed Reels into the 15–35s Instagram target without cutting off words.
Video and audio are retimed together, preserving caption-to-voice synchronization.
Reject excessive acceleration rather than shipping unintelligible narration.
"""
import json, subprocess
from pathlib import Path
root=Path("produced")
mp4=root/"latest.mp4"
meta_file=root/"latest.json"
meta=json.loads(meta_file.read_text(encoding="utf-8"))
probe=json.loads(subprocess.check_output(["ffprobe","-v","error","-show_entries","format=duration","-of","json",str(mp4)],text=True))
duration=float(probe["format"]["duration"])
if 15<=duration<=35:
 print(f"Already within target: {duration:.2f}s")
elif 35<duration<=49:
 speed=duration/34.5
 out=root/"latest-retimed.mp4"
 subprocess.run(["ffmpeg","-hide_banner","-loglevel","error","-y","-i",str(mp4),
                 "-filter_complex",f"[0:v]setpts=PTS/{speed:.9f}[v];[0:a]atempo={speed:.9f}[a]",
                 "-map","[v]","-map","[a]","-c:v","libx264","-preset","veryfast",
                 "-crf","20","-pix_fmt","yuv420p","-c:a","aac","-b:a","160k",
                 "-movflags","+faststart",str(out)],check=True)
 out.replace(mp4)
 actual=json.loads(subprocess.check_output(["ffprobe","-v","error","-show_entries","format=duration","-of","json",str(mp4)],text=True))
 new_duration=float(actual["format"]["duration"])
 assert 15<=new_duration<=35, f"Retime failed: {new_duration}"
 meta["duration_s"]=round(new_duration,3)
 meta["retime_speed"]=round(speed,4)
 meta["retime_note"]="Video, spoken audio and burned-in captions sped up together"
 import hashlib
 meta["video_sha256"]=hashlib.sha256(mp4.read_bytes()).hexdigest()
 meta_file.write_text(json.dumps(meta,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
 print(f"Retimed {duration:.2f}s -> {new_duration:.2f}s ({speed:.3f}x)")
else:
 raise SystemExit(f"Duration {duration:.2f}s cannot safely be brought to 15-35s; revise the script instead")
