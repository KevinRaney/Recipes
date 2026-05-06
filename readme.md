# Lean & Green Recipes

Source for [recipes.raney.co](https://recipes.raney.co), built with
[MkDocs](https://www.mkdocs.org/) + [Material](https://squidfunk.github.io/mkdocs-material/).

## Setup

```sh
pip install -r mkdocs.requirements
```

## Local Development

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
