#!/usr/bin/env python3
"""Build the curated browse pages from recipe front matter.

Generates:
  docs/index.md            - landing with counts and links into browse/
  docs/browse/index.md     - browse hub
  docs/browse/by-protein.md
  docs/browse/by-method.md
  docs/browse/by-cuisine.md
  docs/browse/by-dish.md

Each browse page groups recipes by tag within its dimension. Run after
adding or renaming recipes (or after running add_frontmatter.py).
"""
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DOCS = ROOT / "docs"
BROWSE = DOCS / "browse"

FRONT_MATTER_RE = re.compile(r"\A---\s*\n(.*?)\n---\s*\n", re.S)
TITLE_RE = re.compile(r'^title:\s*"(.*?)"\s*$', re.M)
TAGS_BLOCK_RE = re.compile(r"^tags:\s*\n((?:\s+-\s+\S+\s*\n)+)", re.M)
TAG_LINE_RE = re.compile(r"^\s+-\s+(\S+)\s*$", re.M)


def load_recipe(path: Path):
    text = path.read_text()
    m = FRONT_MATTER_RE.match(text)
    if not m:
        return None
    fm = m.group(1)
    title_m = TITLE_RE.search(fm)
    if not title_m:
        return None
    tags = []
    tb = TAGS_BLOCK_RE.search(fm + "\n")
    if tb:
        tags = TAG_LINE_RE.findall(tb.group(1))
    return {
        "title": title_m.group(1),
        "tags": set(tags),
        "rel": path.relative_to(DOCS).as_posix(),
    }


def page_url(rel: str) -> str:
    """Convert a docs-relative .md path to the directory URL Zensical emits."""
    return rel[:-3] + "/" if rel.endswith(".md") else rel


def link_from_browse(recipe) -> str:
    """Browse pages live at docs/browse/, so prefix `../` to reach recipes."""
    return f"[{recipe['title']}](../{page_url(recipe['rel'])})"


def by_tag(recipes, tag):
    return sorted(
        (r for r in recipes if tag in r["tags"]),
        key=lambda r: r["title"].lower(),
    )


# Course taxonomy is reflected in the directory structure already, so the
# browse pages focus on the cross-cutting axes (protein, method, etc.).
PROTEINS = [
    ("beef", "Beef"),
    ("chicken", "Chicken"),
    ("turkey", "Turkey"),
    ("seafood", "Seafood"),
    ("pork", "Pork"),
    ("vegetarian", "Vegetarian"),
]
METHODS = [
    ("air-fryer", "Air fryer"),
    ("instant-pot", "Instant Pot"),
    ("pressure-cooker", "Pressure cooker"),
    ("slow-cooker", "Slow cooker / crockpot"),
    ("grill", "Grill"),
    ("oven", "Oven & roasted"),
    ("stovetop", "Skillet & stovetop"),
]
CUISINES = [
    ("mexican", "Mexican"),
    ("italian", "Italian"),
    ("asian", "Asian"),
    ("mediterranean", "Mediterranean / Greek"),
    ("cajun", "Cajun & Creole"),
    ("american", "American comfort"),
]
DISHES = [
    ("casserole", "Casseroles"),
    ("pizza", "Pizzas"),
    ("burgers", "Burgers"),
    ("meatballs", "Meatballs & meatloaf"),
    ("stuffed", "Stuffed"),
    ("wraps", "Wraps"),
    ("dip", "Dips"),
]
COURSE_COUNTS = [
    ("appetizer", "Appetizers", "appetizers/"),
    ("soup", "Soups", "soups/"),
    ("salad", "Salads", "salads/"),
    ("main", "Mains", "hearty/"),
    ("tip", "Tips & Hacks", "Tips-and-Hacks/"),
]


def front_matter(title: str, description: str, tags: list[str]) -> str:
    lines = [
        "---",
        f'title: "{title}"',
        f'description: "{description}"',
        "tags:",
    ]
    lines.extend(f"  - {t}" for t in tags)
    lines.append("hide:")
    lines.append("  - toc")
    lines.append("---")
    lines.append("")
    return "\n".join(lines)


def render_dimension(heading: str, intro: str, taxonomy, recipes) -> str:
    out = [
        f"# {heading}",
        "",
        intro,
        "",
    ]
    for tag, label in taxonomy:
        items = by_tag(recipes, tag)
        if not items:
            continue
        out.append(f"## {label}")
        out.append("")
        out.append(f"_{len(items)} recipe{'s' if len(items) != 1 else ''}_")
        out.append("")
        for r in items:
            out.append(f"- {link_from_browse(r)}")
        out.append("")
    return "\n".join(out).rstrip() + "\n"


def write_page(path: Path, fm: str, body: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(fm + body)


def main() -> None:
    recipes = []
    for md in sorted(DOCS.rglob("*.md")):
        rel = md.relative_to(DOCS)
        if rel.as_posix() == "index.md":
            continue
        if rel.parts and rel.parts[0] == "browse":
            continue
        info = load_recipe(md)
        if info:
            recipes.append(info)

    counts = {
        course: sum(1 for r in recipes if course in r["tags"])
        for course, _, _ in COURSE_COUNTS
    }

    # docs/index.md - short landing
    landing_fm = front_matter(
        "Lean & Green Recipes",
        f"Browse {len(recipes)} Lean & Green recipes by protein, method, cuisine, or dish type.",
        ["overview"],
    )
    landing_body = "# Lean & Green Recipes\n\n"
    landing_body += (
        "Welcome! Every recipe here fits the Lean & Green plan and is tagged "
        "for easy browsing. Use the search at the top, click any tag chip on "
        "a recipe to find similar dishes, or dive into the curated browse "
        "pages below.\n\n"
    )
    landing_body += f"**{len(recipes)} recipes and tips** indexed.\n\n"
    landing_body += "## Browse pages\n\n"
    landing_body += "- [By protein](browse/by-protein/) - Beef, Chicken, Turkey, Seafood, Pork, Vegetarian\n"
    landing_body += "- [By cooking method](browse/by-method/) - Air fryer, Instant Pot, Slow cooker, Grill, Oven, Stovetop\n"
    landing_body += "- [By cuisine](browse/by-cuisine/) - Mexican, Italian, Asian, Mediterranean, Cajun, American\n"
    landing_body += "- [By dish type](browse/by-dish/) - Casseroles, Pizzas, Burgers, Meatballs, Stuffed, Wraps, Dips\n\n"
    landing_body += "## Course\n\n"
    for course, label, url in COURSE_COUNTS:
        if counts[course]:
            landing_body += f"- [{label}]({url}) ({counts[course]})\n"
    write_page(DOCS / "index.md", landing_fm, landing_body)

    # browse/index.md - hub
    hub_fm = front_matter(
        "Browse",
        "Curated indexes of every recipe, grouped by protein, method, cuisine, and dish type.",
        ["overview"],
    )
    hub_body = (
        "# Browse\n\n"
        "Curated indexes of every Lean & Green recipe, grouped four ways:\n\n"
        "- **[By protein](by-protein/)** - what's the main protein?\n"
        "- **[By cooking method](by-method/)** - air fryer, slow cooker, grill, etc.\n"
        "- **[By cuisine](by-cuisine/)** - Mexican, Italian, Asian, Mediterranean, Cajun, American\n"
        "- **[By dish type](by-dish/)** - casseroles, pizzas, burgers, wraps, and more\n"
    )
    write_page(BROWSE / "index.md", hub_fm, hub_body)

    write_page(
        BROWSE / "by-protein.md",
        front_matter(
            "Browse by protein",
            "Lean & Green recipes grouped by main protein: beef, chicken, turkey, seafood, pork, vegetarian.",
            ["overview", "by-protein"],
        ),
        render_dimension(
            "Browse by protein",
            "Recipes grouped by their main protein. Click any tag chip on a recipe page to find similar dishes.",
            PROTEINS,
            recipes,
        ),
    )
    write_page(
        BROWSE / "by-method.md",
        front_matter(
            "Browse by cooking method",
            "Lean & Green recipes grouped by how they're cooked: air fryer, Instant Pot, slow cooker, grill, oven, stovetop.",
            ["overview", "by-method"],
        ),
        render_dimension(
            "Browse by cooking method",
            "Recipes grouped by primary cooking method. Many recipes work multiple ways - listings reflect the method called out in the title or directions.",
            METHODS,
            recipes,
        ),
    )
    write_page(
        BROWSE / "by-cuisine.md",
        front_matter(
            "Browse by cuisine",
            "Lean & Green recipes grouped by cuisine: Mexican, Italian, Asian, Mediterranean, Cajun, American.",
            ["overview", "by-cuisine"],
        ),
        render_dimension(
            "Browse by cuisine",
            "Recipes grouped by cuisine. Tags are derived from titles and may be inexact for fusion dishes.",
            CUISINES,
            recipes,
        ),
    )
    write_page(
        BROWSE / "by-dish.md",
        front_matter(
            "Browse by dish type",
            "Lean & Green recipes grouped by dish style: casseroles, pizzas, burgers, meatballs, stuffed, wraps, dips.",
            ["overview", "by-dish"],
        ),
        render_dimension(
            "Browse by dish type",
            "Recipes grouped by dish style.",
            DISHES,
            recipes,
        ),
    )

    print(
        f"Wrote landing + 5 browse pages "
        f"({len(recipes)} recipes indexed)"
    )


if __name__ == "__main__":
    main()
