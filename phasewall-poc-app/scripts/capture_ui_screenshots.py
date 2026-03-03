#!/usr/bin/env python3
from __future__ import annotations

import argparse
import subprocess
import sys
import time
from pathlib import Path
from urllib.error import URLError
from urllib.request import urlopen

from playwright.sync_api import TimeoutError as PlaywrightTimeoutError
from playwright.sync_api import sync_playwright


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Capture PhaseWall Streamlit UI screenshots.")
    parser.add_argument("--url", default="http://localhost:8501", help="Streamlit app URL.")
    parser.add_argument(
        "--out",
        default="docs/screenshots",
        help="Output directory for PNG screenshots.",
    )
    parser.add_argument(
        "--headless",
        default="true",
        choices=["true", "false"],
        help="Run browser headless.",
    )
    parser.add_argument(
        "--timeout-seconds",
        type=int,
        default=300,
        help="Maximum wait for long operations (e.g., benchmark run).",
    )
    parser.add_argument(
        "--start-streamlit",
        action="store_true",
        help="Start `streamlit run app.py` automatically and stop it at the end.",
    )
    return parser.parse_args()


def wait_for_http(url: str, timeout_seconds: int) -> None:
    deadline = time.time() + timeout_seconds
    while time.time() < deadline:
        try:
            with urlopen(url) as response:
                if response.status == 200:
                    return
        except URLError:
            pass
        time.sleep(0.5)
    raise TimeoutError(f"Timed out waiting for {url}")


def scroll_to_y(page, y: int) -> None:
    page.evaluate(f"window.scrollTo(0, {y})")
    page.wait_for_timeout(700)


def save_full_page(page, out_dir: Path, filename: str) -> None:
    out_path = out_dir / filename
    page.screenshot(path=str(out_path), full_page=True)
    print(f"[saved] {out_path}")


def main() -> int:
    args = parse_args()
    out_dir = Path(args.out)
    out_dir.mkdir(parents=True, exist_ok=True)

    streamlit_proc: subprocess.Popen | None = None
    if args.start_streamlit:
        streamlit_proc = subprocess.Popen(
            [sys.executable, "-m", "streamlit", "run", "app.py", "--server.headless=true"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        wait_for_http(args.url, timeout_seconds=60)

    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=args.headless == "true")
            context = browser.new_context(viewport={"width": 1600, "height": 1200})
            page = context.new_page()
            page.set_default_timeout(60_000)
            page.goto(args.url, wait_until="domcontentloaded")
            page.get_by_text("PhaseWall PoC: Gaussian 1σ Phase-Wall").wait_for()
            page.wait_for_timeout(2_000)

            save_full_page(page, out_dir, "01-shell.png")

            page.get_by_role("tab", name="Surface").click()
            page.get_by_role("slider", name="σ").wait_for()
            page.wait_for_timeout(2_000)
            save_full_page(page, out_dir, "02-surface-default.png")

            sigma_slider = page.get_by_role("slider", name="σ")
            sigma_slider.focus()
            page.keyboard.press("ArrowRight")
            page.keyboard.press("ArrowRight")
            page.wait_for_timeout(1_500)
            save_full_page(page, out_dir, "03-surface-adjusted.png")

            page.get_by_role("tab", name="Walker Arena").click()
            page.get_by_role("slider", name="Walkers").wait_for()
            page.wait_for_timeout(3_000)
            scroll_to_y(page, 0)
            save_full_page(page, out_dir, "04-walkers-baseline.png")

            scroll_to_y(page, 600)
            save_full_page(page, out_dir, "05-walkers-results.png")

            scroll_to_y(page, 1300)
            save_full_page(page, out_dir, "06-walkers-metrics.png")

            page.get_by_role("tab", name="Optimizer Arena").click()
            page.get_by_role("combobox", name="Engine").wait_for()
            page.wait_for_timeout(3_000)
            scroll_to_y(page, 0)
            save_full_page(page, out_dir, "07-optimizer-baseline.png")

            scroll_to_y(page, 600)
            save_full_page(page, out_dir, "08-optimizer-curve.png")

            scroll_to_y(page, 1200)
            save_full_page(page, out_dir, "09-optimizer-metrics.png")

            page.get_by_role("tab", name="Evidence Report").click()
            page.get_by_role("spinbutton", name="Seeds").wait_for()
            page.wait_for_timeout(1_500)
            scroll_to_y(page, 0)
            save_full_page(page, out_dir, "10-evidence-prerun.png")

            page.get_by_role("button", name="Run benchmark and export artifacts").click()
            try:
                page.get_by_text("Artifacts written to:").wait_for(timeout=args.timeout_seconds * 1000)
            except PlaywrightTimeoutError as exc:
                raise TimeoutError("Evidence benchmark run did not finish in time.") from exc
            page.wait_for_timeout(1_500)
            save_full_page(page, out_dir, "11-evidence-postrun.png")

            context.close()
            browser.close()
    finally:
        if streamlit_proc is not None and streamlit_proc.poll() is None:
            streamlit_proc.terminate()
            streamlit_proc.wait(timeout=10)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
