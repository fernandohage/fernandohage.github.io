#!/usr/bin/env python3
"""
Script to list all markdown files that have missing images.
Checks for image tags in markdown files and verifies if the image files exist.
"""

import os
import re
from pathlib import Path

def find_images_in_markdown(file_path):
    """Find all image references in a markdown file."""
    images = []
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Find markdown image syntax: ![alt text](path)
        markdown_images = re.findall(r'!\[.*?\]\(([^)]+)\)', content)
        images.extend(markdown_images)
        
        # Find HTML img tags: <img src="path">
        html_images = re.findall(r'<img[^>]+src=["\']([^"\']+)["\']', content, re.IGNORECASE)
        images.extend(html_images)
        
        return images
    except Exception as e:
        print(f"Error reading {file_path}: {e}")
        return []

def check_image_exists(image_path, base_dir):
    """Check if an image file exists."""
    # Handle different path formats
    if image_path.startswith('http://') or image_path.startswith('https://'):
        # Skip external URLs
        return True
    
    # Handle absolute paths starting with /
    if image_path.startswith('/'):
        image_path = image_path[1:]  # Remove leading slash
    
    # Construct full path
    full_path = Path(base_dir) / image_path
    return full_path.exists()

def find_markdown_files(directory):
    """Find all markdown files in the given directory."""
    markdown_files = []
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.endswith('.md'):
                markdown_files.append(os.path.join(root, file))
    return markdown_files

def main():
    """Main function to find markdown files with missing images."""
    base_dir = '/Users/jonatas.teixeira/weebly_scrapping/new_website'
    
    # Find all markdown files
    markdown_files = find_markdown_files(base_dir)
    
    files_with_missing_images = []
    
    print("Checking markdown files for missing images...")
    print("-" * 60)
    
    for md_file in markdown_files:
        # Get relative path for cleaner output
        rel_path = os.path.relpath(md_file, base_dir)
        
        # Find images in the markdown file
        images = find_images_in_markdown(md_file)
        
        if not images:
            continue  # Skip files with no images
        
        missing_images = []
        for image_path in images:
            if not check_image_exists(image_path, base_dir):
                missing_images.append(image_path)
        
        if missing_images:
            files_with_missing_images.append(rel_path)
            print(f"❌ {rel_path}")
            for missing_img in missing_images:
                print(f"   Missing: {missing_img}")
        else:
            print(f"✅ {rel_path}")
    
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    print(f"Total markdown files checked: {len(markdown_files)}")
    print(f"Files with missing images: {len(files_with_missing_images)}")
    
    if files_with_missing_images:
        print("\nFiles with missing images:")
        for file_path in files_with_missing_images:
            print(f"  {file_path}")
    else:
        print("\n🎉 All images found!")
    
    # Write the list to a file
    output_file = os.path.join(base_dir, 'files_with_missing_images.txt')
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write("# Markdown files with missing images\n")
        f.write(f"# Generated on: {os.popen('date').read().strip()}\n")
        f.write(f"# Total files with missing images: {len(files_with_missing_images)}\n\n")
        
        for file_path in files_with_missing_images:
            f.write(f"{file_path}\n")
    
    print(f"\nList saved to: {output_file}")

if __name__ == "__main__":
    main()
