#!/usr/bin/env python3
"""
build_covers.py — resolve cover art for the critical discography, at build time.

Why build time: MusicBrainz asks for one request per second and a real
User-Agent, neither of which a browser can honour. Resolving once during the
build and committing the result means the published site makes zero calls to
MusicBrainz, and (with --download) zero calls to the Cover Art Archive either.

Usage
    python build_covers.py recordings.json --contact you@example.org
    python build_covers.py recordings.json --contact you@example.org --download

Input  : JSON list of recordings, each with at least
         {"id", "work", "artist_hint", "label", "year", "mbid": optional}
Output : covers.json   — id -> {mbid, image, source, checked}
         img/<id>.jpg  — only with --download
Cache  : .cache/covers_cache.json — nothing already known is fetched again
"""

from __future__ import annotations

import argparse
import json
import pathlib
import sys
import time
import urllib.parse
import urllib.request
from datetime import datetime, timedelta, timezone

MB_ROOT = "https://musicbrainz.org/ws/2"
CAA_ROOT = "https://coverartarchive.org"

# Re-check a hit rarely; re-check a miss more often, since the archive grows.
TTL_HIT = timedelta(days=90)
TTL_MISS = timedelta(days=14)

CACHE_PATH = pathlib.Path(".cache/covers_cache.json")
MIN_INTERVAL = 1.05          # MusicBrainz: one request per second, be polite
_last_call = 0.0


def now() -> datetime:
    return datetime.now(timezone.utc)


def throttle() -> None:
    global _last_call
    wait = MIN_INTERVAL - (time.monotonic() - _last_call)
    if wait > 0:
        time.sleep(wait)
    _last_call = time.monotonic()


def get(url: str, ua: str, *, head: bool = False) -> tuple[int, bytes, str]:
    """Return (status, body, final_url). Never raises on 4xx."""
    throttle()
    req = urllib.request.Request(url, method="HEAD" if head else "GET")
    req.add_header("User-Agent", ua)
    req.add_header("Accept", "application/json")
    try:
        with urllib.request.urlopen(req, timeout=20) as resp:
            return resp.status, (b"" if head else resp.read()), resp.geturl()
    except urllib.error.HTTPError as err:
        return err.code, b"", url
    except Exception as err:                      # network down, DNS, timeout
        print(f"    ! {type(err).__name__}: {err}", file=sys.stderr)
        return 0, b"", url


def load_cache() -> dict:
    if CACHE_PATH.exists():
        return json.loads(CACHE_PATH.read_text("utf-8"))
    return {}


def save_cache(cache: dict) -> None:
    CACHE_PATH.parent.mkdir(parents=True, exist_ok=True)
    CACHE_PATH.write_text(json.dumps(cache, indent=2, ensure_ascii=False), "utf-8")


def fresh(entry: dict) -> bool:
    checked = datetime.fromisoformat(entry["checked"])
    ttl = TTL_HIT if entry.get("image") else TTL_MISS
    return now() - checked < ttl


def find_release(rec: dict, ua: str) -> str | None:
    """Search MusicBrainz for the release most likely to be this recording."""
    terms = f'{rec["work"]} AND artist:"{rec["artist_hint"]}"'
    if rec.get("label"):
        terms += f' AND label:"{rec["label"]}"'
    query = urllib.parse.urlencode({"query": terms, "fmt": "json", "limit": 5})
    status, body, _ = get(f"{MB_ROOT}/release/?{query}", ua)
    if status != 200 or not body:
        return None

    results = json.loads(body).get("releases", [])
    if not results:
        return None

    # Prefer a release whose date is near the recording year; the search score
    # alone happily returns a 2016 budget reissue for a 1953 set.
    want = str(rec.get("year", ""))[:4]

    def rank(rel: dict) -> tuple[int, int]:
        date = (rel.get("date") or "")[:4]
        near = abs(int(date) - int(want)) if date.isdigit() and want.isdigit() else 999
        return (near, -rel.get("score", 0))

    return sorted(results, key=rank)[0]["id"]


def front_cover(mbid: str, ua: str) -> str | None:
    """The Cover Art Archive redirects to the real file; 404 means none yet."""
    url = f"{CAA_ROOT}/release/{mbid}/front-500"
    status, _, final = get(url, ua, head=True)
    return final if status == 200 else None


def download(url: str, dest: pathlib.Path, ua: str) -> bool:
    status, body, _ = get(url, ua)
    if status != 200 or not body:
        return False
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_bytes(body)
    return True


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("recordings", type=pathlib.Path)
    ap.add_argument("--contact", required=True,
                    help="contact address for the User-Agent MusicBrainz requires")
    ap.add_argument("--out", type=pathlib.Path, default=pathlib.Path("covers.json"))
    ap.add_argument("--download", action="store_true",
                    help="save images into img/ and serve them from the site")
    ap.add_argument("--refresh", action="store_true", help="ignore the cache")
    args = ap.parse_args()

    ua = f"CriticalDiscography/1.0 ({args.contact})"
    records = json.loads(args.recordings.read_text("utf-8"))
    cache = {} if args.refresh else load_cache()
    out, calls = {}, 0

    for rec in records:
        key = rec["id"]
        cached = cache.get(key)
        if cached and fresh(cached):
            out[key] = cached
            print(f"  cached  {key}")
            continue

        print(f"  resolve {key}")
        mbid = rec.get("mbid") or (cached or {}).get("mbid") or find_release(rec, ua)
        calls += 1
        image = front_cover(mbid, ua) if mbid else None
        calls += 1 if mbid else 0

        if image and args.download:
            local = pathlib.Path("img") / f"{key}.jpg"
            if download(image, local, ua):
                image = str(local)
                calls += 1

        entry = {"mbid": mbid, "image": image,
                 "source": "Cover Art Archive" if image else None,
                 "checked": now().isoformat()}
        cache[key] = out[key] = entry
        print(f"          {mbid or 'no release matched'} -> {image or 'no front cover'}")

    save_cache(cache)
    args.out.write_text(json.dumps(out, indent=2, ensure_ascii=False), "utf-8")

    have = sum(1 for e in out.values() if e["image"])
    print(f"\n{have}/{len(out)} covers · {calls} network calls this run · wrote {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
