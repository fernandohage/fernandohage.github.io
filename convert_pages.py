#!/usr/bin/env python3
import os
import re
import shutil
from bs4 import BeautifulSoup
from datetime import datetime
import html
import unicodedata
from urllib.parse import urljoin, urlparse

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

def extract_title_from_html(soup, filename):
    """Extract title from HTML content"""
    # Try to get title from the page title
    title_elem = soup.find('title')
    if title_elem:
        title = title_elem.get_text().strip()
        # Remove site name suffix
        title = re.sub(r' - FERNANDO HAGE$', '', title)
        title = re.sub(r' - Fernando Hage.*$', '', title)
        title = html.unescape(title)
        return convert_to_title_case(title)
    
    # Fallback to banner heading
    banner = soup.find('div', id='banner')
    if banner:
        heading = banner.find(['h1', 'h2', 'h3'])
        if heading:
            title = heading.get_text().strip()
            title = html.unescape(title)
            return convert_to_title_case(title)
    
    # Fallback to filename
    title = os.path.splitext(filename)[0].replace('-', ' ')
    return convert_to_title_case(title)

def process_images(soup, post_title, base_dir, output_dir):
    """Extract and copy images from HTML"""
    images = []
    image_counter = 1
    
    # Find all images - both regular img tags and gallery images
    img_tags = soup.find_all('img')
    for img in img_tags:
        src = img.get('src', '')
        if not src:
            continue
        
        # Skip external images and small icons
        if src.startswith('http') and 'fernandohage.weebly.com' not in src:
            continue
        if 'icon' in src.lower() or 'logo' in src.lower():
            continue
        if src.endswith('.svg'):
            continue
        
        # Clean source path
        if src.startswith('./'):
            src = src[2:]
        elif src.startswith('/'):
            src = src[1:]
        
        # Handle different source formats
        if src.startswith('uploads/'):
            src_path = os.path.join(base_dir, 'fernandohage.weebly.com', src)
        elif not src.startswith('fernandohage.weebly.com'):
            src_path = os.path.join(base_dir, 'fernandohage.weebly.com', src)
        else:
            src_path = os.path.join(base_dir, src)
        
        # Skip if file doesn't exist
        if not os.path.exists(src_path):
            print(f"  Image not found: {src_path}")
            continue
        
        # Skip very small images (likely icons)
        try:
            file_size = os.path.getsize(src_path)
            if file_size < 1000:  # Skip files smaller than 1KB
                continue
        except:
            continue
        
        # Create meaningful filename
        clean_title = clean_filename(post_title)
        ext = os.path.splitext(src)[1] or '.jpg'
        new_filename = f"{clean_title}-{image_counter:02d}{ext}"
        
        # Destination path
        dest_path = os.path.join(base_dir, 'assets', 'images', new_filename)
        
        # Copy image
        os.makedirs(os.path.dirname(dest_path), exist_ok=True)
        try:
            shutil.copy2(src_path, dest_path)
            images.append(f"/assets/images/{new_filename}")
            print(f"  Copied image: {new_filename}")
            
            # Update img src in soup
            img['src'] = f"/assets/images/{new_filename}"
            
        except Exception as e:
            print(f"  Error copying {src_path}: {e}")
        
        image_counter += 1
    
    return images

def convert_tables_to_markdown(soup):
    """Convert HTML tables to markdown format"""
    tables = soup.find_all('table')
    for table in tables:
        markdown_table = []
        
        # Process header
        header_row = table.find('tr')
        if header_row:
            headers = [th.get_text().strip() for th in header_row.find_all(['th', 'td'])]
            if headers:
                markdown_table.append('| ' + ' | '.join(headers) + ' |')
                markdown_table.append('| ' + ' | '.join(['---'] * len(headers)) + ' |')
        
        # Process body rows
        rows = table.find_all('tr')[1:] if header_row else table.find_all('tr')
        for row in rows:
            cells = [td.get_text().strip() for td in row.find_all(['td', 'th'])]
            if cells:
                markdown_table.append('| ' + ' | '.join(cells) + ' |')
        
        # Replace table with markdown
        if markdown_table:
            table_markdown = '\n'.join(markdown_table)
            table.replace_with(BeautifulSoup(table_markdown, 'html.parser'))

def process_links(soup, base_dir):
    """Process internal links to reference correct markdown files"""
    links = soup.find_all('a', href=True)
    for link in links:
        href = link['href']
        
        # Skip external links
        if href.startswith('http') and 'fernandohage.weebly.com' not in href:
            continue
        
        # Skip anchors and special links
        if href.startswith('#') or href.startswith('mailto:') or href.startswith('tel:'):
            continue
        
        # Convert .html links to .md references
        if href.endswith('.html'):
            # Extract filename without extension
            filename = os.path.basename(href).replace('.html', '')
            # Convert to markdown reference
            link['href'] = f"{filename}.md"

def extract_content_from_html(soup):
    """Extract main content from HTML"""
    # Remove script and style elements
    for script in soup(["script", "style"]):
        script.decompose()
    
    # Find main content area
    content_div = soup.find('div', id='wsite-content')
    if not content_div:
        content_div = soup.find('div', id='content')
    if not content_div:
        content_div = soup.find('body')
    
    if not content_div:
        return ""
    
    # Process tables first
    convert_tables_to_markdown(content_div)
    
    # Convert to text while preserving some structure
    content_text = []
    
    # Process paragraphs and divs
    for element in content_div.find_all(['p', 'div', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'ul', 'ol', 'li', 'blockquote']):
        if element.name in ['h1', 'h2', 'h3', 'h4', 'h5', 'h6']:
            level = int(element.name[1])
            text = element.get_text().strip()
            if text:
                content_text.append(f"{'#' * level} {text}")
        elif element.name in ['ul', 'ol']:
            # Skip, will be handled by li elements
            continue
        elif element.name == 'li':
            text = element.get_text().strip()
            if text:
                content_text.append(f"- {text}")
        elif element.name == 'blockquote':
            text = element.get_text().strip()
            if text:
                content_text.append(f"> {text}")
        else:
            text = element.get_text().strip()
            if text and len(text) > 10:  # Skip very short divs
                content_text.append(text)
    
    return '\n\n'.join(content_text)

def convert_html_to_markdown(html_file, base_dir, output_dir):
    """Convert single HTML file to markdown"""
    filename = os.path.basename(html_file)
    print(f"Processing: {filename}")
    
    with open(html_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    soup = BeautifulSoup(content, 'html.parser')
    
    # Extract metadata
    title = extract_title_from_html(soup, filename)
    
    # Process images and update soup
    images = process_images(soup, title, base_dir, output_dir)
    
    # Process internal links
    process_links(soup, base_dir)
    
    # Extract main content
    content_text = extract_content_from_html(soup)
    
    # Create markdown content
    markdown_content = f"""---
layout: page
title: {repr(title)}
permalink: /{clean_filename(title)}/
language: pt
---

# {title}

"""
    
    # Add main content
    if content_text:
        markdown_content += f"{content_text}\n\n"
    
    # Add images section if any
    if images:
        markdown_content += "## Galeria de Imagens\n\n"
        for img in images:
            markdown_content += f"![{title}]({img})\n\n"
    
    # Create output filename
    clean_title = clean_filename(title)
    output_filename = f"{clean_title}.md"
    
    # Ensure output directory exists
    os.makedirs(output_dir, exist_ok=True)
    
    # Write markdown file
    output_path = os.path.join(output_dir, output_filename)
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(markdown_content)
    
    print(f"  Created: {output_filename}")
    print(f"  Images: {len(images)}")
    return output_path

def main():
    base_dir = "/Users/jonatas.teixeira/weebly_scrapping/new_website"
    html_dir = os.path.join(base_dir, "fernandohage.weebly.com")
    output_dir = os.path.join(base_dir, "_i18n", "pt", "_site")
    
    # Create output directory
    os.makedirs(output_dir, exist_ok=True)
    os.makedirs(os.path.join(base_dir, 'assets', 'images'), exist_ok=True)
    
    # Process all HTML files in the root directory
    html_files = [f for f in os.listdir(html_dir) if f.endswith('.html')]
    
    print(f"Found {len(html_files)} HTML files to convert...")
    
    for html_file in sorted(html_files):
        html_path = os.path.join(html_dir, html_file)
        try:
            convert_html_to_markdown(html_path, base_dir, output_dir)
        except Exception as e:
            print(f"Error processing {html_file}: {e}")
        print()
    
    print("Conversion completed!")

if __name__ == "__main__":
    main()
