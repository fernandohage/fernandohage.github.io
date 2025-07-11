#!/usr/bin/env python3
"""
Enhanced script to complete image migration from original HTML files to markdown files.
This version uses a more intelligent approach to map images:
1. First tries to match exact image names from HTML file
2. Maps them sequentially to the expected markdown image names
3. Falls back to fuzzy matching if needed
"""

import os
import re
import shutil
from pathlib import Path
from urllib.parse import unquote
import html

def get_original_file_from_markdown(md_file_path):
    """Extract the original_file path from markdown front matter."""
    try:
        with open(md_file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Find original_file in front matter
        match = re.search(r'^original_file:\s*(.+)$', content, re.MULTILINE)
        if match:
            return match.group(1).strip()
        return None
    except Exception as e:
        print(f"Error reading markdown file {md_file_path}: {e}")
        return None

def find_images_in_markdown(md_file_path):
    """Find all image references in a markdown file."""
    images = []
    try:
        with open(md_file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Find markdown image syntax: ![alt text](path)
        markdown_images = re.findall(r'!\[.*?\]\(([^)]+)\)', content)
        images.extend(markdown_images)
        
        # Find HTML img tags: <img src="path">
        html_images = re.findall(r'<img[^>]+src=["\']([^"\']+)["\']', content, re.IGNORECASE)
        images.extend(html_images)
        
        return images
    except Exception as e:
        print(f"Error reading markdown file {md_file_path}: {e}")
        return []

def find_images_in_html(html_file_path):
    """Find all image references in an HTML file."""
    images = []
    try:
        with open(html_file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Find og:image meta tags (these are usually the main content images)
        og_images = re.findall(r'<meta\s+property=["\']og:image["\']\s+content=["\']([^"\']+)["\']', content, re.IGNORECASE)
        images.extend(og_images)
        
        # Find regular img tags
        img_tags = re.findall(r'<img[^>]+src=["\']([^"\']+)["\']', content, re.IGNORECASE)
        images.extend(img_tags)
        
        # Find background images in style attributes
        bg_images = re.findall(r'background-image:\s*url\(["\']?([^"\')]+)["\']?\)', content, re.IGNORECASE)
        images.extend(bg_images)
        
        # Clean up the image paths
        cleaned_images = []
        for img in images:
            # Remove HTML entities
            img = html.unescape(img)
            # Remove URL encoding
            img = unquote(img)
            # Remove query parameters
            img = img.split('?')[0]
            # Skip external URLs
            if not (img.startswith('http://') or img.startswith('https://')):
                cleaned_images.append(img)
        
        return cleaned_images
    except Exception as e:
        print(f"Error reading HTML file {html_file_path}: {e}")
        return []

def find_image_files_in_directory(directory):
    """Find all image files in a directory."""
    image_extensions = {'.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp', '.svg'}
    image_files = []
    
    try:
        for root, dirs, files in os.walk(directory):
            for file in files:
                if any(file.lower().endswith(ext) for ext in image_extensions):
                    image_files.append(os.path.join(root, file))
        return image_files
    except Exception as e:
        print(f"Error scanning directory {directory}: {e}")
        return []

def normalize_image_name(img_path):
    """Normalize image name for comparison."""
    # Get just the filename
    filename = os.path.basename(img_path)
    # Remove common suffixes and prefixes
    filename = re.sub(r'_orig$', '', filename.split('.')[0])
    filename = re.sub(r'_\d+$', '', filename)
    filename = re.sub(r'-\d+$', '', filename)
    # Convert to lowercase and remove special characters for comparison
    filename = re.sub(r'[^a-z0-9]', '', filename.lower())
    return filename

def extract_keywords_from_markdown_filename(md_file):
    """Extract keywords from markdown filename for matching."""
    basename = os.path.basename(md_file)
    # Remove date prefix and .md extension
    name = re.sub(r'^\d{4}-\d{2}-\d{2}-', '', basename)
    name = re.sub(r'\.md$', '', name)
    # Split by dashes and get keywords
    keywords = name.split('-')
    return [kw.lower() for kw in keywords if len(kw) > 2]  # Only words longer than 2 chars

def map_html_images_to_markdown_images(html_images, missing_images, source_dir):
    """Map HTML images to markdown images using sequential and fuzzy matching."""
    mappings = []
    
    # First, find all existing image files based on HTML paths
    available_images = []
    for html_img in html_images:
        # Convert HTML path to filesystem path
        if html_img.startswith('../'):
            potential_path = os.path.join(source_dir, html_img[3:])  # Remove ../
        else:
            potential_path = os.path.join(source_dir, html_img.lstrip('/'))
        
        if os.path.exists(potential_path):
            available_images.append((html_img, potential_path))
    
    print(f"      Found {len(available_images)} available images from HTML")
    
    # Create sequential mapping: first available image -> first missing image, etc.
    for i, missing_img in enumerate(missing_images):
        if i < len(available_images):
            html_img, source_path = available_images[i]
            mappings.append((missing_img, html_img, source_path))
            print(f"      Mapping: {missing_img} <- {html_img}")
        else:
            print(f"      No source image available for: {missing_img}")
    
    return mappings

def copy_image(source_path, target_path):
    """Copy an image file from source to target location."""
    try:
        # Create target directory if it doesn't exist
        os.makedirs(os.path.dirname(target_path), exist_ok=True)
        
        # Copy the file
        shutil.copy2(source_path, target_path)
        return True
    except Exception as e:
        print(f"Error copying {source_path} to {target_path}: {e}")
        return False

def process_markdown_file(md_file_path, base_dir):
    """Process a single markdown file and copy its missing images."""
    print(f"\nProcessing: {os.path.relpath(md_file_path, base_dir)}")
    
    # Get the original HTML file path
    original_file = get_original_file_from_markdown(md_file_path)
    if not original_file:
        print("  ❌ No original_file found in front matter")
        return 0
    
    # Construct the full path to the original HTML file
    html_file_path = os.path.join(base_dir, original_file)
    if not os.path.exists(html_file_path):
        print(f"  ❌ Original HTML file not found: {html_file_path}")
        return 0
    
    print(f"  📄 Original file: {original_file}")
    
    # Find missing images in markdown
    md_images = find_images_in_markdown(md_file_path)
    missing_images = []
    
    for img in md_images:
        # Convert to absolute path for checking
        if img.startswith('/'):
            img_path = os.path.join(base_dir, img[1:])
        else:
            img_path = os.path.join(os.path.dirname(md_file_path), img)
        
        if not os.path.exists(img_path):
            missing_images.append(img)
    
    if not missing_images:
        print("  ✅ No missing images")
        return 0
    
    print(f"  🔍 Found {len(missing_images)} missing images")
    
    # Find images in the original HTML file
    html_images = find_images_in_html(html_file_path)
    if not html_images:
        print("  ❌ No images found in original HTML file")
        return 0
    
    print(f"  📸 Found {len(html_images)} images in HTML file")
    
    # Source directory for images (where the uploads are)
    source_dir = os.path.join(base_dir, "fernandohage.weebly.com")
    
    # Create mappings between HTML images and markdown images
    mappings = map_html_images_to_markdown_images(html_images, missing_images, source_dir)
    
    copied_count = 0
    
    for missing_img, html_img, source_path in mappings:
        # Determine target path
        if missing_img.startswith('/'):
            target_path = os.path.join(base_dir, missing_img[1:])
        else:
            target_path = os.path.join(base_dir, missing_img)
        
        print(f"      📁 Copying {os.path.basename(source_path)} to: {os.path.relpath(target_path, base_dir)}")
        
        if copy_image(source_path, target_path):
            copied_count += 1
            print(f"      ✅ Copied successfully")
        else:
            print(f"      ❌ Copy failed")
    
    return copied_count

def main():
    """Main function to process all markdown files with missing images."""
    base_dir = '/Users/jonatas.teixeira/weebly_scrapping/new_website'
    missing_files_list = os.path.join(base_dir, 'files_with_missing_images.txt')
    
    if not os.path.exists(missing_files_list):
        print(f"Error: {missing_files_list} not found. Run list_files_with_missing_images.py first.")
        return
    
    # Read the list of files with missing images
    markdown_files = []
    with open(missing_files_list, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#'):
                markdown_files.append(line)
    
    print(f"Processing {len(markdown_files)} markdown files with missing images...")
    print("=" * 70)
    
    total_copied = 0
    processed_files = 0
    
    for md_file_rel in markdown_files:
        md_file_path = os.path.join(base_dir, md_file_rel)
        
        if os.path.exists(md_file_path):
            copied = process_markdown_file(md_file_path, base_dir)
            total_copied += copied
            processed_files += 1
        else:
            print(f"\n❌ File not found: {md_file_rel}")
    
    print("\n" + "=" * 70)
    print("MIGRATION SUMMARY")
    print("=" * 70)
    print(f"Files processed: {processed_files}")
    print(f"Images copied: {total_copied}")
    
    if total_copied > 0:
        print(f"\n🎉 Successfully copied {total_copied} images!")
        print("You can now run list_files_with_missing_images.py again to check remaining missing images.")
    else:
        print("\n⚠️  No images were copied. Check the original HTML files and image paths.")

if __name__ == "__main__":
    main()
