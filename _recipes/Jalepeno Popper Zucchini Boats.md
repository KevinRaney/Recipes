---
layout: post
title: Jalepeño Popper Zucchini Boats
date:   2021-08-01 12:15:00 -0400
is_full_lean_and_green: true
lean_and_green:
 - is_full: true
 - servings: 3
 - lean: 1
 - lean_type: Lean
 - green: 3
 - condiment: 3
 - healthy_fat: 1
categories: Spicy
---
{% for specs in page.lean_and_green%}
{% if specs.servings%}
{% assign serving = specs.servings%}
{% endif %}
{% if specs.lean_type %}
{% assign lean_type = specs.lean_type | capitalize %}
{% endif  %}
{% if specs.lean %}
{% assign lean = specs.lean %}
{% endif  %}
{% if specs.green %}
{% assign green = specs.green %}
{% endif  %}
{% if specs.condiment %}
{% assign condiment = specs.condiment %}
{% endif %}
{% if specs.healthy_fat %}
{% assign healthy_fat = specs.healthy_fat %}
{% endif %}
{% endfor %}


# Nutritional Information

<table>
<tr><td>Servings</td><td>{{serving}}</td></tr>
<tr><td>{{ lean_type }}</td><td>{{lean}}</td></tr>
<tr><td>Greens</td><td>{{green}}</td></tr>
<tr><td>Healthy Fats</td><td>{{healthy_fat}}</td></tr>
<tr><td>Condiments</td><td>{{condiment}}</td></tr>
</table>

{{serving}} serving(s), {{lean}} {{lean_type}}, {{healthy_fat}} healthy fat(s), {{green}} green(s) and {{condiment}} condiment(s). 

# Ingredients
- 4 zucchini, halved lengthwise (about 16 oz 8 greens)
- 1 tbsp. extra-virgin olive oil
- 1/4 tsp Kosher salt
- 1/2 tsp Freshly ground black pepper
- 6 wedges light laughing cow cream cheese, softened
- 5 oz cooked shredded chicken
- 4 oz. shredded low fat Monterey jack , divided
- 1 c shredded 2% cheddar cheese, divided
- 1 ounce extra lean turkey bacon, cooked and crumbled
- 1/2 c jalapeños, seeds removed and diced
- 1/2 tsp. garlic powder

# Directions
1. Preheat oven to 350°.
2. Score zucchini (like you’re dicing an avocado) and scoop out insides, reserving them for later. 
3. Place zucchini halves cut side-up into bottom of 9”-x-13” baking dish and drizzle with oil. 
4. Bake until zucchini turns bright green and is just beginning to soften, 15 minutes.
5. In a large bowl, combine laughing cow, shredded chicken, ½ of each cheese, turkey bacon, jalapeños, and garlic powder. 
6. Season with salt and pepper.
7. Fold in reserved zucchini pieces.
8. Spoon filling into zucchini and top with remaining ½ of each cheese and bake until cheese is melty, 15 minutes.

![Jalepeño Popper Zucchini Boats](/images/Jalepeño Popper Zucchini Boats.jpg)