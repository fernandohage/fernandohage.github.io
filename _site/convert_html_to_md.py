#!/usr/bin/env python3
"""
Script para converter arquivos HTML do Weebly para Markdown
"""

import os
import re
import shutil
from pathlib import Path
from urllib.parse import urljoin, urlparse
from bs4 import BeautifulSoup
import html2text
import unicodedata

def slugify(text):
    """Convert text to a slug suitable for filenames"""
    # Remove HTML tags if any
    text = re.sub(r'<[^>]+>', '', text)
    # Normalize unicode characters
    text = unicodedata.normalize('NFKD', text)
    # Convert to lowercase
    text = text.lower()
    # Replace spaces with hyphens
    text = re.sub(r'[\s_]+', '-', text)
    # Remove non-alphanumeric characters except hyphens
    text = re.sub(r'[^a-z0-9-]', '', text)
    # Remove multiple consecutive hyphens
    text = re.sub(r'-+', '-', text)
    # Remove leading/trailing hyphens
    text = text.strip('-')
    return text

def title_case(text):
    """Convert text to Title Case"""
    # Handle common Portuguese articles and prepositions
    minor_words = ['a', 'o', 'as', 'os', 'da', 'do', 'das', 'dos', 'de', 'e', 'em', 'na', 'no', 'nas', 'nos', 'para', 'por', 'com', 'sem']
    
    words = text.split()
    result = []
    
    for i, word in enumerate(words):
        # Always capitalize first and last word
        if i == 0 or i == len(words) - 1:
            result.append(word.capitalize())
        # Don't capitalize minor words unless they're the first or last
        elif word.lower() in minor_words:
            result.append(word.lower())
        else:
            result.append(word.capitalize())
    
    return ' '.join(result)

def extract_content_from_html(html_content):
    """Extract main content from HTML"""
    soup = BeautifulSoup(html_content, 'html.parser')
    
    # Try to find the main content area
    content_div = soup.find('div', {'id': 'wsite-content'})
    if not content_div:
        # Try alternative selectors
        content_div = soup.find('div', {'class': 'wsite-content'})
    if not content_div:
        content_div = soup.find('main')
    if not content_div:
        content_div = soup.find('div', {'id': 'content'})
    
    if content_div:
        return content_div
    
    # If no specific content area found, return the body
    return soup.find('body')

def get_page_title(soup):
    """Extract page title from HTML"""
    # Try to get title from h1, h2, or title tag
    title_elem = soup.find('h1')
    if not title_elem:
        title_elem = soup.find('h2')
    if not title_elem:
        title_elem = soup.find('title')
    
    if title_elem:
        title = title_elem.get_text().strip()
        # Remove site name from title
        title = re.sub(r'\s*-\s*FERNANDO HAGE\s*', '', title)
        return title_case(title)
    
    return "Sem Título"

def convert_html_to_markdown(html_file, output_dir, assets_dir):
    """Convert a single HTML file to Markdown"""
    
    print(f"Processing {html_file}...")
    
    # Read HTML file
    with open(html_file, 'r', encoding='utf-8') as f:
        html_content = f.read()
    
    soup = BeautifulSoup(html_content, 'html.parser')
    
    # Get page title
    page_title = get_page_title(soup)
    
    # Create filename from original HTML filename to avoid duplicates
    original_filename = Path(html_file).stem
    filename = slugify(f"{original_filename}-{page_title}")
    if not filename:
        filename = slugify(original_filename)
    
    # Extract main content
    content_div = extract_content_from_html(html_content)
    
    if not content_div:
        print(f"No content found in {html_file}")
        return
    
    # Process images
    images = content_div.find_all('img')
    image_counter = 1
    
    for img in images:
        src = img.get('src')
        if src:
            # Handle relative URLs
            if src.startswith('uploads/') or src.startswith('files/'):
                # Copy image to assets directory
                source_path = Path(html_file).parent / src
                if source_path.exists():
                    # Create new filename
                    ext = Path(src).suffix or '.jpg'
                    new_filename = f"{filename}-{image_counter:02d}{ext}"
                    dest_path = assets_dir / new_filename
                    
                    # Copy file
                    try:
                        shutil.copy2(source_path, dest_path)
                        print(f"  Copied image: {new_filename}")
                    except Exception as e:
                        print(f"  Error copying {src}: {e}")
                    
                    # Update img src - remove the link wrapper and fix path
                    img['src'] = f"/assets/images/{new_filename}"
                    
                    image_counter += 1
    
    # Fix links in content - remove broken upload links
    for link in content_div.find_all('a'):
        href = link.get('href')
        if href and href.startswith('uploads/'):
            # Remove the link but keep the image
            if link.find('img'):
                # Replace link with just the image
                img = link.find('img')
                link.replace_with(img)
            else:
                # Remove broken link
                link.unwrap()
    
    # Convert to markdown
    h = html2text.HTML2Text()
    h.ignore_links = False
    h.ignore_images = False
    h.body_width = 0
    h.ignore_emphasis = False
    
    markdown_content = h.handle(str(content_div))
    
    # Clean up markdown - remove broken links
    import re
    markdown_content = re.sub(r'\[!\[\]\(/assets/images/[^\]]+\)\]\(uploads/[^)]+\)', lambda m: m.group(0).split('](')[0] + ')', markdown_content)
    
    # Create front matter
    front_matter = f"""---
layout: page
title: "{page_title}"
permalink: /{slugify(page_title)}/
lang: pt
---

"""
    
    # Write markdown file
    output_file = output_dir / f"{filename}.md"
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(front_matter + markdown_content)
    
    print(f"Created {output_file}")

def main():
    """Main function to process all HTML files"""
    
    # Setup directories
    html_dir = Path('fernandohage.weebly.com')
    output_dir = Path('_pages/pt')
    assets_dir = Path('assets/images')
    
    # Create directories if they don't exist
    output_dir.mkdir(parents=True, exist_ok=True)
    assets_dir.mkdir(parents=True, exist_ok=True)
    
    # Get all HTML files
    html_files = list(html_dir.glob('*.html'))
    
    print(f"Found {len(html_files)} HTML files to process")
    
    for html_file in html_files:
        try:
            convert_html_to_markdown(html_file, output_dir, assets_dir)
        except Exception as e:
            print(f"Error processing {html_file}: {e}")
    
    print("Conversion complete!")

if __name__ == "__main__":
    main()
