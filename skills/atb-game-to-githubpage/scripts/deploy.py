#!/usr/bin/env python3
"""
deploy.py - ATB Game to GitHub Pages Automated Deployer

Scans HTML5 / WebGL / Canvas games, resolves asset symlinks and subpath routing,
generates optimized GitHub Actions workflows, tests staging, updates README,
and deploys to GitHub Pages in one click.
"""

import argparse
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Dict, List, Optional, Tuple

SKILL_DIR = Path(__file__).resolve().parent.parent
TEMPLATES_DIR = SKILL_DIR / "templates"
WORKFLOW_TEMPLATE = TEMPLATES_DIR / "deploy-pages.yml.template"


def run_cmd(cmd: List[str], cwd: Optional[Path] = None) -> Tuple[int, str, str]:
    """Execute a system command and return exit code, stdout, stderr."""
    try:
        proc = subprocess.run(
            cmd,
            cwd=str(cwd) if cwd else None,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            check=False,
        )
        return proc.returncode, proc.stdout.strip(), proc.stderr.strip()
    except Exception as e:
        return 1, "", str(e)


def detect_git_info(repo_dir: Path) -> Dict[str, str]:
    """Inspect git configuration to discover remote URL, owner, repo, and default branch."""
    info = {
        "is_git": False,
        "branch": "main",
        "remote_url": "",
        "owner": "",
        "repo": "",
        "pages_url": "",
    }

    code, branch_out, _ = run_cmd(["git", "branch", "--show-current"], cwd=repo_dir)
    if code == 0 and branch_out:
        info["is_git"] = True
        info["branch"] = branch_out

    code, remote_out, _ = run_cmd(["git", "remote", "get-url", "origin"], cwd=repo_dir)
    if code == 0 and remote_out:
        info["remote_url"] = remote_out
        # Match HTTPS (https://github.com/owner/repo.git) or SSH (git@github.com:owner/repo.git)
        m = re.search(r"github\.com[:/]([^/]+)/([^/\.]+)(?:\.git)?", remote_out)
        if m:
            owner, repo = m.group(1), m.group(2)
            info["owner"] = owner
            info["repo"] = repo
            info["pages_url"] = f"https://{owner}.github.io/{repo}/"

    return info


def find_game_web_dir(target_dir: Path) -> Optional[Path]:
    """Locate the web directory containing the primary game entry (index.html)."""
    # Priority search locations
    candidates = [
        target_dir,
        target_dir / "web",
        target_dir / "dist",
        target_dir / "build",
        target_dir / "public",
        target_dir / "html5",
        target_dir / "game",
    ]

    for c in candidates:
        if (c / "index.html").is_file():
            return c

    # Recursive scan up to depth 3 looking for index.html with game indicators
    for index_path in target_dir.glob("*/web/index.html"):
        return index_path.parent
    for index_path in target_dir.glob("*/*/web/index.html"):
        return index_path.parent
    for index_path in target_dir.glob("*/dist/index.html"):
        return index_path.parent
    for index_path in target_dir.glob("*/index.html"):
        if ".git" not in str(index_path):
            return index_path.parent

    return None


def detect_symlinks_and_assets(web_dir: Path, target_dir: Path) -> List[Dict[str, any]]:
    """Detect symlinks inside web_dir that point outside to assets directories."""
    resolved = []
    if not web_dir.is_dir():
        return resolved

    target_dir = target_dir.resolve()
    web_dir = web_dir.resolve()

    for entry in web_dir.iterdir():
        if entry.is_symlink():
            target = entry.resolve()
            rel_to_repo = None
            try:
                rel_to_repo = target.relative_to(target_dir)
            except ValueError:
                rel_to_repo = None

            resolved.append({
                "symlink_name": entry.name,
                "symlink_path": entry,
                "resolved_target": target,
                "rel_target_in_repo": str(rel_to_repo) if rel_to_repo else None,
            })

    return resolved


def audit_relative_paths(web_dir: Path) -> List[str]:
    """Scan HTML and JS files in web_dir for absolute root paths (/assets/, /style.css, etc.)."""
    warnings = []
    index_file = web_dir / "index.html"
    if not index_file.is_file():
        return warnings

    content = index_file.read_text(errors="ignore")

    # Look for href="/..." or src="/..." (ignoring // protocol-relative or external)
    absolute_refs = re.findall(r'(?:src|href)=["\']/(?!\/)([^"\']+)["\']', content)
    for ref in absolute_refs:
        warnings.append(f"Root-absolute path in index.html: '/{ref}' (should be relative, e.g. '{ref}')")

    return warnings


def generate_build_script(
    web_dir: Path,
    target_dir: Path,
    symlinks: List[Dict[str, any]],
    custom_domain: str = "",
) -> str:
    """Generate shell lines for the 'Assemble site bundle' step in GitHub Actions."""
    lines = ["          mkdir -p _site"]

    rel_web = "."
    try:
        rel_web = str(web_dir.relative_to(target_dir))
    except ValueError:
        rel_web = str(web_dir)

    if rel_web == ".":
        lines.append("          # Copy root static files, excluding repo management directories")
        lines.append("          cp -r * _site/ 2>/dev/null || true")
        lines.append("          rm -rf _site/_site _site/.git _site/.github")
    else:
        lines.append(f"          # Copy web frontend files from {rel_web}")
        lines.append(f"          cp -r {rel_web}/* _site/")

    # Resolve symlinks by replacing them with actual files
    for sym in symlinks:
        s_name = sym["symlink_name"]
        rel_target = sym["rel_target_in_repo"]
        if rel_target:
            lines.append(f"          # Replace symlink '{s_name}' with actual contents from '{rel_target}'")
            lines.append(f"          rm -rf _site/{s_name}")
            lines.append(f"          cp -r {rel_target} _site/{s_name}")

    if custom_domain:
        lines.append(f"          # Write CNAME for custom domain")
        lines.append(f'          echo "{custom_domain}" > _site/CNAME')

    lines.append("          # Ensure Jekyll processing is disabled")
    lines.append("          touch _site/.nojekyll")

    return "\n".join(lines)


def stage_and_verify(
    web_dir: Path,
    target_dir: Path,
    symlinks: List[Dict[str, any]],
    custom_domain: str = "",
    stage_dir: Optional[Path] = None,
) -> Tuple[bool, str]:
    """Locally stage the bundle into a test directory and verify its structure."""
    cleanup_needed = False
    if not stage_dir:
        stage_dir = target_dir / "_stage_verify_tmp"
        cleanup_needed = True

    try:
        if stage_dir.exists():
            shutil.rmtree(stage_dir)
        stage_dir.mkdir(parents=True, exist_ok=True)

        rel_web = "."
        try:
            rel_web = str(web_dir.relative_to(target_dir))
        except ValueError:
            pass

        if rel_web == ".":
            for item in target_dir.iterdir():
                if item.name in [".git", ".github", stage_dir.name, "_site"]:
                    continue
                dest = stage_dir / item.name
                if item.is_dir():
                    shutil.copytree(item, dest)
                else:
                    shutil.copy2(item, dest)
        else:
            for item in web_dir.iterdir():
                dest = stage_dir / item.name
                if item.is_symlink():
                    continue
                elif item.is_dir():
                    shutil.copytree(item, dest)
                else:
                    shutil.copy2(item, dest)

        for sym in symlinks:
            s_name = sym["symlink_name"]
            actual = sym["resolved_target"]
            dest = stage_dir / s_name
            if dest.exists():
                if dest.is_dir():
                    shutil.rmtree(dest)
                else:
                    dest.unlink()
            if actual.is_dir():
                shutil.copytree(actual, dest)
            elif actual.is_file():
                shutil.copy2(actual, dest)

        if custom_domain:
            (stage_dir / "CNAME").write_text(custom_domain)

        (stage_dir / ".nojekyll").touch()

        # Verification checks
        if not (stage_dir / "index.html").is_file():
            return False, "Verification failed: index.html missing in staged output."

        file_count = sum(1 for _ in stage_dir.rglob("*") if _.is_file())
        return True, f"Staging verified successfully! Total files in bundle: {file_count}"
    except Exception as e:
        return False, f"Staging verification error: {str(e)}"
    finally:
        if cleanup_needed and stage_dir.exists():
            shutil.rmtree(stage_dir, ignore_errors=True)


def update_readme(repo_dir: Path, pages_url: str) -> bool:
    """Add or update GitHub Pages live demo link and instructions in README.md."""
    readme_path = repo_dir / "README.md"
    content = ""
    if readme_path.is_file():
        content = readme_path.read_text(errors="ignore")

    if pages_url in content:
        return False  # Already present

    snippet = f"\n🎮 **Live Demo / 在线游玩**: [{pages_url}]({pages_url})\n"

    if content.strip():
        # Insert after the first header if present
        lines = content.splitlines()
        first_header_idx = -1
        for i, line in enumerate(lines):
            if line.startswith("# "):
                first_header_idx = i
                break

        if first_header_idx != -1:
            lines.insert(first_header_idx + 1, snippet)
            new_content = "\n".join(lines)
        else:
            new_content = snippet + "\n" + content
    else:
        new_content = f"# Game\n{snippet}\n"

    readme_path.write_text(new_content)
    return True


def deploy_workflow(
    target_dir: Path,
    web_dir: Optional[Path] = None,
    assets_dir: Optional[Path] = None,
    branch: Optional[str] = None,
    custom_domain: str = "",
    dry_run: bool = False,
    auto_readme: bool = True,
    auto_commit: bool = False,
    auto_push: bool = False,
) -> bool:
    target_dir = target_dir.resolve()
    print(f"\n🎮 [ATB Game to GitHub Pages] Scanning repository: {target_dir}")

    git_info = detect_git_info(target_dir)
    target_branch = branch or git_info["branch"] or "main"
    pages_url = git_info["pages_url"]

    # 1. Detect Web Directory
    if web_dir:
        detected_web = web_dir.resolve()
    else:
        detected_web = find_game_web_dir(target_dir)

    if not detected_web or not (detected_web / "index.html").is_file():
        print("❌ Error: Could not find 'index.html' in repository or subfolders.")
        print("   Please specify the web directory via --web-dir <path>.")
        return False

    rel_web = str(detected_web.relative_to(target_dir)) if detected_web != target_dir else "."
    print(f"   ✔ Found game web entry at: {rel_web}/index.html")

    # 2. Detect Assets and Symlinks
    symlinks = detect_symlinks_and_assets(detected_web, target_dir)
    if symlinks:
        print(f"   ✔ Detected {len(symlinks)} symlinked asset directory/directories:")
        for s in symlinks:
            print(f"     - {s['symlink_name']} -> {s['rel_target_in_repo'] or s['resolved_target']}")

    # 3. Path Audit
    warnings = audit_relative_paths(detected_web)
    if warnings:
        print("   ⚠️  Path Warning(s) detected:")
        for w in warnings:
            print(f"     - {w}")
        print("     Tip: GitHub Pages under subpaths (/<repo>/) requires relative paths for assets/scripts.")

    # 4. Generate Workflow Content
    build_steps = generate_build_script(detected_web, target_dir, symlinks, custom_domain)

    if not WORKFLOW_TEMPLATE.is_file():
        print(f"❌ Error: Missing workflow template at {WORKFLOW_TEMPLATE}")
        return False

    template_str = WORKFLOW_TEMPLATE.read_text()
    workflow_content = template_str.replace("${BRANCH}", target_branch).replace("${BUILD_STEPS}", build_steps)

    workflow_file = target_dir / ".github" / "workflows" / "deploy-pages.yml"

    # 5. Local Staging Verification
    print("   🔍 Testing local staging bundle...")
    ok, msg = stage_and_verify(detected_web, target_dir, symlinks, custom_domain)
    if not ok:
        print(f"   ❌ {msg}")
        return False
    print(f"   ✔ {msg}")

    if dry_run:
        print("\n[DRY RUN] Generated GitHub Actions Workflow:")
        print("-" * 50)
        print(workflow_content)
        print("-" * 50)
        print(f"[DRY RUN] Inferred Pages URL: {pages_url or 'https://<user>.github.io/<repo>/'}")
        print("✔ Dry-run complete. No files were written.")
        return True

    # 6. Write Workflow File
    workflow_file.parent.mkdir(parents=True, exist_ok=True)
    workflow_file.write_text(workflow_content)
    print(f"\n   ✔ Created GitHub Actions workflow: {workflow_file.relative_to(target_dir)}")

    # 7. Update README if requested
    if auto_readme and pages_url:
        updated = update_readme(target_dir, pages_url)
        if updated:
            print(f"   ✔ Updated README.md with live demo link: {pages_url}")

    # 8. Git Commit & Push if requested
    if auto_commit and git_info["is_git"]:
        print("   📦 Creating git commit...")
        run_cmd(["git", "add", ".github/workflows/deploy-pages.yml", "README.md"], cwd=target_dir)
        code, out, err = run_cmd(
            ["git", "commit", "-m", "ci: setup automated GitHub Pages deployment for game"],
            cwd=target_dir,
        )
        if code == 0:
            print(f"   ✔ Git commit created.")
            if auto_push:
                print("   🚀 Pushing to origin...")
                p_code, p_out, p_err = run_cmd(["git", "push", "origin", target_branch], cwd=target_dir)
                if p_code == 0:
                    print(f"   ✔ Successfully pushed to origin/{target_branch}!")
                else:
                    print(f"   ⚠️ Push failed: {p_err}. Please push manually.")
        else:
            print(f"   ℹ Commit skipped or already clean: {err or out}")

    print("\n✨ GitHub Pages deployment configured successfully!")
    print("\nNext Steps:")
    print(" 1. Ensure GitHub Pages is set to GitHub Actions:")
    print("    Go to GitHub repo -> Settings -> Pages -> Build and deployment -> Source: [GitHub Actions]")
    if pages_url:
        print(f" 2. Once the workflow completes, play your game at: {pages_url}")
    return True


def main():
    parser = argparse.ArgumentParser(
        description="Deploy any HTML5/Canvas/WebGL game to GitHub Pages via automated GitHub Actions."
    )
    parser.add_argument("-t", "--target", default=".", help="Target repository directory (default: current directory)")
    parser.add_argument("-w", "--web-dir", default=None, help="Explicit web folder containing index.html")
    parser.add_argument("-a", "--assets-dir", default=None, help="Explicit assets directory")
    parser.add_argument("-b", "--branch", default=None, help="Target git branch (default: current branch or main)")
    parser.add_argument("-d", "--domain", default="", help="Custom domain (optional, writes CNAME)")
    parser.add_argument("--dry-run", action="store_true", help="Simulate and test staging without modifying files")
    parser.add_argument("--no-readme", action="store_true", help="Do not modify README.md")
    parser.add_argument("--commit", action="store_true", help="Automatically commit the generated workflow")
    parser.add_argument("--push", action="store_true", help="Automatically push the commit to origin")

    args = parser.parse_args()

    success = deploy_workflow(
        target_dir=Path(args.target),
        web_dir=Path(args.web_dir) if args.web_dir else None,
        assets_dir=Path(args.assets_dir) if args.assets_dir else None,
        branch=args.branch,
        custom_domain=args.domain,
        dry_run=args.dry_run,
        auto_readme=not args.no_readme,
        auto_commit=args.commit,
        auto_push=args.push,
    )

    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
