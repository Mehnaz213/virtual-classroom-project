#!/usr/bin/env python3
"""Convert markdown files to PDF"""

import sys
from pathlib import Path

try:
    from markdown_pdf import MarkdownPdf, Section
except ImportError:
    print("Installing markdown-pdf...")
    import subprocess
    subprocess.check_call([sys.executable, "-m", "pip", "install", "markdown-pdf"])
    from markdown_pdf import MarkdownPdf, Section

def convert_md_to_pdf(md_file, pdf_file):
    """Convert a markdown file to PDF"""
    print(f"Converting {md_file} to {pdf_file}...")
    
    md_path = Path(md_file)
    if not md_path.exists():
        print(f"Error: {md_file} not found")
        return False
    
    try:
        pdf = MarkdownPdf()
        pdf.add_section(Section(md_path.read_text(encoding='utf-8')))
        pdf.save(pdf_file)
        print(f"✓ Successfully created {pdf_file}")
        return True
    except Exception as e:
        print(f"Error converting {md_file}: {e}")
        return False

if __name__ == "__main__":
    # Convert both documentation files
    files = [
        ("DATASET_DOCUMENTATION.md", "DATASET_DOCUMENTATION.pdf"),
        ("DATASET_USAGE_SUMMARY.md", "DATASET_USAGE_SUMMARY.pdf"),
    ]
    
    success_count = 0
    for md_file, pdf_file in files:
        if convert_md_to_pdf(md_file, pdf_file):
            success_count += 1
    
    print(f"\n{success_count}/{len(files)} files converted successfully")
