#!/usr/bin/env python3
"""
Script to fix image references in the biblioteca markdown files.
Updates the specific section names to use the generic biblioteca-joao-affonso image names.
"""

import os
import re
import glob

def fix_image_references():
    # Directory containing the markdown files
    md_dir = "/Users/jonatas.teixeira/weebly_scrapping/new_website/_i18n/pt/_site"
    
    # Find all biblioteca-related markdown files
    biblioteca_files = glob.glob(os.path.join(md_dir, "*biblioteca-joao-affonso.md"))
    
    # Pattern to match image references
    image_pattern = r'!\[([^\]]+)\]\(/assets/images/([^)]+)\)'
    
    # Counter for generic image numbering
    image_counter = 1
    
    for md_file in biblioteca_files:
        print(f"Processing: {md_file}")
        
        with open(md_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Find all image references in this file
        matches = re.findall(image_pattern, content)
        
        # Replace each image reference with the generic biblioteca naming
        for alt_text, image_path in matches:
            # Extract the extension from the original path
            _, ext = os.path.splitext(image_path)
            
            # Create the new image path with generic naming
            new_image_path = f"biblioteca-joao-affonso-{image_counter:02d}{ext}"
            
            # Replace the image reference
            old_ref = f"![{alt_text}](/assets/images/{image_path})"
            new_ref = f"![{alt_text}](/assets/images/{new_image_path})"
            
            content = content.replace(old_ref, new_ref)
            print(f"  Replaced: {image_path} -> {new_image_path}")
            
            image_counter += 1
        
        # Write the updated content back to the file
        with open(md_file, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print(f"  Updated {len(matches)} image references in {os.path.basename(md_file)}")

if __name__ == "__main__":
    fix_image_references()
    print("Image references updated successfully!")
