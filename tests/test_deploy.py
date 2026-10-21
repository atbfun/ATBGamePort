#!/usr/bin/env python3
"""
Unit and Integration Tests for atb-game-to-githubpage deploy engine.
"""

import os
import shutil
import sys
import tempfile
import unittest
from pathlib import Path

# Add scripts directory to path
SCRIPTS_DIR = Path(__file__).resolve().parent.parent / "skills" / "atb-game-to-githubpage" / "scripts"
sys.path.insert(0, str(SCRIPTS_DIR))

from deploy import (
    find_game_web_dir,
    detect_symlinks_and_assets,
    audit_relative_paths,
    generate_build_script,
    stage_and_verify,
)


class TestGameDeployer(unittest.TestCase):
    def setUp(self):
        self.test_dir = Path(tempfile.mkdtemp(prefix="test_game_deploy_")).resolve()

    def tearDown(self):
        if self.test_dir.exists():
            shutil.rmtree(self.test_dir, ignore_errors=True)

    def test_find_web_dir_in_root(self):
        (self.test_dir / "index.html").write_text("<!doctype html><html><body><canvas></canvas></body></html>")
        detected = find_game_web_dir(self.test_dir)
        self.assertEqual(detected, self.test_dir)

    def test_find_web_dir_in_subdirectory(self):
        sub_web = self.test_dir / "kingdomrush" / "web"
        sub_web.mkdir(parents=True)
        (sub_web / "index.html").write_text("<!doctype html><html><body><canvas></canvas></body></html>")
        detected = find_game_web_dir(self.test_dir)
        self.assertEqual(detected, sub_web)

    def test_detect_symlinks_and_assets(self):
        sub_web = self.test_dir / "web"
        sub_assets = self.test_dir / "assets"
        sub_web.mkdir()
        sub_assets.mkdir()
        (sub_assets / "sprite.png").write_text("dummy")

        symlink_path = sub_web / "assets"
        os.symlink(sub_assets, symlink_path)

        symlinks = detect_symlinks_and_assets(sub_web, self.test_dir)
        self.assertEqual(len(symlinks), 1)
        self.assertEqual(symlinks[0]["symlink_name"], "assets")
        self.assertEqual(symlinks[0]["rel_target_in_repo"], "assets")

    def test_audit_absolute_paths(self):
        sub_web = self.test_dir / "web"
        sub_web.mkdir()
        bad_html = sub_web / "index.html"
        bad_html.write_text('<script src="/assets/game.js"></script><link href="style.css">')

        warnings = audit_relative_paths(sub_web)
        self.assertEqual(len(warnings), 1)
        self.assertIn("Root-absolute path in index.html: '/assets/game.js'", warnings[0])

    def test_staging_and_verification(self):
        sub_web = self.test_dir / "web"
        sub_assets = self.test_dir / "assets"
        sub_web.mkdir()
        sub_assets.mkdir()

        (sub_web / "index.html").write_text("<html><body></body></html>")
        (sub_assets / "data.json").write_text('{"ok": true}')

        symlink_path = sub_web / "assets"
        os.symlink(sub_assets, symlink_path)

        symlinks = detect_symlinks_and_assets(sub_web, self.test_dir)
        ok, msg = stage_and_verify(sub_web, self.test_dir, symlinks)
        self.assertTrue(ok)
        self.assertIn("Staging verified successfully", msg)


if __name__ == "__main__":
    unittest.main()
