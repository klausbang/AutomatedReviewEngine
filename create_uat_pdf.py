#!/usr/bin/env python3
"""
UAT Checklist PDF Converter
Converts the UAT Quick Checklist from Markdown to PDF format
"""

import markdown
from weasyprint import HTML, CSS
from weasyprint.text.fonts import FontConfiguration
import os
from pathlib import Path

def convert_markdown_to_pdf():
    """Convert the UAT checklist from Markdown to PDF"""
    
    # File paths
    base_dir = Path(__file__).parent
    md_file = base_dir / "docs" / "uat_quick_checklist.md"
    pdf_file = base_dir / "docs" / "UAT_Quick_Checklist_v1.0.0.pdf"
    
    print(f"Converting {md_file} to PDF...")
    
    # Read the Markdown file
    with open(md_file, 'r', encoding='utf-8') as f:
        md_content = f.read()
    
    # Convert Markdown to HTML
    html_content = markdown.markdown(
        md_content,
        extensions=['extra', 'codehilite', 'toc']
    )
    
    # Custom CSS for professional PDF formatting
    css_content = """
    @page {
        size: A4;
        margin: 2cm;
        @bottom-center {
            content: "UAT Quick Checklist - Automated Review Engine v1.0.0 - Page " counter(page);
            font-size: 10px;
            color: #666;
        }
    }
    
    body {
        font-family: 'Arial', sans-serif;
        font-size: 11px;
        line-height: 1.4;
        color: #333;
        max-width: none;
    }
    
    h1 {
        color: #2c3e50;
        font-size: 18px;
        border-bottom: 2px solid #3498db;
        padding-bottom: 10px;
        margin-bottom: 20px;
        page-break-before: avoid;
    }
    
    h2 {
        color: #34495e;
        font-size: 14px;
        margin-top: 25px;
        margin-bottom: 15px;
        page-break-after: avoid;
    }
    
    h3 {
        color: #2c3e50;
        font-size: 12px;
        margin-top: 20px;
        margin-bottom: 10px;
        page-break-after: avoid;
    }
    
    hr {
        border: none;
        border-top: 1px solid #bdc3c7;
        margin: 20px 0;
    }
    
    .checkbox-line {
        margin: 5px 0;
        padding: 2px 0;
    }
    
    code {
        background-color: #f8f9fa;
        padding: 2px 4px;
        border-radius: 3px;
        font-family: 'Courier New', monospace;
        font-size: 10px;
    }
    
    ul, ol {
        margin: 10px 0;
        padding-left: 20px;
    }
    
    li {
        margin: 3px 0;
    }
    
    table {
        width: 100%;
        border-collapse: collapse;
        margin: 15px 0;
        font-size: 10px;
    }
    
    th, td {
        border: 1px solid #ddd;
        padding: 8px;
        text-align: left;
    }
    
    th {
        background-color: #f2f2f2;
        font-weight: bold;
    }
    
    .signature-line {
        border-bottom: 1px solid #333;
        display: inline-block;
        min-width: 200px;
        margin: 0 10px;
    }
    
    .notes-line {
        border-bottom: 1px solid #333;
        display: inline-block;
        min-width: 300px;
    }
    
    .assessment-section {
        background-color: #f8f9fa;
        padding: 15px;
        border-radius: 5px;
        margin: 15px 0;
    }
    
    .phase-section {
        page-break-inside: avoid;
        margin-bottom: 20px;
    }
    
    .final-section {
        page-break-before: always;
    }
    """
    
    # Enhanced HTML with better formatting
    full_html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <title>UAT Quick Checklist - Automated Review Engine v1.0.0</title>
        <style>{css_content}</style>
    </head>
    <body>
        {html_content}
    </body>
    </html>
    """
    
    # Create the PDF
    font_config = FontConfiguration()
    css = CSS(string=css_content, font_config=font_config)
    
    html_doc = HTML(string=full_html)
    html_doc.write_pdf(pdf_file, stylesheets=[css], font_config=font_config)
    
    print(f"✅ PDF created successfully: {pdf_file}")
    print(f"📄 File size: {pdf_file.stat().st_size / 1024:.1f} KB")
    
    return pdf_file

if __name__ == "__main__":
    try:
        pdf_path = convert_markdown_to_pdf()
        print(f"\n🎉 UAT Quick Checklist PDF is ready!")
        print(f"📍 Location: {pdf_path}")
        print(f"🔗 Full path: {pdf_path.absolute()}")
    except Exception as e:
        print(f"❌ Error creating PDF: {e}")
        import traceback
        traceback.print_exc()
