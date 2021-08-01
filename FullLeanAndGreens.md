---
layout: page
title: Full Lean & Greens
permalink: /FullLeanAndGreens/
---
Here are all of the recipes that count as Full Lean & Green meals.
# Full Lean & Green's
<ul>
{% assign recipes = site.recipes | sort: "title" %}
{% for recipe in recipes %}
{% if recipe.is_full_lean_and_green %}
<li><a href="{{ recipe.url }}">{{ recipe.title }}</a></li>
{% endif %}
{% endfor %}
</ul>