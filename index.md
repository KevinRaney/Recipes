---
# Feel free to add content and custom Front Matter to this file.
# To modify the layout, see https://jekyllrb.com/docs/themes/#overriding-theme-defaults

layout: home
---
# Recently Added Recipes

{% for recipe in site.recipes %}
  <h2>
    <a href="{{ recipe.url }}">
      {{ recipe.title }}
    </a>
  </h2>
  <p>{{ recipe.date | date_to_string }}</p>
{% endfor %}