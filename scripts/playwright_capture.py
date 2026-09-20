from __future__ import annotations

import os
import shutil
import subprocess
import time
from pathlib import Path

from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]
SCREENSHOTS = ROOT / "media" / "screenshots"
DEMO_DIR = ROOT / "media" / "demo"
VIDEO_TMP = ROOT / ".playwright-video"
BASE_URL = os.environ.get("BASE_URL", "http://127.0.0.1:8012")
USERNAME = os.environ.get("DEMO_USERNAME", "demo")
PASSWORD = os.environ.get("DEMO_PASSWORD", "demo1234")

SCREENSHOTS.mkdir(parents=True, exist_ok=True)
DEMO_DIR.mkdir(parents=True, exist_ok=True)
if VIDEO_TMP.exists():
    shutil.rmtree(VIDEO_TMP)
VIDEO_TMP.mkdir(parents=True)


def shot(page, name: str, path: str, hash_fragment: str | None = None) -> None:
    suffix = f"#{hash_fragment}" if hash_fragment else ""
    url = f"{BASE_URL}{path}{suffix}"
    page.goto(url, wait_until="networkidle")
    if hash_fragment:
        page.wait_for_timeout(650)
    page.screenshot(path=str(SCREENSHOTS / f"{name}.png"), full_page=True)


def main() -> None:
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            viewport={"width": 1440, "height": 960},
            device_scale_factor=1,
            color_scheme="dark",
            record_video_dir=str(VIDEO_TMP),
            record_video_size={"width": 1440, "height": 900},
        )
        page = context.new_page()
        page.goto(f"{BASE_URL}/login", wait_until="networkidle")
        page.locator('input[name="username"]').fill(USERNAME)
        page.locator('input[name="password"]').fill(PASSWORD)
        page.get_by_role("button", name="Log in").click()
        page.wait_for_load_state("networkidle")

        # Screenshots used by README/wiki.
        shot(page, "01-today", "/dashboard")
        shot(page, "02-diary", "/diary")
        shot(page, "03-log-food", "/log")
        shot(page, "04-nutrition-missing", "/nutrition", "missing")
        shot(page, "05-planner", "/planner")
        shot(page, "06-progress", "/progress")
        shot(page, "07-foods", "/custom-food")

        # Recorded guided demo.
        page.goto(f"{BASE_URL}/dashboard", wait_until="networkidle")
        page.wait_for_timeout(900)
        for label, path in [
            ("Diary", "/diary"),
            ("Log Food", "/log"),
            ("Nutrition", "/nutrition"),
            ("Planner", "/planner"),
            ("Progress", "/progress"),
            ("Foods", "/custom-food"),
        ]:
            page.goto(f"{BASE_URL}{path}", wait_until="networkidle")
            page.wait_for_timeout(900)
            page.evaluate("window.scrollTo({top: Math.min(document.body.scrollHeight * 0.42, 760), behavior:'smooth'})")
            page.wait_for_timeout(850)
            page.evaluate("window.scrollTo({top:0, behavior:'smooth'})")
            page.wait_for_timeout(450)

        # Show the food search interaction in the recording.
        page.goto(f"{BASE_URL}/log", wait_until="networkidle")
        search = page.locator("#food-search")
        if search.count():
            search.fill("chicken breast")
            page.wait_for_timeout(1200)
            first = page.locator("#search-results button").first
            if first.count():
                first.click()
                page.wait_for_timeout(750)
                grams = page.locator("#grams")
                if grams.count():
                    grams.fill("180")
                    page.wait_for_timeout(800)

        page.goto(f"{BASE_URL}/nutrition#missing", wait_until="networkidle")
        page.wait_for_timeout(1000)
        context.close()
        browser.close()

    videos = sorted(VIDEO_TMP.glob("*.webm"), key=lambda p: p.stat().st_mtime)
    if not videos:
        raise RuntimeError("Playwright did not produce a video")
    webm = DEMO_DIR / "pot-of-mannah-demo.webm"
    shutil.copy2(videos[-1], webm)

    ffmpeg = shutil.which("ffmpeg")
    if ffmpeg:
        mp4 = DEMO_DIR / "pot-of-mannah-demo.mp4"
        subprocess.run(
            [ffmpeg, "-y", "-i", str(webm), "-vf", "scale=1280:-2", "-c:v", "libx264", "-preset", "medium", "-crf", "28", "-pix_fmt", "yuv420p", "-movflags", "+faststart", "-an", str(mp4)],
            check=True,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        print(mp4)
    print(webm)


if __name__ == "__main__":
    main()
