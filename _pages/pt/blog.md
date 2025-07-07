---
layout: page
title: Blog
lang: pt
permalink: /blog/
---

<div class="blog-page">
  <div class="container">
    <header class="page-header">
      <h1>Blog</h1>
      <p class="page-description">Todos os posts sobre moda, cultura e arte</p>
    </header>

    <div class="posts-grid">
      {% assign posts = site.posts | where: "lang", "pt" %}
      {% for post in posts %}
        <article class="post-card">
          <div class="post-content">
            <h2 class="post-title">
              <a href="{{ post.url | relative_url }}">{{ post.title }}</a>
            </h2>
            
            <div class="post-meta">
              <time datetime="{{ post.date | date_to_xmlschema }}">
                {{ post.date | date: "%d de %B de %Y" }}
              </time>
              {% if post.categories %}
                <span class="post-categories">
                  {% for category in post.categories %}
                    <span class="category">{{ category }}</span>
                  {% endfor %}
                </span>
              {% endif %}
            </div>
            
            {% if post.excerpt %}
              <div class="post-excerpt">
                {{ post.excerpt | strip_html | truncate: 150 }}
              </div>
            {% endif %}
            
            <a href="{{ post.url | relative_url }}" class="read-more">
              Ler mais →
            </a>
          </div>
        </article>
      {% endfor %}
    </div>

    {% if posts.size == 0 %}
      <div class="no-posts">
        <p>Nenhum post encontrado.</p>
      </div>
    {% endif %}
  </div>
</div>

<style>
.blog-page {
  padding: 2rem 0;
}

.container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 20px;
}

.page-header {
  text-align: center;
  margin-bottom: 3rem;
}

.page-header h1 {
  font-size: 2.5rem;
  color: #333;
  margin-bottom: 1rem;
}

.page-description {
  font-size: 1.2rem;
  color: #666;
  margin: 0;
}

.posts-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 2rem;
  margin-bottom: 3rem;
}

.post-card {
  background: #fff;
  border-radius: 8px;
  box-shadow: 0 2px 10px rgba(0,0,0,0.1);
  overflow: hidden;
  transition: transform 0.3s ease, box-shadow 0.3s ease;
}

.post-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 5px 20px rgba(0,0,0,0.15);
}

.post-content {
  padding: 1.5rem;
}

.post-title {
  margin: 0 0 1rem 0;
  font-size: 1.3rem;
  line-height: 1.4;
}

.post-title a {
  color: #333;
  text-decoration: none;
  transition: color 0.3s ease;
}

.post-title a:hover {
  color: #007acc;
}

.post-meta {
  display: flex;
  align-items: center;
  gap: 1rem;
  margin-bottom: 1rem;
  font-size: 0.9rem;
  color: #666;
}

.post-categories {
  display: flex;
  gap: 0.5rem;
}

.category {
  background: #f0f0f0;
  padding: 0.2rem 0.5rem;
  border-radius: 12px;
  font-size: 0.8rem;
  color: #555;
}

.post-excerpt {
  color: #555;
  line-height: 1.6;
  margin-bottom: 1.5rem;
}

.read-more {
  display: inline-block;
  color: #007acc;
  text-decoration: none;
  font-weight: 500;
  transition: color 0.3s ease;
}

.read-more:hover {
  color: #005a99;
}

.no-posts {
  text-align: center;
  padding: 3rem;
  color: #666;
}

@media (max-width: 768px) {
  .posts-grid {
    grid-template-columns: 1fr;
    gap: 1.5rem;
  }
  
  .page-header h1 {
    font-size: 2rem;
  }
  
  .post-content {
    padding: 1.25rem;
  }
}
</style> 