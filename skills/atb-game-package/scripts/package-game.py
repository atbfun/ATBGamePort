#!/usr/bin/env python3
"""
Zero-Dependency Offline HTML5 Game Packager (atb-game-package).

Bundles HTML5 games into:
1. <game>-standalone.html: Single self-contained HTML file with embedded VFS
   and runtime shim for 100% offline file:/// browser execution.
2. <game>-portable/: Materialized directory with OS-native zero-dependency launchers
   (Play-macOS.command, Play-Windows.bat) and dereferenced assets.
3. <game>-release.zip: Distribution zip archive with preserved Unix 0755 permissions.

Powered by fun.aitobox.com.
"""

from __future__ import annotations

import argparse
import base64
import html.parser
import json
import mimetypes
import os
import re
import shutil
import sys
import zipfile
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple


MIME_MAP = {
    ".png": "image/png",
    ".jpg": "image/jpeg",
    ".jpeg": "image/jpeg",
    ".gif": "image/gif",
    ".svg": "image/svg+xml",
    ".webp": "image/webp",
    ".ico": "image/x-icon",
    ".mp3": "audio/mpeg",
    ".ogg": "audio/ogg",
    ".wav": "audio/wav",
    ".m4a": "audio/mp4",
    ".json": "application/json",
    ".xml": "application/xml",
    ".txt": "text/plain",
    ".wasm": "application/wasm",
    ".css": "text/css",
    ".js": "application/javascript",
}


@dataclass
class GameLayout:
    game_name: str
    root_dir: Path
    web_dir: Path
    entrypoint: Path
    assets_dirs: List[Path]


def detect_mime(file_path: Path) -> str:
    ext = file_path.suffix.lower()
    if ext in MIME_MAP:
        return MIME_MAP[ext]
    mime, _ = mimetypes.guess_type(str(file_path))
    return mime or "application/octet-stream"


def resolve_game_layout(input_path: Path, explicit_name: Optional[str] = None) -> GameLayout:
    path = input_path.resolve()
    if not path.exists():
        raise FileNotFoundError(f"Input path does not exist: {path}")

    # Case 1: Direct file input (e.g. path/to/index.html)
    if path.is_file() and path.name.endswith(".html"):
        web_dir = path.parent
        root_dir = web_dir.parent if web_dir.name == "web" else web_dir
        entrypoint = path
        game_name = explicit_name or (root_dir.name if root_dir.name != "web" else web_dir.parent.name)
    elif path.is_dir():
        # Check standard ATBGamePort structure: target/<game>/web/index.html
        if (path / "web" / "index.html").is_file():
            web_dir = path / "web"
            root_dir = path
            entrypoint = path / "web" / "index.html"
            game_name = explicit_name or path.name
        elif (path / "index.html").is_file():
            web_dir = path
            root_dir = path.parent if path.name == "web" else path
            entrypoint = path / "index.html"
            game_name = explicit_name or (root_dir.name if path.name == "web" else path.name)
        else:
            raise FileNotFoundError(f"Could not locate index.html inside {path} or {path / 'web'}")
    else:
        raise ValueError(f"Invalid input path: {path}")

    # Discover asset directories (both siblings and children)
    assets_dirs: List[Path] = []
    candidates = [
        root_dir / "assets",
        web_dir / "assets",
        web_dir / "images",
        web_dir / "sounds",
        web_dir / "music",
        web_dir / "data",
        web_dir / "levels",
    ]
    seen_resolved: Set[Path] = set()
    for candidate in candidates:
        if candidate.exists():
            resolved = candidate.resolve()
            if resolved not in seen_resolved:
                seen_resolved.add(resolved)
                assets_dirs.append(candidate)

    return GameLayout(
        game_name=game_name,
        root_dir=root_dir,
        web_dir=web_dir,
        entrypoint=entrypoint,
        assets_dirs=assets_dirs,
    )


def normalize_asset_key(rel_str: str) -> str:
    cleaned = rel_str.split("?")[0].split("#")[0].replace("\\", "/")
    # Remove leading ../ or ./
    cleaned = re.sub(r"^(\.\./|\./)+", "", cleaned)
    # Remove leading slashes
    cleaned = cleaned.lstrip("/")
    return cleaned


def gather_vfs_assets(layout: GameLayout) -> Dict[str, dict]:
    vfs: Dict[str, dict] = {}
    scanned_files: Set[Path] = set()

    def process_file(file_path: Path, base_dir: Path, key_prefix: str = ""):
        real_path = file_path.resolve()
        if real_path in scanned_files or not real_path.is_file():
            return
        scanned_files.add(real_path)

        try:
            rel = file_path.relative_to(base_dir).as_posix()
        except ValueError:
            rel = file_path.name

        if key_prefix and not rel.startswith(key_prefix):
            rel = f"{key_prefix.rstrip('/')}/{rel}"

        canon_key = normalize_asset_key(rel)
        raw_bytes = real_path.read_bytes()
        mime = detect_mime(real_path)
        b64_str = base64.b64encode(raw_bytes).decode("ascii")
        entry = {"mime": mime, "b64": b64_str}

        vfs[canon_key] = entry
        # Also register variants
        vfs[f"./{canon_key}"] = entry
        vfs[f"../{canon_key}"] = entry
        if not canon_key.startswith("assets/"):
            vfs[f"assets/{canon_key}"] = entry

    # 1. Scan explicit asset directories
    for adir in layout.assets_dirs:
        resolved_adir = adir.resolve()
        if not resolved_adir.is_dir():
            continue
        prefix = "assets" if adir.name == "assets" or "assets" in adir.parts else ""
        for root, _, files in os.walk(resolved_adir):
            for f in sorted(files):
                if f.startswith("."):
                    continue
                p = Path(root) / f
                process_file(p, resolved_adir, key_prefix=prefix)

    # 2. Scan web directory for other static assets (png, jpg, mp3, json, etc.)
    for root, _, files in os.walk(layout.web_dir.resolve()):
        for f in sorted(files):
            if f.startswith(".") or f.endswith(".html"):
                continue
            p = Path(root) / f
            process_file(p, layout.web_dir.resolve())

    return vfs


def build_vfs_shim_js(vfs_data: Dict[str, dict]) -> str:
    vfs_json = json.dumps(vfs_data, separators=(",", ":"))
    return f"""(function() {{
  "use strict";
  window.__ATB_VFS__ = {vfs_json};

  function normalizeUrl(url) {{
    if (!url) return "";
    var s = String(url).split("?")[0].split("#")[0];
    try {{ s = decodeURIComponent(s); }} catch (e) {{}}
    s = s.replace(/\\\\/g, "/");
    s = s.replace(/^[a-zA-Z]+:\\/\\/[^/]+\\//, "");
    s = s.replace(/^(\\.\\.\\/|\\.\\/)+/, "");
    s = s.replace(/^\\/+/, "");
    return s;
  }}

  function getVfsEntry(url) {{
    if (!url || !window.__ATB_VFS__) return null;
    var norm = normalizeUrl(url);
    if (window.__ATB_VFS__[norm]) return window.__ATB_VFS__[norm];
    if (window.__ATB_VFS__["assets/" + norm]) return window.__ATB_VFS__["assets/" + norm];
    var parts = norm.split("/");
    var filename = parts[parts.length - 1];
    if (window.__ATB_VFS__[filename]) return window.__ATB_VFS__[filename];
    return null;
  }}

  function b64ToUint8(b64) {{
    var bin = atob(b64);
    var len = bin.length;
    var bytes = new Uint8Array(len);
    for (var i = 0; i < len; i++) {{
      bytes[i] = bin.charCodeAt(i);
    }}
    return bytes;
  }}

  // 1. Intercept window.fetch
  var originalFetch = window.fetch;
  window.fetch = function(input, init) {{
    var url = typeof input === "string" ? input : (input && input.url ? input.url : "");
    var entry = getVfsEntry(url);
    if (entry) {{
      var bytes = b64ToUint8(entry.b64);
      var blob = new Blob([bytes], {{ type: entry.mime }});
      var resp = new Response(blob, {{
        status: 200,
        statusText: "OK",
        headers: {{ "Content-Type": entry.mime }}
      }});
      return Promise.resolve(resp);
    }}
    return originalFetch ? originalFetch.apply(this, arguments) : Promise.reject(new Error("fetch failed: " + url));
  }};

  // 2. Intercept XMLHttpRequest
  var OriginalXHR = window.XMLHttpRequest;
  function PatchedXHR() {{
    var xhr = new OriginalXHR();
    var targetUrl = "";
    var origOpen = xhr.open;
    var origSend = xhr.send;

    xhr.open = function(method, url) {{
      targetUrl = url;
      return origOpen.apply(this, arguments);
    }};

    xhr.send = function() {{
      var entry = getVfsEntry(targetUrl);
      if (entry) {{
        var bytes = b64ToUint8(entry.b64);
        var mime = entry.mime;
        setTimeout(function() {{
          Object.defineProperty(xhr, "readyState", {{ value: 4, writable: true }});
          Object.defineProperty(xhr, "status", {{ value: 200, writable: true }});
          Object.defineProperty(xhr, "statusText", {{ value: "OK", writable: true }});
          var respData = bytes.buffer;
          if (xhr.responseType === "blob") {{
            respData = new Blob([bytes], {{ type: mime }});
          }} else if (xhr.responseType === "text" || !xhr.responseType) {{
            var str = "";
            for (var j = 0; j < bytes.length; j++) {{ str += String.fromCharCode(bytes[j]); }}
            try {{ respData = decodeURIComponent(escape(str)); }} catch (e) {{ respData = str; }}
            Object.defineProperty(xhr, "responseText", {{ value: respData, writable: true }});
          }} else if (xhr.responseType === "json") {{
            var dec = new TextDecoder("utf-8").decode(bytes);
            respData = JSON.parse(dec);
          }}
          Object.defineProperty(xhr, "response", {{ value: respData, writable: true }});
          if (typeof xhr.onreadystatechange === "function") xhr.onreadystatechange();
          if (typeof xhr.onload === "function") xhr.onload();
          xhr.dispatchEvent(new Event("readystatechange"));
          xhr.dispatchEvent(new Event("load"));
        }}, 0);
        return;
      }}
      return origSend.apply(this, arguments);
    }};

    return xhr;
  }}
  PatchedXHR.prototype = OriginalXHR.prototype;
  window.XMLHttpRequest = PatchedXHR;

  // 3. Intercept Image src & Element.setAttribute
  var imgProto = window.HTMLImageElement ? window.HTMLImageElement.prototype : null;
  if (imgProto) {{
    var origImgSrcDesc = Object.getOwnPropertyDescriptor(imgProto, "src");
    if (origImgSrcDesc && origImgSrcDesc.set) {{
      Object.defineProperty(imgProto, "src", {{
        set: function(val) {{
          var entry = getVfsEntry(val);
          if (entry && typeof val === "string" && !val.startsWith("data:") && !val.startsWith("blob:")) {{
            val = "data:" + entry.mime + ";base64," + entry.b64;
          }}
          return origImgSrcDesc.set.call(this, val);
        }},
        get: origImgSrcDesc.get,
        configurable: true
      }});
    }}
  }}

  var origSetAttr = Element.prototype.setAttribute;
  Element.prototype.setAttribute = function(name, val) {{
    if (String(name).toLowerCase() === "src" && typeof val === "string" && !val.startsWith("data:") && !val.startsWith("blob:")) {{
      var entry = getVfsEntry(val);
      if (entry) {{
        val = "data:" + entry.mime + ";base64," + entry.b64;
      }}
    }}
    return origSetAttr.call(this, name, val);
  }};

  // 4. Intercept Audio & MediaElement src
  var origAudio = window.Audio;
  window.Audio = function(src) {{
    var entry = getVfsEntry(src);
    if (entry) {{
      src = "data:" + entry.mime + ";base64," + entry.b64;
    }}
    return new origAudio(src);
  }};
  window.Audio.prototype = origAudio.prototype;

  var mediaProto = window.HTMLMediaElement ? window.HTMLMediaElement.prototype : null;
  if (mediaProto) {{
    var origMediaSrcDesc = Object.getOwnPropertyDescriptor(mediaProto, "src");
    if (origMediaSrcDesc && origMediaSrcDesc.set) {{
      Object.defineProperty(mediaProto, "src", {{
        set: function(val) {{
          var entry = getVfsEntry(val);
          if (entry && typeof val === "string" && !val.startsWith("data:") && !val.startsWith("blob:")) {{
            val = "data:" + entry.mime + ";base64," + entry.b64;
          }}
          return origMediaSrcDesc.set.call(this, val);
        }},
        get: origMediaSrcDesc.get,
        configurable: true
      }});
    }}
  }}

  console.log(
    "%c📦 Bundled with atb-game-package | Zero-Dependency Offline VFS Active",
    "background:#0f172a;color:#38bdf8;padding:4px 8px;border-radius:4px;font-weight:bold;"
  );
}})();
"""


def inline_css_urls(css_text: str, vfs: Dict[str, dict]) -> str:
    def replace_url(match: re.Match) -> str:
        url = match.group(1).strip("'\" \t\r\n")
        canon = normalize_asset_key(url)
        entry = vfs.get(canon) or vfs.get(f"assets/{canon}")
        if entry:
            return f"url('data:{entry['mime']};base64,{entry['b64']}')"
        return match.group(0)

    return re.sub(r"url\(([^)]+)\)", replace_url, css_text)


def build_standalone_html(layout: GameLayout, vfs: Dict[str, dict], out_file: Path) -> Path:
    html_raw = layout.entrypoint.read_text(encoding="utf-8")

    # 1. Inline CSS stylesheets
    def replace_css_link(match: re.Match) -> str:
        href = match.group(1).strip("'\"")
        css_path = (layout.web_dir / href).resolve()
        if css_path.is_file():
            css_content = css_path.read_text(encoding="utf-8")
            inlined_css = inline_css_urls(css_content, vfs)
            return f"<style>/* inlined {href} */\n{inlined_css}\n</style>"
        return match.group(0)

    html_transformed = re.sub(
        r'<link\s+[^>]*rel=["\']stylesheet["\'][^>]*href=["\']([^"\']+)["\'][^>]*>',
        replace_css_link,
        html_raw,
        flags=re.IGNORECASE,
    )

    # 2. Inline Scripts
    def replace_script(match: re.Match) -> str:
        full_tag = match.group(0)
        src_match = re.search(r'src=["\']([^"\']+)["\']', full_tag, flags=re.IGNORECASE)
        if not src_match:
            return full_tag
        src = src_match.group(1)
        if src.startswith("http://") or src.startswith("https://"):
            return full_tag
        js_path = (layout.web_dir / src).resolve()
        if js_path.is_file():
            js_content = js_path.read_text(encoding="utf-8")
            # Escape </script> inside javascript to avoid early HTML parser termination
            safe_js = js_content.replace("</script>", "<\\/script>")
            return f"<script>/* inlined {src} */\n{safe_js}\n</script>"
        return full_tag

    html_transformed = re.sub(
        r'<script\s+[^>]*src=["\'][^"\']+["\'][^>]*>\s*</script>',
        replace_script,
        html_transformed,
        flags=re.IGNORECASE,
    )

    # 3. Rewrite static <img src="..."> in HTML if in VFS
    def replace_img_src(match: re.Match) -> str:
        full_tag = match.group(0)
        src_match = re.search(r'src=["\']([^"\']+)["\']', full_tag, flags=re.IGNORECASE)
        if not src_match:
            return full_tag
        src = src_match.group(1)
        canon = normalize_asset_key(src)
        entry = vfs.get(canon) or vfs.get(f"assets/{canon}")
        if entry:
            data_uri = f"data:{entry['mime']};base64,{entry['b64']}"
            return full_tag.replace(src, data_uri, 1)
        return full_tag

    html_transformed = re.sub(
        r'<img\s+[^>]*src=["\'][^"\']+["\'][^>]*>',
        replace_img_src,
        html_transformed,
        flags=re.IGNORECASE,
    )

    # 4. Inject VFS Shim Script at top of <head>
    shim_js = build_vfs_shim_js(vfs)
    shim_tag = f"<script id=\"atb-vfs-shim\">\n{shim_js}\n</script>\n"

    if "<head>" in html_transformed:
        html_final = html_transformed.replace("<head>", f"<head>\n{shim_tag}", 1)
    elif "<HEAD>" in html_transformed:
        html_final = html_transformed.replace("<HEAD>", f"<HEAD>\n{shim_tag}", 1)
    else:
        html_final = shim_tag + html_transformed

    out_file.parent.mkdir(parents=True, exist_ok=True)
    out_file.write_text(html_final, encoding="utf-8")
    return out_file


MACOS_COMMAND_TEMPLATE = """#!/usr/bin/env bash
# macOS Zero-Dependency Game Launcher for {game_name}
# Powered by fun.aitobox.com

cd "$(dirname "$0")" || exit 1

# Find a free local port
PORT=$(python3 -c "import socket; s=socket.socket(); s.bind(('127.0.0.1', 0)); print(s.getsockname()[1]); s.close()" 2>/dev/null)
if [ -z "$PORT" ]; then
  PORT=8000
fi

echo "=========================================================="
echo " Starting local server for {game_name} at http://127.0.0.1:$PORT"
echo " (Close this terminal window or press Ctrl+C to exit)"
echo "=========================================================="

# Start server in background
python3 -m http.server "$PORT" --bind 127.0.0.1 >/dev/null 2>&1 &
SERVER_PID=$!

trap 'kill $SERVER_PID 2>/dev/null; exit 0' EXIT INT TERM

sleep 0.5
open "http://127.0.0.1:$PORT/index.html"

wait $SERVER_PID
"""

WINDOWS_BAT_TEMPLATE = """@echo off
rem Windows Zero-Dependency Launcher for {game_name} (PowerShell HttpListener)
rem Powered by fun.aitobox.com

cd /d "%~dp0"
echo ==========================================================
echo  Starting local server for {game_name}...
echo  (Press Ctrl+C to exit)
echo ==========================================================

powershell.exe -NoProfile -ExecutionPolicy Bypass -Command ^
  "$port = (New-Object System.Net.Sockets.TcpListener([System.Net.IPAddress]::Loopback, 0)); $port.Start(); $p = $port.LocalEndpoint.Port; $port.Stop();" ^
  "Start-Process \\"http://127.0.0.1:$p/index.html\\";" ^
  "$listener = New-Object System.Net.HttpListener;" ^
  "$listener.Prefixes.Add(\\"http://127.0.0.1:$p/\\");" ^
  "$listener.Start();" ^
  "Write-Host \\"Running at http://127.0.0.1:$p/ (Ctrl+C to exit)\\" -ForegroundColor Cyan;" ^
  "$mimes = @{ '.html'='text/html'; '.js'='application/javascript'; '.css'='text/css'; '.png'='image/png'; '.jpg'='image/jpeg'; '.svg'='image/svg+xml'; '.mp3'='audio/mpeg'; '.ogg'='audio/ogg'; '.wav'='audio/wav'; '.json'='application/json'; '.wasm'='application/wasm' };" ^
  "while ($listener.IsListening) {;" ^
  "  try {;" ^
  "    $ctx = $listener.GetContext();" ^
  "    $url = $ctx.Request.Url.LocalPath.TrimStart('/');" ^
  "    if ($url -eq '') { $url = 'index.html'; };" ^
  "    $file = Join-Path (Get-Location) $url;" ^
  "    if (Test-Path $file -PathType Leaf) {;" ^
  "      $ext = [System.IO.Path]::GetExtension($file).ToLower();" ^
  "      $mime = if ($mimes.ContainsKey($ext)) { $mimes[$ext] } else { 'application/octet-stream' };" ^
  "      $bytes = [System.IO.File]::ReadAllBytes($file);" ^
  "      $ctx.Response.ContentType = $mime;" ^
  "      $ctx.Response.ContentLength64 = $bytes.Length;" ^
  "      $ctx.Response.OutputStream.Write($bytes, 0, $bytes.Length);" ^
  "    } else {;" ^
  "      $ctx.Response.StatusCode = 404;" ^
  "    };" ^
  "    $ctx.Response.Close();" ^
  "  } catch { break; };" ^
  "};"
"""

README_PLAY_TEMPLATE = """==========================================================
 {game_name} - Offline Game Package
 Powered by fun.aitobox.com
==========================================================

[English]
How to play:
1. Fast direct play:
   Double-click '{game_name}-standalone.html' in the release folder.
   It opens directly in your default browser with zero dependencies and 0 CORS issues!
2. Portable server mode:
   - On macOS: Double-click 'Play-macOS.command'
   - On Windows: Double-click 'Play-Windows.bat'

----------------------------------------------------------

[简体中文]
运行说明：
1. 极简即点即玩：
   直接双击同级目录下的 '{game_name}-standalone.html'，
   系统默认浏览器即可直接打开满血运行，无需配置任何环境！
2. 便携本地服务模式：
   - macOS 系统：直接双击运行 'Play-macOS.command'
   - Windows 系统：直接双击运行 'Play-Windows.bat'

==========================================================
"""


def build_portable_bundle(layout: GameLayout, out_dir: Path) -> Path:
    out_dir.mkdir(parents=True, exist_ok=True)

    # 1. Copy web directory contents with symlinks dereferenced (symlinks=False copies actual content)
    for item in layout.web_dir.iterdir():
        dest = out_dir / item.name
        if item.is_dir() or item.is_symlink():
            if dest.exists():
                shutil.rmtree(dest)
            # copytree with symlinks=False dereferences symlinks into actual directories
            shutil.copytree(item.resolve(), dest, symlinks=False)
        elif item.is_file():
            shutil.copy2(item, dest)

    # 2. Ensure assets directory exists in portable folder if root_dir/assets exists
    parent_assets = layout.root_dir / "assets"
    if parent_assets.is_dir() and not (out_dir / "assets").exists():
        shutil.copytree(parent_assets.resolve(), out_dir / "assets", symlinks=False)

    # 3. Write Play-macOS.command
    macos_cmd = out_dir / "Play-macOS.command"
    macos_cmd.write_text(MACOS_COMMAND_TEMPLATE.replace("{game_name}", layout.game_name), encoding="utf-8")
    macos_cmd.chmod(0o755)

    # 4. Write Play-Windows.bat
    windows_bat = out_dir / "Play-Windows.bat"
    windows_bat.write_text(WINDOWS_BAT_TEMPLATE.replace("{game_name}", layout.game_name), encoding="utf-8")

    # 5. Write README-PLAY.txt
    readme_txt = out_dir / "README-PLAY.txt"
    readme_txt.write_text(README_PLAY_TEMPLATE.replace("{game_name}", layout.game_name), encoding="utf-8")

    return out_dir


def build_release_zip(standalone_html: Path, portable_dir: Path, out_zip: Path) -> Path:
    out_zip.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(out_zip, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        # Add standalone HTML at root of zip
        if standalone_html.is_file():
            zf.write(standalone_html, arcname=standalone_html.name)

        # Add portable folder with preserved permissions
        if portable_dir.is_dir():
            for root, _, files in os.walk(portable_dir):
                for f in files:
                    full_p = Path(root) / f
                    arcname = (Path(portable_dir.name) / full_p.relative_to(portable_dir)).as_posix()
                    zinfo = zipfile.ZipInfo.from_file(full_p, arcname=arcname)
                    if f.endswith(".command") or f.endswith(".sh"):
                        # Set Unix permissions 0755
                        zinfo.external_attr = (0o100755 << 16) | 0o20
                    else:
                        zinfo.external_attr = (0o100644 << 16) | 0o20
                    zf.writestr(zinfo, full_p.read_bytes())

    return out_zip


def package_game(
    input_dir: Path,
    out_dir: Optional[Path] = None,
    game_name: Optional[str] = None,
    mode: str = "all",
) -> Dict[str, Path]:
    layout = resolve_game_layout(input_dir, explicit_name=game_name)
    name = layout.game_name

    target_dist = out_dir.resolve() if out_dir else (layout.root_dir / "dist").resolve()
    target_dist.mkdir(parents=True, exist_ok=True)

    results: Dict[str, Path] = {}
    vfs = gather_vfs_assets(layout)

    standalone_html = target_dist / f"{name}-standalone.html"
    portable_dir = target_dist / f"{name}-portable"
    release_zip = target_dist / f"{name}-release.zip"

    if mode in ("all", "single"):
        print(f"[*] Building standalone HTML: {standalone_html.name} ({len(vfs)} VFS assets)...")
        build_standalone_html(layout, vfs, standalone_html)
        results["standalone_html"] = standalone_html

    if mode in ("all", "portable"):
        print(f"[*] Building portable bundle: {portable_dir.name}...")
        build_portable_bundle(layout, portable_dir)
        results["portable_dir"] = portable_dir

    if mode == "all":
        print(f"[*] Assembling distribution zip: {release_zip.name}...")
        build_release_zip(standalone_html, portable_dir, release_zip)
        results["release_zip"] = release_zip

    print(f"[+] Packaging complete! Artifacts created in: {target_dist}")
    return results


def parse_args(argv: Optional[List[str]] = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="atb-game-package: Zero-dependency offline HTML5 game packager."
    )
    parser.add_argument(
        "--input-dir",
        "-i",
        required=True,
        help="Path to target/<game> directory or folder containing index.html",
    )
    parser.add_argument(
        "--out-dir",
        "-o",
        default=None,
        help="Output directory (defaults to <input-dir>/dist)",
    )
    parser.add_argument(
        "--game-name",
        "-n",
        default=None,
        help="Explicit game name identifier (defaults to directory name)",
    )
    parser.add_argument(
        "--mode",
        "-m",
        choices=["all", "single", "portable"],
        default="all",
        help="Packaging mode: all (default), single (HTML only), or portable (folder only)",
    )
    return parser.parse_args(argv)


def main(argv: Optional[List[str]] = None) -> int:
    args = parse_args(argv)
    input_path = Path(args.input_dir)
    out_path = Path(args.out_dir) if args.out_dir else None

    try:
        package_game(
            input_dir=input_path,
            out_dir=out_path,
            game_name=args.game_name,
            mode=args.mode,
        )
        return 0
    except Exception as e:
        print(f"[ERROR] Packaging failed: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
