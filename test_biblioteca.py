#!/usr/bin/env python3
import os
import re
import shutil
from bs4 import BeautifulSoup

def test_biblioteca():
    base_dir = "/Users/jonatas.teixeira/weebly_scrapping/new_website"
    html_file = os.path.join(base_dir, "fernandohage.weebly.com", "bibliotecajoaoaffonso.html")
    
    print(f"Processing: {html_file}")
    
    with open(html_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    soup = BeautifulSoup(content, 'html.parser')
    
    # Find all images
    img_tags = soup.find_all('img')
    print(f"Found {len(img_tags)} img tags")
    
    for i, img in enumerate(img_tags[:10]):  # Just first 10
        src = img.get('src', '')
        print(f"{i+1}. Image src: {src}")
        
        if src and src.startswith('uploads/'):
            src_path = os.path.join(base_dir, 'fernandohage.weebly.com', src)
            print(f"   Full path: {src_path}")
            print(f"   Exists: {os.path.exists(src_path)}")
            if os.path.exists(src_path):
                try:
                    file_size = os.path.getsize(src_path)
                    print(f"   Size: {file_size} bytes")
                except:
                    print(f"   Could not get size")

if __name__ == "__main__":
    test_biblioteca()
