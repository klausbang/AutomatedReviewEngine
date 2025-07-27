#!/usr/bin/env python3
"""
UAT Checklist PDF Converter - Plain Text Version
Converts the UAT Quick Checklist to PDF format without HTML formatting
"""

from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.enums import TA_LEFT, TA_CENTER
from reportlab.lib.colors import HexColor
import re
from pathlib import Path

def create_uat_pdf():
    """Create UAT checklist PDF using plain text formatting"""
    
    # File paths
    base_dir = Path(__file__).parent
    md_file = base_dir / "docs" / "uat_quick_checklist.md"
    pdf_file = base_dir / "docs" / "UAT_Quick_Checklist_v1.0.0.pdf"
    
    print(f"Converting {md_file} to PDF...")
    
    # Read the Markdown file
    with open(md_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Create PDF document
    doc = SimpleDocTemplate(
        str(pdf_file),
        pagesize=A4,
        rightMargin=0.75*inch,
        leftMargin=0.75*inch,
        topMargin=1*inch,
        bottomMargin=1*inch
    )
    
    # Define styles
    styles = getSampleStyleSheet()
    
    # Custom styles
    title_style = ParagraphStyle(
        'Title',
        parent=styles['Heading1'],
        fontSize=14,
        spaceAfter=20,
        alignment=TA_CENTER
    )
    
    heading_style = ParagraphStyle(
        'Heading',
        parent=styles['Heading2'],
        fontSize=11,
        spaceBefore=15,
        spaceAfter=8
    )
    
    subheading_style = ParagraphStyle(
        'Subheading',
        parent=styles['Heading3'],
        fontSize=10,
        spaceBefore=8,
        spaceAfter=5
    )
    
    body_style = ParagraphStyle(
        'Body',
        parent=styles['Normal'],
        fontSize=9,
        spaceBefore=3,
        spaceAfter=3
    )
    
    checkbox_style = ParagraphStyle(
        'Checkbox',
        parent=styles['Normal'],
        fontSize=9,
        leftIndent=15,
        spaceBefore=2,
        spaceAfter=2
    )
    
    # Parse content and create story
    story = []
    lines = content.split('\n')
    
    for line in lines:
        line = line.strip()
        
        if not line:
            continue
            
        # Title (# )
        if line.startswith('# '):
            title = line[2:].strip()
            # Remove markdown formatting
            title = re.sub(r'\*\*([^*]+)\*\*', r'\1', title)
            story.append(Paragraph(title, title_style))
            story.append(Spacer(1, 12))
            
        # Main headings (## )
        elif line.startswith('## '):
            heading = line[3:].strip()
            # Remove emoji and markdown
            heading = re.sub(r'[🚀✅🎛️📤📋📊🛡️🎯]', '', heading).strip()
            heading = re.sub(r'\*\*([^*]+)\*\*', r'\1', heading)
            story.append(Paragraph(heading, heading_style))
            
        # Subheadings (### )
        elif line.startswith('### '):
            subheading = line[4:].strip()
            subheading = re.sub(r'\*\*([^*]+)\*\*', r'\1', subheading)
            story.append(Paragraph(subheading, subheading_style))
            
        # Checkboxes
        elif line.startswith('□'):
            checkbox_text = line.replace('□', '☐')
            # Remove markdown formatting
            checkbox_text = re.sub(r'\*\*([^*]+)\*\*', r'\1', checkbox_text)
            checkbox_text = re.sub(r'`([^`]+)`', r'\1', checkbox_text)
            story.append(Paragraph(checkbox_text, checkbox_style))
            
        # Results/Notes lines
        elif 'Result:' in line or 'Notes:' in line:
            clean_line = re.sub(r'\*\*([^*]+)\*\*', r'\1', line)
            story.append(Paragraph(clean_line, body_style))
            
        # Horizontal rules
        elif line.startswith('---'):
            story.append(Spacer(1, 8))
            
        # Regular paragraphs
        elif line and not line.startswith('```') and not line.startswith('|'):
            # Clean up all markdown formatting
            cleaned = line
            cleaned = re.sub(r'\*\*([^*]+)\*\*', r'\1', cleaned)
            cleaned = re.sub(r'\*([^*]+)\*', r'\1', cleaned)
            cleaned = re.sub(r'`([^`]+)`', r'\1', cleaned)
            
            if cleaned.strip():
                story.append(Paragraph(cleaned, body_style))
    
    # Add some extra content
    story.append(Spacer(1, 20))
    story.append(Paragraph("Test Completion", heading_style))
    story.append(Paragraph("Tester Signature: ________________________ Date: __________", body_style))
    story.append(Spacer(1, 10))
    story.append(Paragraph("Contact: klaus.bang.andersen@gmail.com", body_style))
    
    # Build PDF
    doc.build(story)
    
    print(f"✅ PDF created successfully: {pdf_file}")
    if pdf_file.exists():
        print(f"📄 File size: {pdf_file.stat().st_size / 1024:.1f} KB")
    
    return pdf_file

if __name__ == "__main__":
    try:
        pdf_path = create_uat_pdf()
        print(f"\n🎉 UAT Quick Checklist PDF is ready!")
        print(f"📍 Location: {pdf_path}")
        print(f"🔗 Full path: {pdf_path.absolute()}")
    except Exception as e:
        print(f"❌ Error creating PDF: {e}")
        import traceback
        traceback.print_exc()
