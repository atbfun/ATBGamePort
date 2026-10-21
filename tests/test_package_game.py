#!/usr/bin/env python3
"""
Unit and Integration Tests for atb-game-package packaging engine.
"""

import importlib.util
import json
import os
import shutil
import sys
import tempfile
import unittest
import zipfile
from pathlib import Path

# Dynamically import package-game.py from skills/atb-game-package/scripts/
SCRIPT_PATH = Path(__file__).resolve().parent.parent / "skills" / "atb-game-package" / "scripts" / "package-game.py"


def load_package_module():
    if not SCRIPT_PATH.is_file():
        raise ImportError(f"Cannot find packaging script at {SCRIPT_PATH}")
    spec = importlib.util.spec_from_file_location("package_game", SCRIPT_PATH)
    mod = importlib.util.module_from_spec(spec)
    sys.modules["package_game"] = mod
    spec.loader.exec_module(mod)
    return mod


VERIFY_SCRIPT_PATH = Path(__file__).resolve().parent.parent / "skills" / "atb-game-package" / "scripts" / "verify-package.py"


def load_verify_module():
    if not VERIFY_SCRIPT_PATH.is_file():
        raise ImportError(f"Cannot find verification script at {VERIFY_SCRIPT_PATH}")
    spec = importlib.util.spec_from_file_location("verify_package", VERIFY_SCRIPT_PATH)
    mod = importlib.util.module_from_spec(spec)
    sys.modules["verify_package"] = mod
    spec.loader.exec_module(mod)
    return mod


class TestPackageGame(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory(prefix="test_pkg_")
        self.test_root = Path(self.temp_dir.name).resolve()

        # Build mock game structure matching target/<game>/
        # target/mockgame/
        #   assets/
        #     images/ball.png
        #     sounds/ping.mp3
        #     data/levels.json
        #   web/
        #     index.html
        #     style.css
        #     game.js
        #     assets -> ../assets (symlink)
        self.game_dir = self.test_root / "target" / "mockgame"
        self.assets_dir = self.game_dir / "assets"
        self.web_dir = self.game_dir / "web"

        (self.assets_dir / "images").mkdir(parents=True, exist_ok=True)
        (self.assets_dir / "sounds").mkdir(parents=True, exist_ok=True)
        (self.assets_dir / "data").mkdir(parents=True, exist_ok=True)
        self.web_dir.mkdir(parents=True, exist_ok=True)

        # 1x1 transparent PNG bytes
        self.png_bytes = (
            b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x06"
            b"\x00\x00\x00\x1f\x15c4\x00\x00\x00\rIDATx\x9cc\xf8\xff\xff?\x00\x05\xfe\x02\xfe"
            b"\xdc\xccY\xe7\x00\x00\x00\x00IEND\xaeB`\x82"
        )
        (self.assets_dir / "images" / "ball.png").write_bytes(self.png_bytes)
        (self.assets_dir / "sounds" / "ping.mp3").write_bytes(b"MOCK_MP3_AUDIO_DATA_FOR_TEST")
        (self.assets_dir / "data" / "levels.json").write_text(json.dumps({"level": 1, "title": "Mock Level"}), encoding="utf-8")

        # Create symlink web/assets -> ../assets
        os.symlink("../assets", self.web_dir / "assets")

        (self.web_dir / "style.css").write_text(
            "body { background: #000; } .ball { background-image: url('assets/images/ball.png'); }",
            encoding="utf-8",
        )
        (self.web_dir / "game.js").write_text(
            "console.log('Game loaded'); fetch('assets/data/levels.json'); const a = new Audio('assets/sounds/ping.mp3');",
            encoding="utf-8",
        )
        (self.web_dir / "index.html").write_text(
            """<!DOCTYPE html>
<html>
<head>
  <meta charset="utf-8">
  <title>Mock Game</title>
  <link rel="stylesheet" href="style.css">
</head>
<body>
  <div id="game-root">
    <img src="assets/images/ball.png" alt="ball" id="ball-img">
  </div>
  <script src="game.js"></script>
</body>
</html>""",
            encoding="utf-8",
        )

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_normalize_asset_key(self):
        mod = load_package_module()
        self.assertEqual(mod.normalize_asset_key("assets/images/ball.png?v=1.2#part"), "assets/images/ball.png")
        self.assertEqual(mod.normalize_asset_key("./assets/images/ball.png"), "assets/images/ball.png")
        self.assertEqual(mod.normalize_asset_key("../assets/images/ball.png"), "assets/images/ball.png")
        self.assertEqual(mod.normalize_asset_key("../../assets/images/ball.png"), "assets/images/ball.png")
        self.assertEqual(mod.normalize_asset_key("/assets/images/ball.png"), "assets/images/ball.png")

    def test_package_game_end_to_end(self):
        mod = load_package_module()
        layout = mod.resolve_game_layout(self.game_dir)
        self.assertEqual(layout.game_name, "mockgame")
        self.assertEqual(layout.entrypoint, self.web_dir / "index.html")

        out_dist = self.game_dir / "dist"
        res = mod.package_game(
            input_dir=self.game_dir,
            out_dir=out_dist,
            game_name="mockgame",
            mode="all",
        )

        standalone_html = res["standalone_html"]
        portable_dir = res["portable_dir"]
        release_zip = res["release_zip"]

        # 1. Assert Standalone HTML exists and inlines resources
        self.assertTrue(standalone_html.is_file())
        html_content = standalone_html.read_text(encoding="utf-8")
        self.assertIn("window.__ATB_VFS__", html_content)
        self.assertIn("assets/images/ball.png", html_content)
        self.assertIn("assets/sounds/ping.mp3", html_content)
        self.assertIn("assets/data/levels.json", html_content)
        self.assertIn("data:image/png;base64,", html_content)
        self.assertIn("console.log('Game loaded')", html_content)
        # Verify VFS Shim function hooks exist
        self.assertIn("window.fetch", html_content)
        self.assertIn("XMLHttpRequest", html_content)
        self.assertIn("Audio", html_content)

        # 2. Assert Portable Bundle exists and has dereferenced real files
        self.assertTrue(portable_dir.is_dir())
        portable_assets = portable_dir / "assets"
        self.assertTrue(portable_assets.is_dir())
        self.assertFalse(portable_assets.is_symlink())
        self.assertTrue((portable_assets / "images" / "ball.png").is_file())
        self.assertTrue((portable_dir / "Play-macOS.command").is_file())
        self.assertTrue((portable_dir / "Play-Windows.bat").is_file())
        self.assertTrue((portable_dir / "README-PLAY.txt").is_file())

        # Check executable permission on macOS launcher
        macos_stat = os.stat(portable_dir / "Play-macOS.command")
        self.assertTrue(bool(macos_stat.st_mode & 0o111), "Play-macOS.command must be executable")

        # 3. Assert Release ZIP contains standalone html, portable dir, and preserves 0755
        self.assertTrue(release_zip.is_file())
        with zipfile.ZipFile(release_zip, "r") as zf:
            namelist = zf.namelist()
            self.assertTrue(any("standalone.html" in name for name in namelist))
            self.assertTrue(any("Play-macOS.command" in name for name in namelist))
            self.assertTrue(any("Play-Windows.bat" in name for name in namelist))

            macos_info = [z for z in zf.infolist() if z.filename.endswith("Play-macOS.command")][0]
            # External attr holds unix permissions in high 16 bits
            perm = (macos_info.external_attr >> 16) & 0o777
            self.assertTrue(bool(perm & 0o111), f"Expected executable permission in zip, got octal: {oct(perm)}")

    def test_verify_package_helpers(self):
        vmod = load_verify_module()
        self.assertTrue(hasattr(vmod, "verify_portable_bundle"))
        self.assertTrue(hasattr(vmod, "verify_release_zip"))
        self.assertTrue(hasattr(vmod, "compute_png_colored_ratio"))

        # Test on packaged game fixture
        pmod = load_package_module()
        layout = pmod.resolve_game_layout(self.game_dir)
        dist_dir = self.game_dir / "dist"
        res = pmod.package_game(self.game_dir, out_dir=dist_dir)

        p_issues = vmod.verify_portable_bundle(res["portable_dir"])
        self.assertEqual(p_issues, [], f"Portable bundle issues: {p_issues}")

        z_issues = vmod.verify_release_zip(res["release_zip"])
        self.assertEqual(z_issues, [], f"Release zip issues: {z_issues}")


if __name__ == "__main__":
    unittest.main()
