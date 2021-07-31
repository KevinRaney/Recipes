---
layout: page
title: Full Lean & Greens
permalink: /FullLeanAndGreens/
---
{% for recipe in site.recipes %}
  {% if recipe.is_full_lean_and_green == "true" %}
    <h2>
      <a href="{{ recipe.url }}">
        {{ recipe.title }}
      </a>
    </h2>
    <p>{{ recipe.date | date_to_string }}</p>
  {% endif %}
{% endfor %}