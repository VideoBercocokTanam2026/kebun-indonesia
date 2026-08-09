#!/usr/bin/env python3
"""
Generator situs Video Bercocok Tanam.

Cara pakai:
    python3 generate.py

Baca semua video dari videos.json, lalu otomatis membuat:
  - index.html                         (halaman utama, grid video)
  - bercocok-tanam-part-N.html         (1 halaman per video)

Tidak perlu diedit manual — cukup edit videos.json (dan taruh gambar
cover di folder covers/ kalau mau og:image custom), lalu jalankan file
ini (atau biarkan GitHub Actions yang menjalankannya otomatis).
"""

import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.abspath(__file__))
SITE_BASE_URL = "https://videobercocoktanam2026.github.io/kebun-indonesia/"
DEFAULT_DESC = "Kumpulan video bercocok tanam ala Indonesia, dari bibit sampai panen."


def slugify(text):
    text = text.lower().strip()
    text = re.sub(r"[^a-z0-9]+", "-", text)
    return text.strip("-")


def load_videos():
    with open(os.path.join(ROOT, "videos.json"), "r", encoding="utf-8") as f:
        return json.load(f)


def js_videos_array(videos):
    """Ubah daftar video jadi teks array JavaScript untuk ditempel ke HTML."""
    items = []
    for v in videos:
        drive_link = f"https://drive.google.com/file/d/{v['driveId']}/view"
        items.append(
            "    {\n"
            f"      judul: {json.dumps(v['judul'], ensure_ascii=False)},\n"
            f"      deskripsi: {json.dumps(v.get('deskripsi', ''), ensure_ascii=False)},\n"
            f"      driveLink: {json.dumps(drive_link)},\n"
            f"      tanggal: {json.dumps(v['tanggal'], ensure_ascii=False)}\n"
            "    }"
        )
    return "const VIDEOS = [\n" + ",\n".join(items) + "\n  ];\n"


def cover_image_url(slug, drive_id):
    """Pakai cover custom kalau filenya ada di covers/ (boleh .jpg/.jpeg/.png/.webp),
    kalau tidak ada fallback ke thumbnail otomatis Google Drive."""
    for ext in ("jpg", "jpeg", "png", "webp"):
        cover_path = os.path.join(ROOT, "covers", f"{slug}.{ext}")
        if os.path.exists(cover_path):
            return f"{SITE_BASE_URL}covers/{slug}.{ext}"
    return f"https://drive.google.com/thumbnail?id={drive_id}&sz=w1200"


def build_index(videos):
    template_path = os.path.join(ROOT, "templates", "index.template.html")
    with open(template_path, "r", encoding="utf-8") as f:
        html = f.read()

    marker = re.compile(r"const VIDEOS = /\*__VIDEOS_JSON__\*/\[\];\n")
    html = marker.sub(js_videos_array(videos), html, count=1)

    out_path = os.path.join(ROOT, "index.html")
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(html)
    print("generated index.html")


def build_video_pages(videos):
    template_path = os.path.join(ROOT, "templates", "video.template.html")
    with open(template_path, "r", encoding="utf-8") as f:
        template = f.read()

    marker = re.compile(r"const VIDEOS = /\*__VIDEOS_JSON__\*/\[\];\n")
    videos_js = js_videos_array(videos)

    for v in videos:
        slug = slugify(v["judul"])
        drive_id = v["driveId"]
        og_image = cover_image_url(slug, drive_id)

        html = template
        html = html.replace("__PAGE_TITLE__", v["judul"])
        html = html.replace("__OG_TITLE__", v["judul"])
        html = html.replace("__OG_DESC__", v.get("deskripsi") or DEFAULT_DESC)
        html = html.replace("__OG_URL__", f"{SITE_BASE_URL}{slug}.html")
        html = html.replace("__OG_IMAGE__", og_image)
        html = html.replace("__VIDEO_ID__", drive_id)
        html = marker.sub(videos_js, html, count=1)

        out_path = os.path.join(ROOT, f"{slug}.html")
        with open(out_path, "w", encoding="utf-8") as f:
            f.write(html)
        print(f"generated {slug}.html")


def main():
    videos = load_videos()
    if not videos:
        print("videos.json kosong, tidak ada yang digenerate.", file=sys.stderr)
        return
    build_index(videos)
    build_video_pages(videos)


if __name__ == "__main__":
    main()
