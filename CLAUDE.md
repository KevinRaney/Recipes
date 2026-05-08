# CLAUDE.md

Repo for [recipes.raney.co](https://recipes.raney.co), a Lean & Green recipe site built with [Zensical](https://zensical.org).

## Layout

- `docs/` - all site content. Top-level dirs (`appetizers/`, `soups/`, `salads/`, `hearty/<protein>/`, `Tips-and-Hacks/`) become navigation tabs.
- `docs/index.md`, `docs/browse/*.md` - **auto-generated** by `scripts/build_browse.py`. Do not hand-edit.
- `zensical.toml` - site config, theme, and tag-icon mappings.
- `scripts/` - tooling for front matter and browse pages.
- `.github/workflows/build_and_deploy.yml` - lint + `zensical build` + Pages deploy.

## Adding a recipe

1. Drop the new `.md` (and `.png` if applicable) into the right directory: `docs/appetizers/`, `docs/soups/`, `docs/salads/`, `docs/hearty/<Protein>/`, or `docs/Tips-and-Hacks/`.
2. Write the body (title `# H1`, `## Ingredients`, `## Directions`). State servings and per-serving fueling (lean / leaner / leanest, healthy fats, condiments, greens) somewhere near the top so the front matter generator can pick them up.
3. Run both scripts in order:
   ```
   python3 scripts/add_frontmatter.py
   python3 scripts/build_browse.py
   ```
4. Verify with `zensical build` (or `zensical serve`).
5. Commit the recipe, the regenerated `docs/index.md`, and the regenerated `docs/browse/*.md` together.

`add_frontmatter.py` strips and rewrites the `---` block on every recipe, so the script is the source of truth - hand-edited tags or descriptions will be overwritten on the next run. If you need a tag the script doesn't infer, extend the rules in `scripts/add_frontmatter.py`.

## Tag taxonomy

Generated tags fall into these axes:

- **Course** - `appetizer`, `soup`, `salad`, `main`, `tip` (from directory)
- **Protein** - `beef`, `chicken`, `pork`, `seafood`, `turkey`, `vegetarian` (from `hearty/<dir>`)
- **Method** - `air-fryer`, `instant-pot`, `pressure-cooker`, `slow-cooker`, `grill`, `oven`, `stovetop`
- **Cuisine** - `mexican`, `italian`, `asian`, `mediterranean`, `cajun`, `american`
- **Featured ingredient** - `shrimp`, `salmon`, `crab`, `tuna`, `scallops`, `cod`, `cauliflower`, `zucchini`, `spaghetti-squash`, `eggplant`, `tofu`
- **Dish type** - `casserole`, `pizza`, `burgers`, `meatballs`, `stuffed`, `wraps`, `dip`

When adding a new tag, also add an icon in `[project.theme.icon.tag]` in `zensical.toml` (use only icons that ship with Zensical - `material/`, `fontawesome/`, `lucide/`, `octicons/` under `templates/.icons/`).

## Local build

```
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
.venv/bin/zensical serve
```

`zensical build -s` enables strict mode and is what CI runs.
