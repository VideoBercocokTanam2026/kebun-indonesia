#!/usr/bin/env python3
"""
Generator situs Bercocok Tanam Indonesia (arsitektur dynamic-fetch).

Cara pakai:
    python3 generate.py

Baca semua video dari videos.json, lalu otomatis membuat:
  - index.html                         (halaman utama, grid video)
  - bercocok-tanam-indonesia-part-N.html   (1 halaman per video)

Arsitektur baru: index.html dan tiap halaman video TIDAK lagi menanam
(baked-in) daftar video di dalam file HTML-nya. Sebagai gantinya, semua
halaman mengambil data lewat fetch('videos.json') saat dibuka di browser.

Akibatnya:
  - index.html isinya selalu sama persis setiap generate -> cukup upload
    SEKALI saja, tidak perlu diupload ulang tiap tambah video baru.
  - Halaman video yang SUDAH ADA juga tidak berubah isinya saat video baru
    ditambahkan -> tidak perlu diupload ulang.
  - Menambah video baru cukup upload: videos.json + 1 halaman video baru
    (+ cover custom kalau ada).

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


def cover_image_url(slug, drive_id):
    """Pakai cover custom kalau filenya ada di covers/ (boleh .jpg/.jpeg/.png/.webp),
    kalau tidak ada fallback ke thumbnail otomatis Google Drive."""
    for ext in ("jpg", "jpeg", "png", "webp"):
        cover_path = os.path.join(ROOT, "covers", f"{slug}.{ext}")
        if os.path.exists(cover_path):
            return f"{SITE_BASE_URL}covers/{slug}.{ext}"
    return f"https://drive.google.com/thumbnail?id={drive_id}&sz=w1200"


def build_index():
    """index.html sekarang statis (tidak ada data video ditanam di dalamnya),
    jadi cukup disalin langsung dari template - isinya akan selalu sama persis
    setiap kali digenerate, tidak perlu diupload ulang kalau sudah pernah ada
    di repo."""
    template_path = os.path.join(ROOT, "templates", "index.template.html")
    with open(template_path, "r", encoding="utf-8") as f:
        html = f.read()

    out_path = os.path.join(ROOT, "index.html")
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(html)
    print("generated index.html")


def build_video_pages(videos):
    template_path = os.path.join(ROOT, "templates", "video.template.html")
    with open(template_path, "r", encoding="utf-8") as f:
        template = f.read()

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

        out_path = os.path.join(ROOT, f"{slug}.html")
        with open(out_path, "w", encoding="utf-8") as f:
            f.write(html)
        print(f"generated {slug}.html")


def main():
    videos = load_videos()
    if not videos:
        print("videos.json kosong, tidak ada yang digenerate.", file=sys.stderr)
        return
    build_index()
    build_video_pages(videos)


if __name__ == "__main__":
    main()
