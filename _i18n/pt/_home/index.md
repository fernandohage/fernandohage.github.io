# {% t pages.welcome_title %}

## {% t pages.welcome_subtitle %}

{% t pages.welcome_description %}

## {% t pages.latest_posts %}

{% assign posts = site.posts | where: 'language', 'pt' %}
{% for post in posts limit:10 %}

* * [{{ post.title }}](/{{ post.language }}{{ post.url }})

{% endfor %}
