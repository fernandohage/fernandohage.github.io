#!/usr/bin/env python3
"""
Script para corrigir referências quebradas de imagem nos arquivos Markdown
"""

import os
import glob
import re

def fix_image_references():
    """Corrige referências a uploads/ nos arquivos Markdown"""
    
    # Lista todos os arquivos Markdown em _pages/pt/
    md_files = glob.glob('_pages/pt/*.md')
    
    for md_file in md_files:
        print(f"Processando {md_file}...")
        
        with open(md_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Conta quantas referências há
        upload_refs = len(re.findall(r'uploads/', content))
        
        if upload_refs > 0:
            print(f"  Encontradas {upload_refs} referências a uploads/")
            
            # Remove todas as referências a uploads/
            # Pattern 1: ![texto](uploads/path) -> remover completamente
            content = re.sub(r'!\[([^\]]*)\]\(uploads/[^)]+\)', '', content)
            
            # Pattern 2: ](uploads/path) -> remover o link
            content = re.sub(r'\]\(uploads/[^)]+\)', ']', content)
            
            # Pattern 3: (uploads/path) -> remover parênteses
            content = re.sub(r'\(uploads/[^)]+\)', '', content)
            
            # Pattern 4: uploads/path sozinho
            content = re.sub(r'uploads/[^\s\)]+', '', content)
            
            # Limpa linhas vazias extras
            content = re.sub(r'\n\s*\n\s*\n', '\n\n', content)
            
            # Salva o arquivo corrigido
            with open(md_file, 'w', encoding='utf-8') as f:
                f.write(content)
            
            print(f"  Arquivo corrigido!")
        else:
            print(f"  Nenhuma referência a uploads/ encontrada")

if __name__ == "__main__":
    fix_image_references()
    print("Correção concluída!")
