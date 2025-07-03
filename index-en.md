---
layout: home
lang: en
permalink_en: /
---

# {{ site.data[site.active_lang].strings.pages.welcome_title }}

## {{ site.data[site.active_lang].strings.pages.welcome_subtitle }}

{{ site.data[site.active_lang].strings.pages.welcome_description }}

## Latest Projects

{% assign posts = site.posts | limit: 5 %}

{% for post in posts %}
* [{{ post.title }}]({{ post.url | relative_url }})
{% endfor %}
