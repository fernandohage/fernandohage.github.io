#!/usr/bin/env python3
import os
import re
import shutil
from bs4 import BeautifulSoup
from datetime import datetime
import html
import unicodedata



def clean_filename(filename):
    """Clean filename for Jekyll posts"""
    # Remove HTML entities
    filename = html.unescape(filename)
    # Normalize unicode characters
    filename = unicodedata.normalize('NFKD', filename)
    # Convert to ASCII
    filename = filename.encode('ascii', 'ignore').decode('ascii')
    # Replace spaces and special chars with hyphens
    filename = re.sub(r'[^\w\s-]', '', filename)
    filename = re.sub(r'[-\s]+', '-', filename)
    return filename.lower().strip('-')

def convert_to_title_case(title):
    """Convert title to proper title case"""
    # Remove HTML entities first
    title = html.unescape(title)
    
    # Articles, prepositions, and conjunctions that should be lowercase (except at beginning/end)
    lowercase_words = {
        'a', 'an', 'and', 'as', 'at', 'but', 'by', 'for', 'in', 'nor', 
        'of', 'on', 'or', 'so', 'the', 'to', 'up', 'yet', 'da', 'de', 
        'do', 'das', 'dos', 'na', 'no', 'nas', 'nos', 'em', 'com', 'por', 
        'para', 'sem', 'sob', 'sobre', 'entre', 'contra', 'até', 'desde',
        'o', 'os', 'as', 'um', 'uma', 'uns', 'umas', 'e', 'ou', 'mas',
        'que', 'se', 'quando', 'onde', 'porque', 'pois', 'já', 'ainda',
        'também', 'nem', 'não', 'à', 'ao', 'às', 'aos', 'pela', 'pelo',
        'pelas', 'pelos', 'num', 'numa', 'nuns', 'numas'
    }
    
    # Split title into words
    words = title.split()
    
    if not words:
        return title
    
    # Process each word
    processed_words = []
    for i, word in enumerate(words):
        # Remove punctuation for checking but keep it for final word
        clean_word = re.sub(r'[^\w]', '', word.lower())
        
        # First and last words are always capitalized
        # Also capitalize if it's not in the lowercase_words set
        if i == 0 or i == len(words) - 1 or clean_word not in lowercase_words:
            # Capitalize first letter of the actual word (preserving punctuation)
            if word:
                processed_word = word[0].upper() + word[1:].lower()
            else:
                processed_word = word
        else:
            processed_word = word.lower()
        
        processed_words.append(processed_word)
    
    return ' '.join(processed_words)

def extract_date_from_html(soup):
    """Extract date from HTML content"""
    date_text = soup.find('span', class_='date-text')
    if date_text:
        date_str = date_text.get_text().strip()
        try:
            # Try to parse different date formats
            if '/' in date_str:
                # Format: 6/9/2019
                parts = date_str.split('/')
                if len(parts) == 3:
                    day, month, year = parts
                    return f"{year}-{month.zfill(2)}-{day.zfill(2)}"
        except:
            pass
    return "2025-07-02"  # Default date

def extract_title_from_html(soup):
    """Extract title from HTML content"""
    title_elem = soup.find('h2', class_='blog-title')
    if title_elem:
        title_link = title_elem.find('a')
        if title_link:
            title = title_link.get_text().strip()
            return convert_to_title_case(title)
    
    # Fallback to meta title
    meta_title = soup.find('meta', property='og:title')
    if meta_title:
        title = meta_title.get('content', '').strip()
        return convert_to_title_case(title)
    
    return "Untitled Post"

def extract_content_from_html(soup):
    """Extract main content from HTML"""
    content_div = soup.find('div', class_='blog-content')
    if not content_div:
        return ""
    
    content = []
    
    # Process paragraphs
    paragraphs = content_div.find_all('div', class_='paragraph')
    for p in paragraphs:
        text = p.get_text().strip()
        if text:
            # Clean up HTML entities
            text = html.unescape(text)
            content.append(text)
    
    return '\n\n'.join(content)

def extract_images_from_html(soup, post_title, base_dir):
    """Extract and copy images from HTML"""
    images = []
    image_counter = 1
    
    # Find image gallery
    gallery = soup.find('div', class_='imageGallery')
    if gallery:
        img_tags = gallery.find_all('img', class_='galleryImage')
        for img in img_tags:
            src = img.get('src', '')
            if src and src.startswith('../uploads/'):
                # Create meaningful filename
                clean_title = clean_filename(post_title)
                ext = os.path.splitext(src)[1] or '.jpg'
                new_filename = f"{clean_title}-{image_counter:02d}{ext}"
                
                # Source and destination paths - fix path for uploads
                # Convert '../uploads/...' to 'fernandohage.weebly.com/uploads/...'
                src_relative = src.replace('../uploads', 'fernandohage.weebly.com/uploads')
                src_path = os.path.join(base_dir, src_relative)
                dest_path = os.path.join(base_dir, 'assets', 'images', new_filename)
                
                # Copy image if it exists
                if os.path.exists(src_path):
                    os.makedirs(os.path.dirname(dest_path), exist_ok=True)
                    try:
                        shutil.copy2(src_path, dest_path)
                        images.append(f"/assets/images/{new_filename}")
                        print(f"  Copied image: {new_filename}")
                    except Exception as e:
                        print(f"  Error copying {src_path}: {e}")
                else:
                    print(f"  Image not found: {src_path}")
                
                image_counter += 1
    
    return images

def convert_html_to_markdown(html_file, base_dir):
    """Convert single HTML file to markdown"""
    print(f"Processing: {html_file}")
    
    with open(html_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    soup = BeautifulSoup(content, 'html.parser')
    
    # Extract metadata
    title = extract_title_from_html(soup)
    date = extract_date_from_html(soup)
    content_text = extract_content_from_html(soup)
    
    # Extract and copy images
    images = extract_images_from_html(soup, title, base_dir)
    
    # Create markdown content
    markdown_content = f"""---
layout: post
title: {repr(title)}
date: {date} 15:00:00 +0200
categories: projetos moda
language: pt
author: Fernando Hage
---

# {title}

"""
    
    # Add images if any
    if images:
        markdown_content += "## Galeria de Imagens\n\n"
        for img in images:
            markdown_content += f"![{title}]({img})\n\n"
    
    # Add main content
    if content_text:
        markdown_content += f"{content_text}\n\n"
    
    markdown_content += """---

*Este post faz parte do diário de bordo dos projetos de Fernando Hage.*"""
    
    # Create output filename
    clean_title = clean_filename(title)
    filename = f"{date}-{clean_title}.md"
    
    # Ensure output directory exists
    output_dir = os.path.join(base_dir, '_i18n', 'pt', '_posts')
    os.makedirs(output_dir, exist_ok=True)
    
    # Write markdown file
    output_path = os.path.join(output_dir, filename)
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(markdown_content)
    
    print(f"  Created: {filename}")
    print(f"  Images: {len(images)}")
    return output_path

def main():
    base_dir = "/Users/jonatas.teixeira/weebly_scrapping/new_website"
    blog_dir = os.path.join(base_dir, "fernandohage.weebly.com", "blog-clipping")
    
    # Create assets/images directory
    os.makedirs(os.path.join(base_dir, 'assets', 'images'), exist_ok=True)
    
    # Process all HTML files
    html_files = [f for f in os.listdir(blog_dir) if f.endswith('.html')]
    
    print(f"Found {len(html_files)} HTML files to convert...")
    
    for html_file in sorted(html_files):
        html_path = os.path.join(blog_dir, html_file)
        try:
            convert_html_to_markdown(html_path, base_dir)
        except Exception as e:
            print(f"Error processing {html_file}: {e}")
        print()
    
    print("Conversion completed!")

if __name__ == "__main__":
    main()
