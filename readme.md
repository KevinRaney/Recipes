# Lean & Green Recipes

Source for [recipes.raney.co](https://recipes.raney.co), built with
[MkDocs](https://www.mkdocs.org/) + [Material](https://squidfunk.github.io/mkdocs-material/).

## Prerequisites

- **Python 3.12+** (CI uses 3.12 — see [.github/workflows/build_and_deploy.yml](.github/workflows/build_and_deploy.yml)). On macOS: `brew install python`.
- **Node.js** (LTS) — only needed if you want to run the markdown linter locally via `npx`.

## Setup

Homebrew's Python is PEP 668 "externally managed", so install dependencies into a virtual environment:

```sh
python3 -m venv .venv
source .venv/bin/activate
pip install -r mkdocs.requirements
```

The `.venv/` directory is gitignored. Re-activate it in new shells with `source .venv/bin/activate`; leave it with `deactivate`.

## Local Development

With the venv activated:

```sh
mkdocs serve
```

## Lint

CI runs these before building. To run them locally:

```sh
# Markdown
npx markdownlint-cli2 --config .markdownlint.yaml "docs/**/*.md" "readme.md"

# YAML
yamllint -c .yamllint.yaml mkdocs.yml .github/workflows

# Strict build (fails on warnings, broken links, etc.)
mkdocs build --strict
```

## Deploy

`main` deploys automatically via GitHub Actions. To deploy from a workstation:

```sh
mkdocs gh-deploy
```
