#!/usr/bin/env python3
"""
Script to verify missing image references in Markdown files
Checks if images referenced in MD files exist in the assets directory
"""

import os
import glob
import re
from pathlib import Path

def extract_image_references(md_file):
    """Extract all image references from a Markdown file"""
    with open(md_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Find all image references: ![alt text](/assets/images/filename.ext)
    image_refs = re.findall(r'!\[[^\]]*\]\((/assets/images/[^)]+)\)', content)
    
    # Also check for HTML img tags: <img src="/assets/images/filename.ext"
    html_img_refs = re.findall(r'<img[^>]+src="(/assets/images/[^"]+)"', content)
    
    return image_refs + html_img_refs

def check_image_exists(image_path):
    """Check if an image file exists in the assets directory"""
    # Remove leading slash and convert to Path
    clean_path = image_path.lstrip('/')
    full_path = Path(clean_path)
    
    return full_path.exists()

def find_original_image_in_weebly(image_filename):
    """Try to find the original image in the weebly directory"""
    weebly_dir = Path('fernandohage.weebly.com')
    if not weebly_dir.exists():
        return None
    
    # Search for images with similar names
    possible_paths = []
    
    # Search in uploads directory
    uploads_dir = weebly_dir / 'uploads'
    if uploads_dir.exists():
        for ext in ['jpg', 'jpeg', 'png', 'gif', 'webp']:
            pattern = f"**/*.{ext}"
            for img_path in uploads_dir.glob(pattern):
                if img_path.name.lower() in image_filename.lower() or image_filename.lower() in img_path.name.lower():
                    possible_paths.append(str(img_path))
    
    # Search in files directory
    files_dir = weebly_dir / 'files'
    if files_dir.exists():
        for ext in ['jpg', 'jpeg', 'png', 'gif', 'webp']:
            pattern = f"**/*.{ext}"
            for img_path in files_dir.glob(pattern):
                if img_path.name.lower() in image_filename.lower() or image_filename.lower() in img_path.name.lower():
                    possible_paths.append(str(img_path))
    
    return possible_paths

def generate_missing_images_report():
    """Generate a report of missing images"""
    print("=" * 60)
    print("MISSING IMAGES REPORT")
    print("=" * 60)
    
    # Find all Markdown files
    md_files = []
    for pattern in ['_pages/**/*.md', '_posts/**/*.md', '*.md']:
        md_files.extend(glob.glob(pattern, recursive=True))
    
    missing_images = {}
    total_images = 0
    missing_count = 0
    
    for md_file in md_files:
        print(f"\nChecking: {md_file}")
        
        image_refs = extract_image_references(md_file)
        if not image_refs:
            print("  No image references found")
            continue
            
        print(f"  Found {len(image_refs)} image references")
        total_images += len(image_refs)
        
        file_missing = []
        for img_ref in image_refs:
            if not check_image_exists(img_ref):
                file_missing.append(img_ref)
                missing_count += 1
                print(f"    ❌ MISSING: {img_ref}")
            else:
                print(f"    ✅ EXISTS: {img_ref}")
        
        if file_missing:
            missing_images[md_file] = file_missing
    
    # Summary report
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    print(f"Total Markdown files checked: {len(md_files)}")
    print(f"Total image references found: {total_images}")
    print(f"Missing images: {missing_count}")
    print(f"Files with missing images: {len(missing_images)}")
    
    if missing_images:
        print("\n" + "=" * 60)
        print("DETAILED MISSING IMAGES REPORT")
        print("=" * 60)
        
        for md_file, missing_imgs in missing_images.items():
            print(f"\n📄 {md_file} ({len(missing_imgs)} missing images)")
            for img in missing_imgs:
                print(f"  ❌ {img}")
                
                # Try to find original in weebly
                img_filename = Path(img).name
                original_paths = find_original_image_in_weebly(img_filename)
                if original_paths:
                    print(f"    🔍 Possible sources in weebly:")
                    for path in original_paths[:3]:  # Show max 3 matches
                        print(f"      - {path}")
                else:
                    print(f"    🔍 No similar image found in weebly directory")
    
    # Check for broken upload references
    print("\n" + "=" * 60)
    print("CHECKING FOR BROKEN UPLOAD REFERENCES")
    print("=" * 60)
    
    broken_refs = {}
    for md_file in md_files:
        with open(md_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Find references to uploads/ that weren't converted
        upload_refs = re.findall(r'uploads/[^)\s]+', content)
        if upload_refs:
            broken_refs[md_file] = upload_refs
    
    if broken_refs:
        print("Found broken upload references:")
        for md_file, refs in broken_refs.items():
            print(f"\n📄 {md_file}")
            for ref in refs:
                print(f"  ⚠️  {ref}")
    else:
        print("No broken upload references found ✅")
    
    # Generate action items
    if missing_images or broken_refs:
        print("\n" + "=" * 60)
        print("RECOMMENDED ACTIONS")
        print("=" * 60)
        
        if missing_images:
            print("1. Missing Images:")
            print("   - Check the original weebly files for these images")
            print("   - Copy them to assets/images/ directory")
            print("   - Ensure proper naming convention")
        
        if broken_refs:
            print("2. Broken Upload References:")
            print("   - Run the fix_image_refs.py script to clean these up")
            print("   - Or manually find and copy the referenced images")
    
    return missing_images, broken_refs

if __name__ == "__main__":
    missing_images, broken_refs = generate_missing_images_report()
    
    # Save detailed report to file
    with open('missing_images_report.txt', 'w', encoding='utf-8') as f:
        f.write("MISSING IMAGES DETAILED REPORT\n")
        f.write("=" * 60 + "\n\n")
        
        if missing_images:
            for md_file, missing_imgs in missing_images.items():
                f.write(f"File: {md_file}\n")
                for img in missing_imgs:
                    f.write(f"  Missing: {img}\n")
                f.write("\n")
        
        if broken_refs:
            f.write("\nBROKEN UPLOAD REFERENCES\n")
            f.write("=" * 30 + "\n")
            for md_file, refs in broken_refs.items():
                f.write(f"File: {md_file}\n")
                for ref in refs:
                    f.write(f"  Broken: {ref}\n")
                f.write("\n")
    
    print(f"\nDetailed report saved to: missing_images_report.txt")