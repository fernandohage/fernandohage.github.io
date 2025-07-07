---
layout: page
title: Site Map
lang: en
permalink: /sitemap/
---

<div class="sitemap-page">
  <div class="container">
    <header class="page-header">
      <h1>Site Map</h1>
      <p class="page-description">All site pages organized by category</p>
    </header>

    <div class="pages-grid">
      {% assign pages = site.pages | where: "lang", "en" | sort: "title" %}
      {% for page in pages %}
        {% if page.title and page.url != '/sitemap/' %}
          <article class="page-card">
            <div class="page-content">
              <h2 class="page-title">
                <a href="{{ page.url | relative_url }}">{{ page.title }}</a>
              </h2>
              
              {% if page.description %}
                <div class="page-description">
                  {{ page.description | strip_html | truncate: 120 }}
                </div>
              {% endif %}
              
              <div class="page-meta">
                <span class="page-url">{{ page.url }}</span>
              </div>
              
              <a href="{{ page.url | relative_url }}" class="view-page">
                View page →
              </a>
            </div>
          </article>
        {% endif %}
      {% endfor %}
    </div>

    {% if pages.size == 0 %}
      <div class="no-pages">
        <p>No pages found.</p>
      </div>
    {% endif %}

    <div class="blog-section">
      <h2>Blog Posts</h2>
      <p><a href="{{ '/blog/' | relative_url }}" class="blog-link">View all blog posts →</a></p>
    </div>
  </div>
</div>

<style>
.sitemap-page {
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

.pages-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 2rem;
  margin-bottom: 3rem;
}

.page-card {
  background: #fff;
  border-radius: 8px;
  box-shadow: 0 2px 10px rgba(0,0,0,0.1);
  overflow: hidden;
  transition: transform 0.3s ease, box-shadow 0.3s ease;
}

.page-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 5px 20px rgba(0,0,0,0.15);
}

.page-content {
  padding: 1.5rem;
}

.page-title {
  margin: 0 0 1rem 0;
  font-size: 1.3rem;
  line-height: 1.4;
}

.page-title a {
  color: #333;
  text-decoration: none;
  transition: color 0.3s ease;
}

.page-title a:hover {
  color: #007acc;
}

.page-description {
  color: #555;
  line-height: 1.6;
  margin-bottom: 1rem;
  font-size: 0.9rem;
}

.page-meta {
  margin-bottom: 1.5rem;
  font-size: 0.8rem;
  color: #888;
}

.page-url {
  font-family: monospace;
  background: #f5f5f5;
  padding: 0.2rem 0.5rem;
  border-radius: 3px;
}

.view-page {
  display: inline-block;
  color: #007acc;
  text-decoration: none;
  font-weight: 500;
  transition: color 0.3s ease;
}

.view-page:hover {
  color: #005a99;
}

.blog-section {
  background: #f9f9f9;
  padding: 2rem;
  border-radius: 8px;
  text-align: center;
  margin-top: 3rem;
}

.blog-section h2 {
  margin-bottom: 1rem;
  color: #333;
}

.blog-link {
  color: #007acc;
  text-decoration: none;
  font-weight: 500;
  font-size: 1.1rem;
}

.blog-link:hover {
  color: #005a99;
}

.no-pages {
  text-align: center;
  padding: 3rem;
  color: #666;
}

@media (max-width: 768px) {
  .pages-grid {
    grid-template-columns: 1fr;
    gap: 1.5rem;
  }
  
  .page-header h1 {
    font-size: 2rem;
  }
  
  .page-content {
    padding: 1.25rem;
  }
}
</style> 