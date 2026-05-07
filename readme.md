# Lean & Green Recipes

Source for [recipes.raney.co](https://recipes.raney.co), built with
[Zensical](https://zensical.org/).

## Prerequisites

- **Python 3.12+** (CI uses 3.12 — see [.github/workflows/build_and_deploy.yml](.github/workflows/build_and_deploy.yml)). On macOS: `brew install python`.
- **Node.js** (LTS) — only needed if you want to run the markdown linter locally via `npx`.

## Setup

Homebrew's Python is PEP 668 "externally managed", so install dependencies into a virtual environment:

```sh
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

The `.venv/` directory is gitignored. Re-activate it in new shells with `source .venv/bin/activate`; leave it with `deactivate`.

## Local Development

With the venv activated:

```sh
zensical serve
```

## Lint

CI runs these before building. To run them locally:

```sh
# Markdown
npx markdownlint-cli2 --config .markdownlint.yaml "docs/**/*.md" "readme.md"

# YAML
yamllint -c .yamllint.yaml .github/workflows

# Build
zensical build
```

## Deploy

`main` deploys automatically via GitHub Actions, which builds the site with
`zensical build` and publishes the `site/` artifact to GitHub Pages. There is
no `gh-deploy` equivalent in Zensical — push to `main` and let CI publish.

## Configuration

Site config lives in [`zensical.toml`](zensical.toml). Recipe content lives
under [`docs/`](docs/) — files and images stay where they are, and URLs match
the filesystem layout.
