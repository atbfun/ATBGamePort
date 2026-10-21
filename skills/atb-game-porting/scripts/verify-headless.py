#!/usr/bin/env python3
"""
Automated Headless Browser Verification for ATB Game Porting.

Starts a local ThreadingHTTPServer, launches headless Chrome/Chromium to capture
screenshots (screen_initial.png, screen_gameplay.png, screen_stage2.png), and
verifies that each screenshot meets the minimum non-black/colored pixel ratio
(default >= 90%) to enforce the Zero-Black-Screen Iron Rule.
"""

from __future__ import annotations

import argparse
import contextlib
import functools
import http.server
import os
import shutil
import socket
import struct
import subprocess
import sys
import tempfile
import threading
import time
import zlib
from pathlib import Path
from typing import Iterator, Optional, Tuple


CHROME_CANDIDATES = [
    "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
    "/Applications/Chromium.app/Contents/MacOS/Chromium",
    "/Applications/Brave Browser.app/Contents/MacOS/Brave Browser",
    "/Applications/Microsoft Edge.app/Contents/MacOS/Microsoft Edge",
    "google-chrome",
    "google-chrome-stable",
    "chromium",
    "chromium-browser",
    "msedge",
]


class QuietHTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
    def log_message(self, format: str, *args: object) -> None:
        pass


def find_chrome_binary(explicit_path: Optional[str] = None) -> Optional[str]:
    if explicit_path:
        if os.path.isfile(explicit_path) and os.access(explicit_path, os.X_OK):
            return explicit_path
        resolved = shutil.which(explicit_path)
        if resolved:
            return resolved
        return None

    env_chrome = os.environ.get("CHROME_BIN")
    if env_chrome:
        resolved = find_chrome_binary(env_chrome)
        if resolved:
            return resolved

    for candidate in CHROME_CANDIDATES:
        if os.path.isfile(candidate) and os.access(candidate, os.X_OK):
            return candidate
        resolved = shutil.which(candidate)
        if resolved:
            return resolved
    return None


@contextlib.contextmanager
def serve_directory(root_dir: Path) -> Iterator[int]:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(("127.0.0.1", 0))
        port = s.getsockname()[1]

    handler = functools.partial(QuietHTTPRequestHandler, directory=str(root_dir))
    httpd = http.server.ThreadingHTTPServer(("127.0.0.1", port), handler)
    thread = threading.Thread(target=httpd.serve_forever, daemon=True)
    thread.start()
    try:
        yield port
    finally:
        httpd.shutdown()
        httpd.server_close()


def _paeth_predictor(a: int, b: int, c: int) -> int:
    p = a + b - c
    pa = abs(p - a)
    pb = abs(p - b)
    pc = abs(p - c)
    if pa <= pb and pa <= pc:
        return a
    if pb <= pc:
        return b
    return c


def compute_png_colored_ratio(png_path: Path, luma_threshold: int = 12) -> float:
    """
    Pure-Python PNG reader that computes the ratio of non-black pixels
    (R > threshold or G > threshold or B > threshold) without requiring Pillow.
    Supports 8-bit RGB (color_type=2) and RGBA (color_type=6) PNGs emitted by Chrome.
    """
    data = png_path.read_bytes()
    if data[:8] != b"\x89PNG\r\n\x1a\n":
        raise ValueError(f"{png_path} is not a valid PNG file")

    pos = 8
    width = height = bit_depth = color_type = 0
    idat_chunks = []

    while pos < len(data):
        length = struct.unpack(">I", data[pos : pos + 4])[0]
        chunk_type = data[pos + 4 : pos + 8]
        chunk_data = data[pos + 8 : pos + 8 + length]
        pos += 12 + length

        if chunk_type == b"IHDR":
            width, height, bit_depth, color_type, _, _, _ = struct.unpack(">IIBBBBB", chunk_data)
        elif chunk_type == b"IDAT":
            idat_chunks.append(chunk_data)
        elif chunk_type == b"IEND":
            break

    if width == 0 or height == 0:
        raise ValueError(f"Invalid PNG dimensions in {png_path}")
    if bit_depth != 8 or color_type not in (2, 6):
        raise ValueError(f"Unsupported PNG format (bit_depth={bit_depth}, color_type={color_type})")

    bpp = 3 if color_type == 2 else 4
    stride = width * bpp
    raw = zlib.decompress(b"".join(idat_chunks))

    prev_row = bytearray(stride)
    cur_row = bytearray(stride)
    colored_pixels = 0
    total_pixels = width * height
    offset = 0

    for _ in range(height):
        filter_type = raw[offset]
        offset += 1
        row_bytes = raw[offset : offset + stride]
        offset += stride

        if filter_type == 0:  # None
            cur_row[:] = row_bytes
        elif filter_type == 1:  # Sub
            for i in range(stride):
                left = cur_row[i - bpp] if i >= bpp else 0
                cur_row[i] = (row_bytes[i] + left) & 0xFF
        elif filter_type == 2:  # Up
            for i in range(stride):
                cur_row[i] = (row_bytes[i] + prev_row[i]) & 0xFF
        elif filter_type == 3:  # Average
            for i in range(stride):
                left = cur_row[i - bpp] if i >= bpp else 0
                up = prev_row[i]
                cur_row[i] = (row_bytes[i] + ((left + up) >> 1)) & 0xFF
        elif filter_type == 4:  # Paeth
            for i in range(stride):
                left = cur_row[i - bpp] if i >= bpp else 0
                up = prev_row[i]
                up_left = prev_row[i - bpp] if i >= bpp else 0
                cur_row[i] = (row_bytes[i] + _paeth_predictor(left, up, up_left)) & 0xFF
        else:
            raise ValueError(f"Unsupported PNG filter type: {filter_type}")

        for px in range(0, stride, bpp):
            r, g, b = cur_row[px], cur_row[px + 1], cur_row[px + 2]
            if r > luma_threshold or g > luma_threshold or b > luma_threshold:
                colored_pixels += 1

        prev_row[:] = cur_row

    return colored_pixels / float(total_pixels)


def capture_snapshot(
    chrome_bin: str,
    url: str,
    out_png: Path,
    window_size: Tuple[int, int] = (1280, 800),
    virtual_time_budget_ms: int = 3000,
) -> Tuple[int, str]:
    out_png.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix="atb_headless_") as user_data_dir:
        cmd = [
            chrome_bin,
            "--headless=new",
            "--disable-gpu",
            "--no-first-run",
            "--no-default-browser-check",
            "--mute-audio",
            f"--user-data-dir={user_data_dir}",
            f"--window-size={window_size[0]},{window_size[1]}",
            f"--virtual-time-budget={virtual_time_budget_ms}",
            f"--screenshot={out_png}",
            url,
        ]
        proc = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, timeout=45)
        return proc.returncode, (proc.stdout + "\n" + proc.stderr).strip()


def parse_args(argv: Optional[list[str]] = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Verify HTML5 Canvas game port with Headless Chrome snapshots and non-black pixel ratio checks."
    )
    parser.add_argument(
        "--web-dir",
        required=True,
        help="Path to target/<game>/web directory containing index.html",
    )
    parser.add_argument(
        "--out-dir",
        default=None,
        help="Directory to write screen_initial.png, screen_gameplay.png, and screen_stage2.png (defaults to <web-dir>/../analysis/snapshots)",
    )
    parser.add_argument(
        "--min-colored-ratio",
        type=float,
        default=0.90,
        help="Minimum required ratio of non-black pixels (0.0 to 1.0, default: 0.90)",
    )
    parser.add_argument(
        "--chrome-bin",
        default=None,
        help="Optional explicit path to Chrome/Chromium executable",
    )
    return parser.parse_args(argv)


def main(argv: Optional[list[str]] = None) -> int:
    args = parse_args(argv)
    web_dir = Path(args.web_dir).resolve()
    index_html = web_dir / "index.html"

    if not web_dir.is_dir() or not index_html.is_file():
        print(f"[ERROR] index.html not found in --web-dir: {web_dir}", file=sys.stderr)
        return 1

    out_dir = (
        Path(args.out_dir).resolve()
        if args.out_dir
        else (web_dir.parent / "analysis" / "snapshots").resolve()
    )

    chrome_bin = find_chrome_binary(args.chrome_bin)
    if not chrome_bin:
        print(
            "[ERROR] Could not locate Chrome/Chromium binary. Install Google Chrome or pass --chrome-bin.",
            file=sys.stderr,
        )
        return 1

    # Check that web/assets symlink or directory exists when ../assets is present
    parent_assets = web_dir.parent / "assets"
    web_assets = web_dir / "assets"
    if parent_assets.is_dir() and not web_assets.exists():
        print(
            f"[ERROR] Missing symbolic link {web_assets} -> ../assets. Run `ln -sfn ../assets {web_assets}`.",
            file=sys.stderr,
        )
        return 1

    stages = [
        ("screen_initial.png", "?atb_verify_stage=initial", 2000),
        ("screen_gameplay.png", "?atb_verify_stage=gameplay", 4000),
        ("screen_stage2.png", "?atb_verify_stage=stage2", 6000),
    ]

    # Serve from target/<game>/ parent if assets live in ../assets, or from web_dir directly
    serve_root = web_dir.parent if parent_assets.is_dir() else web_dir
    url_prefix = f"/{web_dir.name}/index.html" if serve_root != web_dir else "/index.html"

    failures = []
    with serve_directory(serve_root) as port:
        for filename, query, budget_ms in stages:
            target_url = f"http://127.0.0.1:{port}{url_prefix}{query}"
            out_png = out_dir / filename
            rc, logs = capture_snapshot(
                chrome_bin=chrome_bin,
                url=target_url,
                out_png=out_png,
                virtual_time_budget_ms=budget_ms,
            )
            if rc != 0 or not out_png.is_file():
                failures.append(f"{filename}: Chrome exited with code {rc}\n{logs}")
                continue

            console_errors = [
                line
                for line in logs.splitlines()
                if "INFO:CONSOLE" in line and ("Uncaught " in line or "Error:" in line or "DOMException" in line)
                or "ERROR:CONSOLE" in line
            ]
            if console_errors:
                failures.append(f"{filename}: Console errors detected:\n    " + "\n    ".join(console_errors))

            ratio = compute_png_colored_ratio(out_png)
            status = "PASS" if ratio >= args.min_colored_ratio else "FAIL"
            print(f"[{status}] {filename}: colored pixel ratio = {ratio:.2%} (threshold >= {args.min_colored_ratio:.0%})")
            if ratio < args.min_colored_ratio:
                failures.append(
                    f"{filename}: colored pixel ratio {ratio:.2%} is below required {args.min_colored_ratio:.0%}"
                )

    if failures:
        print("\n[VERIFY FAILED] Zero-Black-Screen verification failed:", file=sys.stderr)
        for item in failures:
            print(f"  - {item}", file=sys.stderr)
        return 1

    print("\n[VERIFY PASSED] All 3 snapshots captured and exceeded colored pixel threshold.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
