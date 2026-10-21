# Phase 1: Binary Reverse Engineering & Proprietary Format Dissection

> **Golden Rule**: When analyzing any native executable (`.exe`, `.dll`, PE image, Mach-O, or packed archive), you **MUST first activate and invoke the `reverse-engineer-anything` (REA) skill** and its dedicated REA toolchain, combined with local reverse engineering tools (`/Applications/Hopper Disassembler.app` on macOS and system CLI utilities). Never guess internal implementations from filenames alone.

## 1. REA Global Survey & Unpacking
1. Call the Skill tool with `"reverse-engineer-anything"` and invoke `open_binary` and `binary_overview` on the target executable in `source/<game_name>/`.
2. Determine CPU architecture, compiler toolchain (e.g., MSVC C++, Borland, MinGW), PE section layout (`.text`, `.rdata`, `.data`, `.rsrc`), and packing status (e.g., UPX, ASPack).
3. If the binary is packed (e.g., UPX sections `UPX0`/`UPX1`), unpack it first (`upx -d` or memory dump) before static symbol and control-flow analysis.

## 2. Hopper Disassembler Deep CFG & Decompilation
When `/Applications/Hopper Disassembler.app` is available on the machine, leverage it for complex algorithms (curve trajectory decoders, ballistic collision math, proprietary archive encryption/XOR keys, PRNG seeds):
- **Headless CLI Scripting**:
  ```bash
  /Applications/Hopper\ Disassembler.app/Contents/MacOS/hopper -e <binary> -Y <script.py>
  ```
  Use Python scripts inside Hopper to batch-export decompiled pseudocode and symbol tables.
- **Interactive GUI Tracing**:
  ```bash
  open -a "Hopper Disassembler" <binary>
  ```
  Use for visual branch navigation and cross-reference (XRef) inspection when needed.

## 3. Native CLI Toolchain Synergy
Combine REA and Hopper findings with fast system-level inspections:
- **`objdump -x` / `otool -l`**: Inspect PE/Mach-O headers, import tables (DirectDraw, DirectSound, BASS.dll, WinMM, OpenGL), and shared library dependencies.
- **`strings -n 4` / `grep`**: Extract asset file paths, XML/config schema keys, level tables, sound enum identifiers, and debug assertion strings.
- **`hexdump -C` / `xxd`**: Examine proprietary binary file magic headers (e.g., `CURV`, `PAK`, `POP`), endianness, fixed-point scales, and struct alignment.

## 4. PE Resources & RTTI Class Hierarchy Recovery
1. Use REA's `inspect_pe_resources` to extract embedded application icons (`IDI_MAIN_ICON`), version metadata, and manifests.
2. Scan `.rdata` virtual function tables (vtables) and MSVC RTTI type descriptors (`.?AV<ClassName>@@`, e.g., `SexyAppBase`, `Board`, `Bullet`, `WayPointMgr`, `CurveMgr`) to reconstruct the full C++ class inheritance graph.

## 5. Proprietary Format Decoder Reconstruction
Correlate REA pseudocode with Hopper decompilation to write deterministic Python/C++ parsers for:
- Path/trajectory splines and waypoint coordinate tables;
- Level progression XML/binary tables (spawn intervals, speed multipliers, color counts, danger thresholds);
- Sprite atlas coordinates, font kerning tables, and particle emitter definitions.

## Completion Criteria (Phase 1 Done When)
- [ ] All packed binaries are unpacked and inspected via REA `binary_overview` and `inspect_pe_resources`.
- [ ] Class hierarchy (RTTI/vtables) and core state machines are documented.
- [ ] All proprietary binary formats (trajectories, archives, level configs) have verified parser scripts that extract 100% of game levels without error.
- [ ] Complete findings are written to `target/<game_name>/analysis/reverse_engineering_report.md` and Phase 1 items are checked off in `source/<game_name>/MIGRATE.md`.
