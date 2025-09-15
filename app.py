#!/usr/bin/env python3
import os
import io
import sys
import json
import math
import time
import argparse
import re
import textwrap
import requests
from urllib.parse import urlparse
from slugify import slugify
from typing import Any, Dict, List, Optional

from gtts import gTTS
from PIL import Image, ImageFilter
import numpy as np
from moviepy.editor import (
    AudioFileClip, CompositeVideoClip, ColorClip, ImageClip, TextClip, VideoClip
)
from dotenv import load_dotenv

load_dotenv()

W = 1080
H = 1920
FPS = 30
BITRATE = "12M"

def fetch_newsletters(api: str, user: str, pwd: str, timeout: int = 30) -> List[Dict[str, Any]]:
    headers = {"Accept": "application/json"}
    r = requests.get(api, headers=headers, auth=(user, pwd), timeout=timeout)
    r.raise_for_status()
    data = r.json()
    # try common container shapes
    if isinstance(data, dict):
        if "results" in data and isinstance(data["results"], list):
            return data["results"]
        if "items" in data and isinstance(data["items"], list):
            return data["items"]
    if isinstance(data, list):
        return data
    raise ValueError("Unexpected API payload shape")

def mock_fetch_newsletters() -> List[Dict[str, Any]]:
    # Mocked response
    return [
        {
            "title": "Sample Newsletter 1",
            "summary": "This is a summary of the first sample newsletter.",
            "image_url": "https://cdn.prod.website-files.com/63337fce7f2d6c29c4554b84/66c46c1837e9862234104910_Bravelab-DeepWork-Capital%20(1).png"
        },
        {
            "title": "Sample Newsletter 2",
            "summary": "This is a summary of the second sample newsletter.",
            "image_url": "https://uploads-ssl.webflow.com/63337fce7f2d6c29c4554b84/65ae33a5c21f4217286b06d2_Bravelab_Audiomob.png"
        }
    ]

def pick_image_url(item:Dict[str,Any]) -> Optional[str]:
    keys = ["image","image_url","thumbnail","thumbnail_url","cover","cover_url"]
    for k in keys:
        v = item.get(k)
        if isinstance(v, str) and v.startswith(("http://","https://")):
            return v
        if isinstance(v, dict):
            # try common nested "url"
            u = v.get("url") or v.get("src")
            if isinstance(u, str) and u.startswith(("http://","https://")):
                return u
    return None

def pick_title(item:Dict[str,Any]) -> str:
    for k in ["title","name","headline","subject"]:
        v = item.get(k)
        if isinstance(v, str) and v.strip():
            return v.strip()
    return "Aktualność"

def pick_summary(item:Dict[str,Any]) -> str:
    for k in ["summary","description","excerpt","lead","teaser","content","body","text"]:
        v = item.get(k)
        if isinstance(v, str) and v.strip():
            # strip html tags if any
            txt = v
            txt = re.sub(r"<br\s*/?>", "\n", txt, flags=re.I)
            txt = re.sub(r"<[^>]+>", " ", txt)
            txt = re.sub(r"\s+", " ", txt).strip()
            return txt
    return ""

def compress(text:str, max_chars:int=420) -> str:
    text = text.strip()
    if len(text) <= max_chars:
        return text
    return text[:max_chars-1] + "…"

def make_script(title:str, summary:str) -> str:
    # 60–120 słów, prosty ton
    base = f"{title}. {compress(summary, 360)}"
    words = base.split()
    if len(words) < 40:
        base += " This is a summary of the newsletter."
    return base

def gtts_to_mp3(text:str, lang:str="en", out_path:str="voice.mp3") -> float:
    tts = gTTS(text, lang=lang)
    tts.save(out_path)
    # MoviePy will read duration later; return a dummy >0
    return 1.0

def build_bg(image_url:Optional[str], duration:float):
    if image_url:
        try:
            resp = requests.get(image_url, timeout=30)
            resp.raise_for_status()
            img = Image.open(io.BytesIO(resp.content)).convert("RGB")
            ratio = max(W/img.width, H/img.height)
            img = img.resize((int(img.width*ratio), int(img.height*ratio)))
            x = (img.width - W)//2; y = (img.height - H)//2
            img = img.crop((x, y, x+W, y+H)).filter(ImageFilter.GaussianBlur(12))
            bg_path = "bg_tmp.jpg"
            img.save(bg_path, quality=92)
            return ImageClip(bg_path).set_duration(duration)
        except Exception as e:
            print(f"[warn] hero image failed: {e}", file=sys.stderr)
    return ColorClip(size=(W,H), color=(15,18,25)).set_duration(duration)

def split_subtitles(script:str, n_words:int=9) -> List[str]:
    words = script.split()
    return [" ".join(words[i:i+n_words]) for i in range(0, len(words), n_words)]

def timeline_from_chunks(chunks:List[str], total:float) -> List[tuple]:
    if not chunks:
        return []
    per = total/len(chunks)
    out = []
    for i,ch in enumerate(chunks):
        start = i*per
        end = min((i+1)*per, total)
        out.append((ch, start, end))
    return out

def progress_bar(duration:float):
    bar_w = 960
    bar_h = 10
    def make_frame(t):
        p = max(0.0, min(1.0, t/duration))
        img = Image.new("RGB", (bar_w, bar_h), (80,80,80))
        fill_w = int(p*bar_w)
        for x in range(fill_w):
            for y in range(bar_h):
                img.putpixel((x,y), (255,255,255))
        return np.array(img)
    return VideoClip(make_frame=make_frame, duration=duration).set_position(("center", 90))

def render_short(title:str, script_text:str, image_url:Optional[str], out_path:str):
    # 1) voice
    voice_mp3 = "voice_tmp.mp3"
    gtts_to_mp3(script_text, "pl", voice_mp3)
    narration = AudioFileClip(voice_mp3)
    dur = narration.duration

    # 2) bg
    bg = build_bg(image_url, dur)

    # 3) title
    title_clip = TextClip(title, fontsize=70, font="Arial-Bold",
                          method="caption", align="center", size=(1000,None),
                          color="white").set_position(("center", 120)).set_duration(min(4, dur))

    # 4) subtitles
    chunks = split_subtitles(script_text, 9)
    windows = timeline_from_chunks(chunks, dur)
    sub_clips = []
    for text, start, end in windows:
        box = ColorClip((W, 180), color=(0,0,0)).set_opacity(0.35)
        box = box.set_position(("center", H-280)).set_start(start).set_end(end)
        sub = TextClip(text, fontsize=50, font="Arial", method="caption",
                       size=(1000,None), color="white")
        sub = sub.set_position(("center", H-300)).set_start(start).set_end(end)
        sub_clips += [box, sub]

    # 5) progress
    prog = progress_bar(dur)

    final = CompositeVideoClip([bg, title_clip, prog] + sub_clips)
    final = final.set_audio(narration).set_duration(dur).resize((W,H))

    # 6) export
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    final.write_videofile(
        out_path, fps=FPS, codec="libx264", audio_codec="aac",
        bitrate=BITRATE, temp_audiofile="temp-audio.m4a", remove_temp=True
    )
    print(f"[ok] wrote {out_path}")

def main():
    ap = argparse.ArgumentParser(description="Render YT Shorts from newsletters API")
    ap.add_argument("--api", required=not os.getenv("API_URL"), help="API endpoint, e.g. https://zaiks.smartfeed.media/api/v1/newsletters/")
    ap.add_argument("--limit", type=int, default=1, help="How many items to render")
    ap.add_argument("--out", default="out", help="Output directory")
    ap.add_argument("--prefix", default="short", help="Output filename prefix")
    ap.add_argument("--dry", action="store_true", help="List items and exit")
    args = ap.parse_args()

    user = os.getenv("BASIC_USER")
    pwd = os.getenv("BASIC_PASS")

    if not user or not pwd:
        print("ERROR: set BASIC_USER and BASIC_PASS environment variables", file=sys.stderr)
        sys.exit(2)

    api_url = os.getenv("API_URL")
    if not api_url:
        print("ERROR: set API_URL environment variable", file=sys.stderr)
        sys.exit(2)
    # Temporarily use the mock function for testing
    items = fetch_newsletters(api_url, user, pwd)
    if not items:
        print("No items from API.", file=sys.stderr)
        sys.exit(1)

    print(f"[info] fetched {len(items)} items")

    for idx, item in enumerate(items[:args.limit]):
        title = pick_title(item)
        summary = pick_summary(item)
        hero = pick_image_url(item)
        script_text = make_script(title, summary)
        slug = slugify(title) or f"{idx+1}"
        out_path = os.path.join(args.out, f"{args.prefix}-{slug}.mp4")
        if args.dry:
            print(json.dumps({
                "idx": idx,
                "title": title,
                "summary_preview": summary[:140],
                "image": hero,
                "out": out_path
            }, ensure_ascii=False))
            continue
        render_short(title, script_text, hero, out_path)
        # polite pause to avoid rate limits if TTS provider changes later
        time.sleep(1)

if __name__ == "__main__":
    main()
