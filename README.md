# Website Migration

Website: fernandohage.weebly.com

This repository contains the full migration of fernandohage.weebly.com to a modern, fully controllable codebase with built‑in internationalization support.

Implemented by: [@jonatasteixeira](http://github.com/jonatasteixeira)

## 🎯 Goals

Extract all content from the original Weebly site

Refactor pages, blog posts and assets into a clean, semantic structure

Rename images and files to meaningful, SEO‑friendly names

Enable internationalization (i18n) for future language additions

Automate every step with reproducible scripts and pipelines

## ⚙️ Migration Workflow

| Step                      | Description                                                             | Tools                                   |
| ------------------------- | ----------------------------------------------------------------------- | --------------------------------------- |
| 1. Content capture        | Cloned the entire site with static assets                               | `HTTrack`                               |
| 2. Raw cleanup & refactor | Removed Weebly‑specific markup, reorganized folders, renamed files      | **Vibecoding** scripts                  |
| 3. AI‑powered rewriting   | Processed all text (English pages included) for clarity and consistency | **GPT‑4.1**, **Claude 3.7**, **Gemini** |
| 4. Automation             | Generated migration scripts, pipelines and layout templates             | **Vibecoding**                          |

## 🗂 Project Structure

```bash
.
├── assets/           # Static files: images, css, documents, social
│   ├── css/
│   ├── documents/
│   ├── images/
│   └── social/
├── _includes/        # HTML partials (header, footer, etc)
├── _layouts/         # Page and post layouts
├── _pages/           # Main page content (Markdown, by language)
│   ├── en/
│   └── pt/
├── _posts/           # Blog posts (by language)
│   ├── en/
│   └── pt/
├── _data/            # i18n translation resources (YAML)
│   ├── en/
│   └── pt/
├── scripts/          # Automation and migration tooling (e.g. .py, .sh)
├── Gemfile           # Jekyll dependencies
├── README.md         # Project documentation
└── ...               # Other config and utility files
```

## 🛠 Tech Stack

HTTrack – static site copier

Vibecoding – automation & layout refactor toolkit

Large Language Models – GPT‑4.1 (OpenAI), Claude 3.7 (Anthropic), Gemini (Google)

## 📌 Notes & Next Steps

Host the migrated site on a modern platform (GitHub Pages, Vercel, Netlify, etc.).

Integrate a localization framework to serve multiple languages.

Add CI/CD to validate links, run accessibility checks and deploy automatically.

## 📧 Contact

Questions or feedback?
jonatas.teixeira@gmail.com