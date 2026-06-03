"""Download real catalog images from Wikimedia Commons and normalize their canvas."""

from __future__ import annotations

import json
import shutil
import subprocess
import sys
import tempfile
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SOURCE_PATH = ROOT / "tools" / "catalog_expansion.json"
VEHICLE_DIR = ROOT / "custom_addons" / "auto_base" / "static" / "src" / "img" / "vehicles"
BRAND_DIR = ROOT / "custom_addons" / "auto_base" / "static" / "src" / "img" / "brands"
ATTRIBUTION_PATH = ROOT / "docs" / "CATALOG_IMAGE_SOURCES.md"
API_URL = "https://commons.wikimedia.org/w/api.php"
USER_AGENT = "EXOCOMS-Odoo-Catalog/1.0 (catalog asset preparation)"


def safe_print(message: str) -> None:
    encoding = sys.stdout.encoding or "utf-8"
    sys.stdout.write(message.encode(encoding, errors="replace").decode(encoding) + "\n")
    sys.stdout.flush()


def open_with_retry(request: urllib.request.Request, *, timeout: int):
    for attempt in range(6):
        try:
            return urllib.request.urlopen(request, timeout=timeout)
        except urllib.error.HTTPError as exc:
            if exc.code != 429 or attempt == 5:
                raise
            delay = 5 * (attempt + 1)
            safe_print(f"Rate limited by Wikimedia, retrying in {delay}s...")
            time.sleep(delay)
    raise RuntimeError("Wikimedia request retry limit exceeded")


def request_json(url: str) -> dict:
    request = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    with open_with_retry(request, timeout=45) as response:
        return json.load(response)


def download(url: str, destination: Path) -> None:
    request = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    with open_with_retry(request, timeout=90) as response:
        destination.write_bytes(response.read())


def get_image_by_title(title: str) -> dict:
    params = {
        "action": "query",
        "titles": title,
        "prop": "imageinfo",
        "iiprop": "url",
        "iiurlwidth": 900,
        "format": "json",
    }
    url = f"{API_URL}?{urllib.parse.urlencode(params)}"
    payload = request_json(url)
    pages = list(payload.get("query", {}).get("pages", {}).values())
    if not pages or not pages[0].get("imageinfo"):
        raise RuntimeError(f"No Wikimedia Commons image found for exact title: {title}")
    return pages[0]


def search_image(query: str, pick: int, *, logo: bool, title: str | None = None) -> dict:
    if title:
        try:
            return get_image_by_title(title)
        except RuntimeError:
            safe_print(f"Exact Wikimedia title unavailable, searching instead: {title}")
    params = {
        "action": "query",
        "generator": "search",
        "gsrsearch": query,
        "gsrnamespace": 6,
        "gsrlimit": 12,
        "prop": "imageinfo",
        "iiprop": "url",
        "iiurlwidth": 1800 if not logo else 900,
        "format": "json",
    }
    url = f"{API_URL}?{urllib.parse.urlencode(params)}"
    payload = request_json(url)
    pages = list(payload.get("query", {}).get("pages", {}).values())
    pages.sort(key=lambda page: page.get("index", 9999))
    allowed = {".png", ".jpg", ".jpeg", ".webp", ".svg"} if logo else {".jpg", ".jpeg", ".webp", ".png"}
    candidates = [
        page
        for page in pages
        if Path(page["title"].replace("File:", "")).suffix.lower() in allowed
        and page.get("imageinfo")
    ]
    if logo:
        logo_candidates = [
            page
            for page in candidates
            if any(token in page["title"].lower() for token in ("logo", "wordmark", "emblem"))
        ]
        if not logo_candidates:
            raise RuntimeError(f"No reusable Wikimedia Commons logo found for: {query}")
        candidates = logo_candidates
    if not candidates:
        raise RuntimeError(f"No Wikimedia Commons image found for: {query}")
    if pick >= len(candidates):
        raise RuntimeError(f"Pick {pick} is out of range for {query}; found {len(candidates)} images")
    return candidates[pick]


def normalize_image(source: Path, destination: Path, *, logo: bool) -> None:
    if not shutil.which("ffmpeg"):
        raise RuntimeError("ffmpeg is required to normalize catalog images")

    destination.parent.mkdir(parents=True, exist_ok=True)
    if logo:
        video_filter = (
            "scale=520:160:force_original_aspect_ratio=decrease,"
            "pad=iw+20:ih+20:10:10:color=white"
        )
    else:
        # The extra margin keeps the whole vehicle visible in responsive cards.
        video_filter = (
            "scale=1600:900:force_original_aspect_ratio=decrease,"
            "pad=1800:1125:(ow-iw)/2:(oh-ih)/2:color=0xf4f6f8,"
            "format=yuvj444p"
        )
    command = [
        "ffmpeg",
        "-hide_banner",
        "-loglevel",
        "error",
        "-y",
        "-i",
        str(source),
        "-vf",
        video_filter,
        "-frames:v",
        "1",
        str(destination),
    ]
    subprocess.run(command, check=True)


def generate_wordmark(destination: Path, text: str) -> None:
    destination.parent.mkdir(parents=True, exist_ok=True)
    escaped_text = (
        text.replace("\\", r"\\")
        .replace(":", r"\:")
        .replace("'", r"\'")
        .replace("%", r"\%")
    )
    video_filter = (
        "drawtext="
        f"text='{escaped_text}':"
        "fontcolor=0x15243b:fontsize=72:"
        "x=(w-text_w)/2:y=(h-text_h)/2"
    )
    command = [
        "ffmpeg",
        "-hide_banner",
        "-loglevel",
        "error",
        "-y",
        "-f",
        "lavfi",
        "-i",
        "color=c=white:s=520x120",
        "-vf",
        video_filter,
        "-frames:v",
        "1",
        str(destination),
    ]
    subprocess.run(command, check=True)


def image_info(page: dict) -> tuple[str, str, str]:
    info = page["imageinfo"][0]
    source_url = info.get("descriptionurl") or info.get("url")
    download_url = info.get("thumburl") or info.get("url")
    return page["title"], source_url, download_url


def process_asset(
    *,
    filename: str,
    query: str,
    pick: int,
    destination_dir: Path,
    logo: bool,
    temporary_dir: Path,
    title: str | None = None,
    fallback_text: str | None = None,
    fallback_source: str | None = None,
) -> dict:
    try:
        page = search_image(query, pick, logo=logo, title=title)
    except RuntimeError:
        if not logo or not fallback_text:
            raise
        generate_wordmark(destination_dir / filename, fallback_text)
        safe_print(f"{filename}: generated wordmark fallback")
        return {
            "file": filename,
            "query": query,
            "title": f"{fallback_text} wordmark fallback",
            "source_url": fallback_source or "",
        }
    title, source_url, download_url = image_info(page)
    suffix = Path(urllib.parse.urlparse(download_url).path).suffix or ".img"
    temporary_file = temporary_dir / f"{Path(filename).stem}{suffix}"
    destination = destination_dir / filename
    if not destination.exists():
        download(download_url, temporary_file)
        normalize_image(temporary_file, destination, logo=logo)
    safe_print(f"{filename}: {title}")
    return {
        "file": filename,
        "query": query,
        "title": title,
        "source_url": source_url,
    }


def write_attributions(records: list[dict]) -> None:
    lines = [
        "# Sources des images du catalogue",
        "",
        (
            "Photos et logos réels téléchargés depuis Wikimedia Commons. "
            "Consulter chaque page source pour les auteurs et licences applicables."
        ),
        "",
        "| Fichier local | Recherche | Source Wikimedia Commons |",
        "| --- | --- | --- |",
    ]
    for record in records:
        lines.append(
            f'| `{record["file"]}` | {record["query"]} | '
            f'[{record["title"]}]({record["source_url"]}) |'
        )
    ATTRIBUTION_PATH.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    data = json.loads(SOURCE_PATH.read_text(encoding="utf-8"))
    VEHICLE_DIR.mkdir(parents=True, exist_ok=True)
    BRAND_DIR.mkdir(parents=True, exist_ok=True)
    records: list[dict] = []

    with tempfile.TemporaryDirectory(prefix="exocoms_catalog_") as tmp:
        temporary_dir = Path(tmp)
        for brand in data["brands"]:
            records.append(
                process_asset(
                    filename=brand["image"],
                    query=brand["image_query"],
                    pick=brand.get("image_pick", 0),
                    destination_dir=BRAND_DIR,
                    logo=True,
                    temporary_dir=temporary_dir,
                    title=brand.get("image_title"),
                    fallback_text=brand["name"],
                    fallback_source=brand["source"],
                )
            )
            time.sleep(1.0)

        for image in data["vehicle_images"]:
            records.append(
                process_asset(
                    filename=image["file"],
                    query=image["query"],
                    pick=image.get("pick", 0),
                    destination_dir=VEHICLE_DIR,
                    logo=False,
                    temporary_dir=temporary_dir,
                    title=image.get("image_title"),
                )
            )
            time.sleep(1.0)

    write_attributions(records)
    safe_print(f"Generated {ATTRIBUTION_PATH.relative_to(ROOT)}")
    safe_print(f"Assets documented: {len(records)}")


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        safe_print(f"ERROR: {exc}")
        raise
