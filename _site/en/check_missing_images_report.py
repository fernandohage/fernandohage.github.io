#!/usr/bin/env python3
"""
Script to check for missing images in markdown files and generate a comprehensive report.
This script analyzes all markdown files in the project and creates a report with:
1. Name of the markdown file
2. Name of the original HTML file from fernandohage.weebly.com directory
3. List of missing images
4. Summary statistics
"""

import os
import re
import glob
from pathlib import Path
import json
from datetime import datetime

class MissingImageChecker:
    def __init__(self, project_root):
        self.project_root = Path(project_root)
        self.assets_images_dir = self.project_root / "assets" / "images"
        self.weebly_dir = self.project_root / "fernandohage.weebly.com"
        self.markdown_dirs = [
            self.project_root / "_pages" / "pt",
            self.project_root / "_pages" / "en",
            self.project_root / "_posts" / "pt",
            self.project_root / "_posts" / "en",
            self.project_root
        ]
        
        # Load existing image files
        self.existing_images = set()
        if self.assets_images_dir.exists():
            for img_file in self.assets_images_dir.glob("*"):
                if img_file.is_file():
                    self.existing_images.add(img_file.name)
        
        # Load HTML files mapping
        self.html_files = set()
        if self.weebly_dir.exists():
            for html_file in self.weebly_dir.glob("*.html"):
                self.html_files.add(html_file.name)
    
    def extract_image_references(self, content):
        """Extract all image references from markdown content"""
        image_patterns = [
            r'!\[.*?\]\((/assets/images/[^)]+)\)',  # ![alt](/assets/images/image.jpg)
            r'!\[.*?\]\((assets/images/[^)]+)\)',   # ![alt](assets/images/image.jpg)
            r'!\[.*?\]\(([^)]*\.(?:jpg|jpeg|png|gif|webp|svg))\)',  # Any image extension
            r'<img[^>]+src=["\']([^"\']*\.(?:jpg|jpeg|png|gif|webp|svg))["\'][^>]*>',  # HTML img tags
        ]
        
        images = []
        for pattern in image_patterns:
            matches = re.findall(pattern, content, re.IGNORECASE)
            images.extend(matches)
        
        return images
    
    def get_corresponding_html_file(self, md_file_path):
        """Get the corresponding HTML file name for a markdown file"""
        md_file = Path(md_file_path)
        
        # Extract the base name without extension
        base_name = md_file.stem
        
        # Handle special cases and naming patterns
        name_mappings = {
            # Direct mappings
            'territorio-da-moda': 'territoriodamoda.html',
            'territoriodamoda-territorio-da-moda': 'territoriodamoda.html',
            'home-pt-moda-cultura-e-arte': 'home-pt.html',
            'bibliotecajoaoaffonso-biblioteca-joao-affonso': 'bibliotecajoaoaffonso.html',
            'caixadecriadores-caixa-de-criadores': 'caixadecriadores.html',
            'blog-clipping-diario-de-bordo': 'blog-clipping.html',
            'artigos-artigos-publicacoes': 'artigos.html',
            'podcasts-podcasts': 'podcasts.html',
            'videos-videos': 'videos.html',
            'curriculo-curriculo-resumido': 'curriculo.html',
            'contato-fernandohage-gmailcomfasoares-faapbr': 'contato.html',
            'meulivro-entre-palavrasdesenhos-e-modas': 'meulivro.html',
            'tese-de-doutorado-imagens-na-historia-do-vestuario': 'tese-de-doutorado.html',
        }
        
        # Check direct mappings first
        if base_name in name_mappings:
            return name_mappings[base_name]
        
        # Handle biblioteca patterns
        if base_name.startswith('livros') and 'biblioteca-joao-affonso' in base_name:
            clean_name = base_name.replace('-biblioteca-joao-affonso', '')
            return f"{clean_name}.html"
        
        if base_name.startswith('revistas') and 'biblioteca-joao-affonso' in base_name:
            clean_name = base_name.replace('-biblioteca-joao-affonso', '')
            return f"{clean_name}.html"
        
        # Default pattern: try the base name
        potential_html = f"{base_name}.html"
        if potential_html in self.html_files:
            return potential_html
        
        # Try without the last part after hyphen
        if '-' in base_name:
            short_name = base_name.split('-')[0]
            potential_html = f"{short_name}.html"
            if potential_html in self.html_files:
                return potential_html
        
        return "NOT_FOUND"
    
    def check_markdown_file(self, md_file_path):
        """Check a single markdown file for missing images"""
        try:
            with open(md_file_path, 'r', encoding='utf-8') as f:
                content = f.read()
        except Exception as e:
            return {
                'file': str(md_file_path),
                'error': f"Failed to read file: {str(e)}",
                'missing_images': [],
                'total_images': 0,
                'html_file': 'ERROR'
            }
        
        # Extract image references
        image_refs = self.extract_image_references(content)
        
        # Check which images are missing
        missing_images = []
        for img_ref in image_refs:
            # Clean the image reference
            img_path = img_ref.strip()
            if img_path.startswith('/assets/images/'):
                img_name = img_path.split('/')[-1]
            elif img_path.startswith('assets/images/'):
                img_name = img_path.split('/')[-1]
            else:
                # Extract filename from any path
                img_name = Path(img_path).name
            
            if img_name not in self.existing_images:
                missing_images.append({
                    'reference': img_ref,
                    'filename': img_name
                })
        
        # Get corresponding HTML file
        html_file = self.get_corresponding_html_file(md_file_path)
        
        return {
            'file': str(md_file_path),
            'relative_path': str(Path(md_file_path).relative_to(self.project_root)),
            'html_file': html_file,
            'missing_images': missing_images,
            'total_images': len(image_refs),
            'missing_count': len(missing_images)
        }
    
    def find_all_markdown_files(self):
        """Find all markdown files in the project"""
        md_files = []
        
        # Check all markdown directories
        for md_dir in self.markdown_dirs:
            if md_dir.exists():
                md_files.extend(md_dir.glob("*.md"))
        
        # Also check for markdown files in subdirectories
        for root, dirs, files in os.walk(self.project_root):
            for file in files:
                if file.endswith('.md'):
                    file_path = Path(root) / file
                    if file_path not in md_files:
                        md_files.append(file_path)
        
        return sorted(md_files)
    
    def generate_report(self):
        """Generate comprehensive missing images report"""
        print("🔍 Analyzing markdown files for missing images...")
        
        md_files = self.find_all_markdown_files()
        print(f"Found {len(md_files)} markdown files to analyze")
        
        results = []
        files_with_missing_images = []
        
        for md_file in md_files:
            result = self.check_markdown_file(md_file)
            results.append(result)
            
            if result['missing_count'] > 0:
                files_with_missing_images.append(result)
            
            print(f"✓ Analyzed: {result['relative_path']} - {result['missing_count']} missing images")
        
        # Generate summary
        total_files = len(results)
        files_with_missing = len(files_with_missing_images)
        total_missing_images = sum(r['missing_count'] for r in results)
        total_images = sum(r['total_images'] for r in results)
        
        # Create detailed report
        report = {
            'timestamp': datetime.now().isoformat(),
            'summary': {
                'total_markdown_files': total_files,
                'files_with_missing_images': files_with_missing,
                'total_images_referenced': total_images,
                'total_missing_images': total_missing_images,
                'percentage_missing': round((total_missing_images / total_images * 100) if total_images > 0 else 0, 2)
            },
            'files_with_missing_images': files_with_missing_images,
            'all_files': results
        }
        
        # Save detailed JSON report
        json_report_path = self.project_root / "missing_images_detailed_report.json"
        with open(json_report_path, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        # Generate human-readable text report
        text_report_path = self.project_root / "missing_images_report.txt"
        with open(text_report_path, 'w', encoding='utf-8') as f:
            f.write("MISSING IMAGES REPORT\n")
            f.write("=" * 50 + "\n\n")
            f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            
            f.write("SUMMARY\n")
            f.write("-" * 20 + "\n")
            f.write(f"Total markdown files analyzed: {total_files}\n")
            f.write(f"Files with missing images: {files_with_missing}\n")
            f.write(f"Total images referenced: {total_images}\n")
            f.write(f"Total missing images: {total_missing_images}\n")
            f.write(f"Percentage missing: {report['summary']['percentage_missing']}%\n\n")
            
            if files_with_missing_images:
                f.write("FILES WITH MISSING IMAGES\n")
                f.write("-" * 30 + "\n\n")
                
                for file_info in files_with_missing_images:
                    f.write(f"📄 Markdown File: {file_info['relative_path']}\n")
                    f.write(f"🌐 HTML File: {file_info['html_file']}\n")
                    f.write(f"📊 Missing: {file_info['missing_count']} of {file_info['total_images']} images\n\n")
                    
                    if file_info['missing_images']:
                        f.write("   Missing Images:\n")
                        for img in file_info['missing_images']:
                            f.write(f"   - {img['filename']} (referenced as: {img['reference']})\n")
                    
                    f.write("\n" + "─" * 60 + "\n\n")
            else:
                f.write("🎉 No missing images found!\n")
        
        # Generate CSV report for easy analysis
        csv_report_path = self.project_root / "missing_images_report.csv"
        with open(csv_report_path, 'w', encoding='utf-8') as f:
            f.write("Markdown File,HTML File,Total Images,Missing Images,Missing Image Names\n")
            for result in results:
                missing_names = "; ".join([img['filename'] for img in result['missing_images']])
                f.write(f'"{result["relative_path"]}","{result["html_file"]}",{result["total_images"]},{result["missing_count"]},"{missing_names}"\n')
        
        print(f"\n📊 ANALYSIS COMPLETE!")
        print(f"Total files analyzed: {total_files}")
        print(f"Files with missing images: {files_with_missing}")
        print(f"Total missing images: {total_missing_images}")
        print(f"\n📋 Reports generated:")
        print(f"  • Text report: {text_report_path}")
        print(f"  • JSON report: {json_report_path}")
        print(f"  • CSV report: {csv_report_path}")
        
        return report

def main():
    """Main function to run the missing images checker"""
    project_root = Path(__file__).parent
    checker = MissingImageChecker(project_root)
    
    print("🎯 Missing Images Report Generator")
    print("=" * 50)
    
    report = checker.generate_report()
    
    # Print summary to console
    print(f"\n📈 SUMMARY:")
    print(f"Missing images percentage: {report['summary']['percentage_missing']}%")
    
    if report['summary']['files_with_missing_images'] > 0:
        print(f"\n⚠️  Files needing attention:")
        for file_info in report['files_with_missing_images'][:5]:  # Show first 5
            print(f"  • {file_info['relative_path']} ({file_info['missing_count']} missing)")
        
        if len(report['files_with_missing_images']) > 5:
            print(f"  ... and {len(report['files_with_missing_images']) - 5} more files")
    
    print(f"\n✅ Check the generated reports for complete details!")

if __name__ == "__main__":
    main()
