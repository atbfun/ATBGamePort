# Phase 3 & 4: Portable OS Launchers, Zip Permissions & file:/// Verification Specification

## 1. Portable Bundle Materialization
When delivering large game assets (tens of megabytes of audio or level packs), running via a local HTTP server keeps memory usage low and isolates `localStorage` to a localhost port:
1. **Full Dereferencing**:
   - Copy all assets into `dist/<game>-portable/` using physical byte copy (`symlinks=False`), dereferencing symlinks like `web/assets -> ../assets`.
   - Ensure `dist/<game>-portable/index.html` is directly accessible alongside `assets/`.
2. **Platform-Native Dual Launchers**:
   - Provide zero-dependency, double-click launchers for both major desktop platforms without requiring users to install Python, Node.js, or external CLI tools.

## 2. macOS Double-Click Launcher (`Play-macOS.command`)
1. **Script Architecture**:
   - Self-contained POSIX bash script marked executable (`chmod +x` / `0755`).
   - Automatically navigates to the script's root directory: `cd "$(dirname "$0")"`.
   - Discovers a free local port dynamically using Python 3:
     ```bash
     PORT=$(python3 -c "import socket; s=socket.socket(); s.bind(('127.0.0.1', 0)); print(s.getsockname()[1]); s.close()" 2>/dev/null)
     ```
   - Launches a lightweight background HTTP server bound strictly to loopback (`127.0.0.1:$PORT`).
   - Opens the player's default browser: `open "http://127.0.0.1:$PORT/index.html"`.
   - Traps `EXIT`, `INT`, and `TERM` signals to cleanly terminate the background server process when the user closes the terminal window.

## 3. Windows Zero-Dependency Launcher (`Play-Windows.bat`)
1. **Built-in PowerShell `.NET` Microserver**:
   - Zero-dependency: works out-of-the-box on clean Windows 10 and 11 systems without Python, Node.js, or third-party web servers.
   - Invokes `powershell.exe -NoProfile -ExecutionPolicy Bypass` with an inline script.
   - Binds a dynamic port using `System.Net.Sockets.TcpListener` on loopback `127.0.0.1`.
   - Starts an embedded `System.Net.HttpListener` serving files with correct MIME mappings for HTML, JS, CSS, PNG, JPG, SVG, MP3, OGG, WAV, JSON, and WASM.
   - Automatically launches the default browser via `Start-Process "http://127.0.0.1:$p/index.html"`.

## 4. Distribution Zip Archive & Unix Permission Bits
1. **Permission Preservation in Zip Headers**:
   - Standard zip creation tools frequently drop Unix executable permissions on `.command` or `.sh` files, causing macOS to display `"The file cannot be executed because you do not have appropriate access privileges"`.
   - In `build_release_zip()`, explicitly set `ZipInfo.external_attr = (0o100755 << 16) | 0o20` on `Play-macOS.command`.
   - Place `<game>-standalone.html` at the zip root for instant zero-terminal play, alongside the `<game>-portable/` directory.

## 5. Automated Headless Verification (`scripts/verify-package.py`)
Run automated verification without an active HTTP server using `scripts/verify-package.py`:

```bash
python3 skills/atb-game-package/scripts/verify-package.py \
  --html-file target/<game>/dist/<game>-standalone.html \
  --portable-dir target/<game>/dist/<game>-portable \
  --zip-file target/<game>/dist/<game>-release.zip \
  --min-colored-ratio 0.90
```

### Verification Criteria:
1. **`file:///` Protocol Zero Console Errors**:
   - Headless Chrome loads `file:///<abs_path>/<game>-standalone.html?atb_verify_stage=initial|gameplay|stage2`.
   - Log output must report `0` CORS violations, `0` uncaught `DOMException` / `SecurityError` exceptions, and `0` script load errors.
2. **Three-Stage Colored Pixel Ratio ($\ge 90\%$)**:
   - Captures `screen_file_initial.png`, `screen_file_gameplay.png`, and `screen_file_stage2.png`.
   - Each snapshot must achieve a non-black pixel ratio $\ge 90\%$.
3. **Portable & Archive Integrity**:
   - Assert zero dangling symlinks in `<game>-portable/`.
   - Verify `Play-macOS.command` has Unix `0755` executable bits in both the filesystem and `<game>-release.zip`.
