---
layout: home
lang: pt
permalink_pt: /
---

# {{ site.data[site.active_lang].strings.pages.welcome_title }}

## {{ site.data[site.active_lang].strings.pages.welcome_subtitle }}

{{ site.data[site.active_lang].strings.pages.welcome_description }}

## Últimos Projetos

{% assign posts = site.posts | limit: 5 %}

{% for post in posts %}
* [{{ post.title }}]({{ post.url | relative_url }})
{% endfor %}