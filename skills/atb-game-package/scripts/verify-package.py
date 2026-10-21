#!/usr/bin/env python3
"""
Automated Headless file:/// Protocol & Bundle Verification (atb-game-package).

Verifies packaged offline HTML5 game artifacts without starting an HTTP server:
1. Opens <game>-standalone.html directly via file:/// in Headless Chrome/Chromium.
2. Captures screenshots across 3 verification stages (?atb_verify_stage=initial|gameplay|stage2).
3. Verifies non-black colored pixel ratio (default >= 90%) and 0 console/CORS errors.
4. Verifies <game>-portable/ directory integrity (no dangling symlinks, executable scripts).
5. Verifies <game>-release.zip contains preserved Unix 0755 executable permissions.

Powered by fun.aitobox.com.
"""

from __future__ import annotations

import argparse
import os
import shutil
import struct
import subprocess
import sys
import tempfile
import zipfile
import zlib
from pathlib import Path
from typing import List, Optional, Tuple


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
    Pure-Python PNG reader computing the ratio of non-black pixels.
    Supports 8-bit RGB (color_type=2) and RGBA (color_type=6) PNGs.
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

        if filter_type == 0:
            cur_row[:] = row_bytes
        elif filter_type == 1:
            for i in range(stride):
                left = cur_row[i - bpp] if i >= bpp else 0
                cur_row[i] = (row_bytes[i] + left) & 0xFF
        elif filter_type == 2:
            for i in range(stride):
                cur_row[i] = (row_bytes[i] + prev_row[i]) & 0xFF
        elif filter_type == 3:
            for i in range(stride):
                left = cur_row[i - bpp] if i >= bpp else 0
                up = prev_row[i]
                cur_row[i] = (row_bytes[i] + ((left + up) >> 1)) & 0xFF
        elif filter_type == 4:
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
    with tempfile.TemporaryDirectory(prefix="atb_file_verify_") as user_data_dir:
        cmd = [
            chrome_bin,
            "--headless=new",
            "--disable-gpu",
            "--no-first-run",
            "--no-default-browser-check",
            "--mute-audio",
            "--enable-logging=stderr",
            f"--user-data-dir={user_data_dir}",
            f"--window-size={window_size[0]},{window_size[1]}",
            f"--virtual-time-budget={virtual_time_budget_ms}",
            f"--screenshot={out_png}",
            url,
        ]
        proc = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, timeout=45)
        return proc.returncode, (proc.stdout + "\n" + proc.stderr).strip()


def verify_standalone_file_url(
    chrome_bin: str,
    html_file: Path,
    out_dir: Path,
    min_colored_ratio: float = 0.90,
) -> List[str]:
    failures: List[str] = []
    abs_path = html_file.resolve().as_posix()
    base_file_url = f"file://{abs_path}"

    stages = [
        ("screen_file_initial.png", "?atb_verify_stage=initial", 2000),
        ("screen_file_gameplay.png", "?atb_verify_stage=gameplay", 4000),
        ("screen_file_stage2.png", "?atb_verify_stage=stage2", 6000),
    ]

    for filename, query, budget_ms in stages:
        target_url = f"{base_file_url}{query}"
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
            if ("INFO:CONSOLE" in line or "ERROR:CONSOLE" in line)
            and ("Uncaught " in line or "Error:" in line or "DOMException" in line or "CORS" in line)
        ]
        if console_errors:
            failures.append(f"{filename}: Console errors detected in file:/// mode:\n    " + "\n    ".join(console_errors))

        try:
            ratio = compute_png_colored_ratio(out_png)
            status = "PASS" if ratio >= min_colored_ratio else "FAIL"
            print(f"[{status}] [file:///] {filename}: colored ratio = {ratio:.2%} (threshold >= {min_colored_ratio:.0%})")
            if ratio < min_colored_ratio:
                failures.append(
                    f"{filename}: colored pixel ratio {ratio:.2%} is below required {min_colored_ratio:.0%}"
                )
        except Exception as e:
            failures.append(f"{filename}: PNG ratio calculation failed: {e}")

    return failures


def verify_portable_bundle(portable_dir: Path) -> List[str]:
    issues: List[str] = []
    if not portable_dir.is_dir():
        return [f"Portable directory does not exist: {portable_dir}"]

    index_html = portable_dir / "index.html"
    if not index_html.is_file():
        issues.append(f"Missing index.html inside portable bundle: {portable_dir}")

    macos_cmd = portable_dir / "Play-macOS.command"
    if not macos_cmd.is_file():
        issues.append(f"Missing Play-macOS.command in: {portable_dir}")
    else:
        st = os.stat(macos_cmd)
        if not bool(st.st_mode & 0o111):
            issues.append(f"Play-macOS.command is not marked executable in {portable_dir}")

    windows_bat = portable_dir / "Play-Windows.bat"
    if not windows_bat.is_file():
        issues.append(f"Missing Play-Windows.bat in: {portable_dir}")

    # Check for dangling symlinks
    for root, dirs, files in os.walk(portable_dir):
        for name in dirs + files:
            p = Path(root) / name
            if p.is_symlink():
                resolved = p.resolve()
                if not resolved.exists():
                    issues.append(f"Dangling symlink inside portable bundle: {p} -> {resolved}")

    return issues


def verify_release_zip(zip_path: Path) -> List[str]:
    issues: List[str] = []
    if not zip_path.is_file():
        return [f"Release zip does not exist: {zip_path}"]

    try:
        with zipfile.ZipFile(zip_path, "r") as zf:
            corrupt = zf.testzip()
            if corrupt:
                issues.append(f"Corrupted file inside zip: {corrupt}")

            macos_entries = [info for info in zf.infolist() if info.filename.endswith("Play-macOS.command")]
            if not macos_entries:
                issues.append("Missing Play-macOS.command inside release zip")
            else:
                info = macos_entries[0]
                perm = (info.external_attr >> 16) & 0o777
                if not bool(perm & 0o111):
                    issues.append(f"Play-macOS.command in zip missing Unix executable permissions (octal: {oct(perm)})")
    except Exception as e:
        issues.append(f"Failed to read release zip: {e}")

    return issues


def parse_args(argv: Optional[List[str]] = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Verify atb-game-package offline distribution artifacts."
    )
    parser.add_argument(
        "--html-file",
        default=None,
        help="Path to <game>-standalone.html to test via direct file:/// protocol",
    )
    parser.add_argument(
        "--portable-dir",
        default=None,
        help="Path to <game>-portable directory",
    )
    parser.add_argument(
        "--zip-file",
        default=None,
        help="Path to <game>-release.zip",
    )
    parser.add_argument(
        "--out-dir",
        default=None,
        help="Directory to save snapshot PNGs (defaults to <html-file-parent>/snapshots)",
    )
    parser.add_argument(
        "--min-colored-ratio",
        type=float,
        default=0.90,
        help="Minimum required colored pixel ratio (default: 0.90)",
    )
    parser.add_argument(
        "--skip-browser",
        action="store_true",
        help="Skip headless Chrome browser execution (verify bundle and zip integrity only)",
    )
    parser.add_argument(
        "--chrome-bin",
        default=None,
        help="Explicit path to Chrome/Chromium executable",
    )
    return parser.parse_args(argv)


def main(argv: Optional[List[str]] = None) -> int:
    args = parse_args(argv)
    failures: List[str] = []

    if args.portable_dir:
        p_issues = verify_portable_bundle(Path(args.portable_dir))
        if p_issues:
            failures.extend(p_issues)
        else:
            print(f"[PASS] Portable bundle integrity verified: {args.portable_dir}")

    if args.zip_file:
        z_issues = verify_release_zip(Path(args.zip_file))
        if z_issues:
            failures.extend(z_issues)
        else:
            print(f"[PASS] Release zip permissions and integrity verified: {args.zip_file}")

    if args.html_file and not args.skip_browser:
        html_p = Path(args.html_file).resolve()
        if not html_p.is_file():
            print(f"[ERROR] Standalone HTML not found: {html_p}", file=sys.stderr)
            return 1

        chrome_bin = find_chrome_binary(args.chrome_bin)
        if not chrome_bin:
            print("[ERROR] Chrome binary not found. Install Chrome or pass --chrome-bin.", file=sys.stderr)
            return 1

        out_dir = Path(args.out_dir).resolve() if args.out_dir else (html_p.parent / "snapshots").resolve()
        b_issues = verify_standalone_file_url(
            chrome_bin=chrome_bin,
            html_file=html_p,
            out_dir=out_dir,
            min_colored_ratio=args.min_colored_ratio,
        )
        if b_issues:
            failures.extend(b_issues)
        else:
            print(f"[PASS] Headless file:/// verification passed for: {html_p.name}")

    if failures:
        print("\n[VERIFY FAILED] Verification failures detected:", file=sys.stderr)
        for f in failures:
            print(f"  - {f}", file=sys.stderr)
        return 1

    print("\n[VERIFY ALL PASSED] All package verifications succeeded!")
    return 0


if __name__ == "__main__":
    sys.exit(main())
