#!/usr/bin/env python3
"""Generate Zensical front matter for every recipe under docs/.

Re-runnable: existing `---` front matter is stripped and regenerated so
the script is the single source of truth for tags/description/LeanAndGreen
data, and the rendered nutrition badge between `<!-- LG:BEGIN -->` and
`<!-- LG:END -->` is also stripped and regenerated.
"""
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DOCS = ROOT / "docs"

# Paths that aren't recipes and shouldn't be touched.
SKIP_RELATIVE = {"index.md"}
SKIP_DIRS = {"browse"}

COURSE_FOR_DIR = {
    "appetizers": "appetizer",
    "soups": "soup",
    "salads": "salad",
    "hearty": "main",
    "Tips-and-Hacks": "tip",
}

PROTEIN_FOR_DIR = {
    "Beef": "beef",
    "Chicken": "chicken",
    "Pork": "pork",
    "Seafood": "seafood",
    "Turkey": "turkey",
    "Vegetarian": "vegetarian",
}

INGREDIENT_TAGS = [
    (re.compile(r"\bshrimp\b", re.I), "shrimp"),
    (re.compile(r"\bsalmon\b", re.I), "salmon"),
    (re.compile(r"\bscallop", re.I), "scallops"),
    (re.compile(r"\bcrab\b", re.I), "crab"),
    (re.compile(r"\btuna\b", re.I), "tuna"),
    (re.compile(r"\bcod\b", re.I), "cod"),
    (re.compile(r"\bcauliflower\b", re.I), "cauliflower"),
    (re.compile(r"\bzucchini\b", re.I), "zucchini"),
    (re.compile(r"\bspaghetti[\s-]*squash\b", re.I), "spaghetti-squash"),
    (re.compile(r"\beggplant\b", re.I), "eggplant"),
    (re.compile(r"\btofu\b", re.I), "tofu"),
]

CUISINE_TAGS = [
    (re.compile(r"\b(mexican|enchilada|taco|fajita|barbacoa|carne|chipotle|burrito|huevos|tomatillo|jalape|chile|poblano)\b", re.I), "mexican"),
    (re.compile(r"\b(italian|parmesan|parmigian|alfredo|caprese|bolognese|lasagn|pesto|bruschett|carbonara|cacciatore|piccata|tetrazzini|marinara|mozzarella|ricotta|prosciutto|tuscan)\b", re.I), "italian"),
    (re.compile(r"\b(asian|thai|chinese|teriyaki|kung\s*pao|stir[\s-]?fry|pad\s*thai|orange\s*chicken|mongolian|filipino|adobo|shawarma|spring\s*roll|egg\s*roll|sushi|cashew\s*chicken|peanut\s*sauce|coconut\s*curry)\b", re.I), "asian"),
    (re.compile(r"\b(greek|mediterranean|tzatziki|tabbouleh|feta|kalamata)\b", re.I), "mediterranean"),
    (re.compile(r"\b(cajun|creole|gumbo|jambalaya|po[\s-]?boy)\b", re.I), "cajun"),
    (re.compile(r"\b(buffalo|bbq|barbecue|ranch|philly)\b", re.I), "american"),
]

DISH_TAGS = [
    (re.compile(r"\bcasserole\b", re.I), "casserole"),
    (re.compile(r"\bpizza\b", re.I), "pizza"),
    (re.compile(r"\bstuffed\b", re.I), "stuffed"),
    (re.compile(r"\b(burger|patty|patties)\b", re.I), "burgers"),
    (re.compile(r"\b(meatball|meatloaf)\b", re.I), "meatballs"),
    (re.compile(r"\bwrap(s|ped)?\b", re.I), "wraps"),
    (re.compile(r"\bdip\b", re.I), "dip"),
]

SERVINGS_RES = [
    re.compile(r"makes\s+(\d+)\s+serving", re.I),
    re.compile(r"^\s*(\d+)\s+serving", re.I | re.M),
]
NUM = r"\d+(?:\s+\d+/\d+|\.\d+|/\d+)?"
LEAN_RE = re.compile(rf"({NUM})\s+(leanest|leaner|lean)s?\b", re.I)
HEALTHY_FAT_RE = re.compile(rf"({NUM})\s+healthy\s*fats?", re.I)
CONDIMENT_RE = re.compile(rf"({NUM})\s+condiments?", re.I)
GREEN_RE = re.compile(rf"({NUM})\s+greens?\b", re.I)
SNACK_RE = re.compile(rf"({NUM})\s+(?:optional\s+)?snacks?\b", re.I)
FRONT_MATTER_RE = re.compile(r"\A---\s*\n.*?\n---\s*\n?", re.S)
LG_BLOCK_RE = re.compile(
    r"\n*<!-- LG:BEGIN -->.*?<!-- LG:END -->\n*", re.S
)

LG_KEYS = ("lean", "leaner", "leanest", "healthy_fats", "greens", "condiments", "snack")


def parse_number(s: str):
    s = s.strip()
    total = 0.0
    try:
        for p in s.split():
            if "/" in p:
                a, b = p.split("/")
                total += float(a) / float(b)
            else:
                total += float(p)
        return total
    except Exception:
        return None


def fmt_num(v):
    if v is None:
        return None
    if abs(v - round(v)) < 1e-6:
        return int(round(v))
    return round(v, 2)


def extract_title(content: str, fallback: str) -> str:
    m = re.search(r"^#\s+(.+?)\s*$", content, re.M)
    if m:
        return re.sub(r"\s*[….]+\s*$", "", m.group(1).strip())
    return fallback


def is_tip(path: Path) -> bool:
    parts = path.relative_to(DOCS).parts
    return bool(parts) and parts[0] == "Tips-and-Hacks"


def derive_tags(path: Path, content: str, title: str) -> list[str]:
    tags: list[str] = []
    parts = path.relative_to(DOCS).parts
    top = parts[0] if parts else ""

    course = COURSE_FOR_DIR.get(top)
    if course:
        tags.append(course)

    if top == "hearty" and len(parts) >= 2:
        protein = PROTEIN_FOR_DIR.get(parts[1])
        if protein:
            tags.append(protein)

    if re.search(r"\bair[\s-]?fry", content, re.I):
        tags.append("air-fryer")
    if re.search(r"\binstant\s*pot\b", content, re.I):
        tags.append("instant-pot")
    if re.search(r"\bpressure[\s-]?cook", content, re.I):
        tags.append("pressure-cooker")
    if re.search(r"\b(slow[\s-]?cook|crock[\s-]?pot|crockpot)", content, re.I):
        tags.append("slow-cooker")
    if re.search(r"\bgrill", title, re.I):
        tags.append("grill")
    if re.search(r"\b(bake|baked|roast|roasted|oven)", title, re.I):
        tags.append("oven")
    if re.search(r"\b(skillet|stir[\s-]?fry)", title, re.I):
        tags.append("stovetop")

    if "tip" in tags:
        return tags

    for pat, tag in INGREDIENT_TAGS:
        if (pat.search(title) or pat.search(content)) and tag not in tags:
            tags.append(tag)

    for pat, tag in CUISINE_TAGS:
        if pat.search(title) and tag not in tags:
            tags.append(tag)

    for pat, tag in DISH_TAGS:
        if pat.search(title) and tag not in tags:
            tags.append(tag)

    return tags


def find_summary_region(content: str) -> str:
    candidates = []
    for pat in (r"^##\s+Ingredients", r"^##\s+", r"^- \[ \]", r"^\*\s"):
        m = re.search(pat, content, re.M | re.I)
        if m:
            candidates.append(m.start())
    return content[: min(candidates)] if candidates else content


def extract_fueling(pattern: re.Pattern, summary: str, full: str):
    m = pattern.search(summary)
    if m:
        return m
    matches = list(pattern.finditer(full))
    return matches[-1] if matches else None


def derive_meta(path: Path, content: str) -> dict:
    out: dict = {}
    if is_tip(path):
        return out

    summary = find_summary_region(content)

    for r in SERVINGS_RES:
        m = r.search(summary) or r.search(content)
        if m:
            try:
                out["servings"] = int(m.group(1))
            except ValueError:
                pass
            break

    lg: dict = {k: 0 for k in LG_KEYS}
    lm = extract_fueling(LEAN_RE, summary, content)
    if lm:
        v = fmt_num(parse_number(lm.group(1)))
        if v is not None:
            lg[lm.group(2).lower()] = v
    hm = extract_fueling(HEALTHY_FAT_RE, summary, content)
    if hm:
        v = fmt_num(parse_number(hm.group(1)))
        if v is not None:
            lg["healthy_fats"] = v
    cm = extract_fueling(CONDIMENT_RE, summary, content)
    if cm:
        v = fmt_num(parse_number(cm.group(1)))
        if v is not None:
            lg["condiments"] = v
    gm = extract_fueling(GREEN_RE, summary, content)
    if gm:
        v = fmt_num(parse_number(gm.group(1)))
        if v is not None:
            lg["greens"] = v
    sm = extract_fueling(SNACK_RE, summary, content)
    if sm:
        v = fmt_num(parse_number(sm.group(1)))
        if v is not None:
            lg["snack"] = v

    tier_sum = sum(float(lg[k]) for k in ("lean", "leaner", "leanest"))
    if not (abs(tier_sum) < 1e-6 or abs(tier_sum - 1) < 1e-6):
        rel = path.relative_to(ROOT).as_posix()
        print(
            f"WARN {rel}: lean+leaner+leanest = {tier_sum} (expected 0 or 1)",
            file=sys.stderr,
        )

    out["LeanAndGreen"] = lg
    return out


def build_description(title: str, tags: list[str]) -> str:
    course = next((t for t in tags if t in ("appetizer", "soup", "salad", "main", "tip")), None)
    protein = next((t for t in tags if t in ("beef", "chicken", "pork", "seafood", "turkey", "vegetarian")), None)
    method = next((t for t in tags if t in ("air-fryer", "instant-pot", "slow-cooker", "pressure-cooker", "grill", "oven", "stovetop")), None)
    cuisine = next((t for t in tags if t in ("mexican", "italian", "asian", "mediterranean", "cajun", "american")), None)

    if course == "tip":
        return f"{title} - Lean & Green tip and plan hack."

    lead = ""
    if cuisine:
        lead = ("American" if cuisine == "american" else cuisine.capitalize()) + " "

    descriptor = f"Lean & Green {course}" if course else "Lean & Green recipe"
    if protein and protein != "vegetarian":
        descriptor += f" featuring {protein}"
    elif protein == "vegetarian":
        descriptor = "Vegetarian " + descriptor.lower()

    if method:
        descriptor += " " + {
            "air-fryer": "made in the air fryer",
            "instant-pot": "made in the Instant Pot",
            "slow-cooker": "made in the slow cooker",
            "pressure-cooker": "made in the pressure cooker",
            "grill": "off the grill",
            "oven": "from the oven",
            "stovetop": "on the stovetop",
        }[method]

    return f"{title} - {lead}{descriptor}."


def yaml_str(s: str) -> str:
    return json.dumps(s, ensure_ascii=False)


COLOR_RANK = {"green": 0, "yellow": 1, "red": 2}


def _fmt_value(v) -> str:
    if isinstance(v, float) and abs(v - round(v)) < 1e-6:
        return str(int(round(v)))
    return str(v)


def evaluate_lean_and_green(lg: dict) -> list[dict]:
    """Return per-row dicts with label, value, color, and tooltip."""
    lean = float(lg.get("lean", 0))
    leaner = float(lg.get("leaner", 0))
    leanest = float(lg.get("leanest", 0))
    healthy_fats = float(lg.get("healthy_fats", 0))
    greens = float(lg.get("greens", 0))
    condiments = float(lg.get("condiments", 0))
    snack = float(lg.get("snack", 0))

    tier_sum = lean + leaner + leanest
    if abs(tier_sum - 1) < 1e-6:
        tier_color = "green"
        tier_tip = "Lean + leaner + leanest = 1 portion (meets)."
    elif tier_sum > 1 + 1e-6:
        tier_color = "red"
        tier_tip = f"Lean + leaner + leanest = {_fmt_value(tier_sum)} (over 1 portion)."
    elif tier_sum > 1e-6:
        tier_color = "yellow"
        tier_tip = f"Lean + leaner + leanest = {_fmt_value(tier_sum)} (under 1 portion)."
    else:
        tier_color = "green"
        tier_tip = "No protein declared."

    fats_target = 2 * leanest + 1 * leaner + 0 * lean
    if abs(healthy_fats - fats_target) < 1e-6:
        fats_color = "green"
    elif healthy_fats < fats_target:
        fats_color = "yellow"
    else:
        fats_color = "red"
    fats_tip = (
        f"Healthy fats target for this tier mix is {_fmt_value(fats_target)} "
        f"(leanest 2 / leaner 1 / lean 0)."
    )

    if abs(greens - 3) < 1e-6:
        greens_color = "green"
    elif greens < 3:
        greens_color = "yellow"
    else:
        greens_color = "red"
    greens_tip = "Lean & Green calls for 3 servings of non-starchy vegetables."

    if condiments <= 3 + 1e-6:
        condiments_color = "green"
    else:
        condiments_color = "red"
    condiments_tip = "Up to 3 condiment servings per day."

    if snack <= 1 + 1e-6:
        snack_color = "green"
    else:
        snack_color = "red"
    snack_tip = "Up to 1 optional snack per day."

    return [
        {"key": "lean", "label": "Lean", "value": _fmt_value(lean),
         "color": tier_color, "title": tier_tip},
        {"key": "leaner", "label": "Leaner", "value": _fmt_value(leaner),
         "color": tier_color, "title": tier_tip},
        {"key": "leanest", "label": "Leanest", "value": _fmt_value(leanest),
         "color": tier_color, "title": tier_tip},
        {"key": "healthy_fats", "label": "Healthy fats",
         "value": _fmt_value(healthy_fats), "color": fats_color,
         "title": fats_tip},
        {"key": "greens", "label": "Greens", "value": _fmt_value(greens),
         "color": greens_color, "title": greens_tip},
        {"key": "condiments", "label": "Condiments",
         "value": _fmt_value(condiments), "color": condiments_color,
         "title": condiments_tip},
        {"key": "snack", "label": "Snack", "value": _fmt_value(snack),
         "color": snack_color, "title": snack_tip},
    ]


def render_lean_and_green_badge(meta: dict) -> str:
    """Render the per-recipe Lean & Green nutrition badge as HTML."""
    lg = meta.get("LeanAndGreen") or {k: 0 for k in LG_KEYS}
    rows = evaluate_lean_and_green(lg)
    overall = max((r["color"] for r in rows), key=lambda c: COLOR_RANK[c])

    lines = [
        "<!-- LG:BEGIN -->",
        f'<aside class="lg-badge lg-badge--{overall}" '
        'aria-label="Lean and Green nutrition summary">',
        '  <header class="lg-badge__title">Lean &amp; Green</header>',
        '  <ul class="lg-badge__rows">',
    ]
    for r in rows:
        lines.append(
            f'    <li class="lg-badge__row lg-badge__row--{r["color"]}" '
            f'title="{r["title"]}">'
            f'<span class="lg-badge__label">{r["label"]}</span>'
            f'<span class="lg-badge__value">{r["value"]}</span>'
            '<span class="lg-badge__swatch" aria-hidden="true"></span>'
            '</li>'
        )
    lines.append("  </ul>")
    lines.append("</aside>")
    lines.append("<!-- LG:END -->")
    return "\n".join(lines)


def inject_badge(body: str, badge: str) -> str:
    """Insert the badge block immediately after the first H1 in the body."""
    body = LG_BLOCK_RE.sub("\n\n", body, count=1)
    m = re.search(r"^#\s+.+?$", body, re.M)
    if not m:
        return body
    end = m.end()
    after = body[end:]
    after = re.sub(r"^\s*\n+", "\n\n", after, count=1)
    if not after.startswith("\n\n"):
        after = "\n\n" + after.lstrip("\n")
    return body[:end] + "\n\n" + badge + after


def to_front_matter(title, description, tags, meta) -> str:
    lines = [
        "---",
        f"title: {yaml_str(title)}",
        f"description: {yaml_str(description)}",
    ]
    if tags:
        lines.append("tags:")
        lines.extend(f"  - {t}" for t in tags)
    if "servings" in meta:
        lines.append(f"servings: {meta['servings']}")
    if "LeanAndGreen" in meta:
        lines.append("LeanAndGreen:")
        for k in LG_KEYS:
            lines.append(f"  {k}: {meta['LeanAndGreen'][k]}")
    lines.append("---")
    lines.append("")
    return "\n".join(lines)


def should_skip(path: Path) -> bool:
    rel = path.relative_to(DOCS)
    if rel.as_posix() in SKIP_RELATIVE:
        return True
    return bool(rel.parts) and rel.parts[0] in SKIP_DIRS


def process(path: Path) -> None:
    content = path.read_text()
    content = FRONT_MATTER_RE.sub("", content, count=1)
    content = LG_BLOCK_RE.sub("\n\n", content, count=1)
    fallback = path.stem.replace("-", " ").replace("_", " ")
    title = extract_title(content, fallback)
    tags = derive_tags(path, content, title)
    meta = derive_meta(path, content)
    description = build_description(title, tags)
    if not is_tip(path) and "LeanAndGreen" in meta:
        badge = render_lean_and_green_badge(meta)
        content = inject_badge(content, badge)
    path.write_text(to_front_matter(title, description, tags, meta) + content)


def main() -> None:
    changed = 0
    for md in sorted(DOCS.rglob("*.md")):
        if should_skip(md):
            continue
        try:
            process(md)
            changed += 1
        except Exception as e:
            print(f"ERROR {md}: {e}")
    print(f"Front matter regenerated for {changed} files")


if __name__ == "__main__":
    main()
