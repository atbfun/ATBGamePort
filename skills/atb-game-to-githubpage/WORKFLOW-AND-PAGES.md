# GitHub Actions Workflow and Pages Setup Specification

This document details the GitHub Actions workflow architecture, permissions, concurrency rules, and repository settings configuration for deploying HTML5 games via `atb-game-to-githubpage`.

---

## 1. Zero-Pollution Workflow Architecture

Modern GitHub Pages uses the official Pages deployment actions (`upload-pages-artifact@v3` and `deploy-pages@v4`) instead of orphan `gh-pages` git branches.

### Workflow Template (`.github/workflows/deploy-pages.yml`)
```yaml
name: Deploy Game to GitHub Pages

on:
  push:
    branches:
      - main
  workflow_dispatch:

permissions:
  contents: read
  pages: write
  id-token: write

concurrency:
  group: 'pages'
  cancel-in-progress: false

jobs:
  deploy:
    environment:
      name: github-pages
      url: ${{ steps.deployment.outputs.page_url }}
    runs-on: ubuntu-latest
    steps:
      - name: Checkout repository
        uses: actions/checkout@v4

      - name: Setup Pages
        uses: actions/configure-pages@v5

      - name: Assemble site bundle
        run: |
          mkdir -p _site
          cp -r web/* _site/
          rm -rf _site/assets
          cp -r assets _site/assets
          touch _site/.nojekyll

      - name: Upload artifact
        uses: actions/upload-pages-artifact@v3
        with:
          path: '_site'

      - name: Deploy to GitHub Pages
        id: deployment
        uses: actions/deploy-pages@v4
```

---

## 2. Security & Concurrency Requirements

1. **Permissions**:
   - `contents: read`: Checks out the repository code.
   - `pages: write`: Authorizes artifact upload to the GitHub Pages service.
   - `id-token: write`: Authorizes OIDC token generation for secure deployment authentication.
2. **Concurrency**:
   - `group: 'pages'`: Serializes concurrent deployments to avoid race conditions.
   - `cancel-in-progress: false`: Ensures pending deployments complete rather than aborting mid-flight.

---

## 3. Custom Domain Support

When passing `--domain <custom_domain>` (e.g. `arcade.example.com`), the workflow generates a `CNAME` file in the root of `_site`:
```bash
echo "arcade.example.com" > _site/CNAME
```
Ensure DNS records (CNAME or ALIAS/ANAME) point to `<owner>.github.io`.

---

## 4. GitHub Repository Activation

To complete deployment on GitHub, the repository administrator must configure Pages source once:
1. Navigate to **Settings** -> **Pages** in the target GitHub repository.
2. Under **Build and deployment** -> **Source**, select **GitHub Actions** (not "Deploy from a branch").
3. Trigger a push or run the workflow manually via **Actions** -> **Deploy Game to GitHub Pages** -> **Run workflow**.
