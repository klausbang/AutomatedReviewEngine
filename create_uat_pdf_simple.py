#!/usr/bin/env python3
"""
UAT Checklist PDF Converter - Simple ReportLab Version
Converts the UAT Quick Checklist from Markdown to PDF format using ReportLab
"""

from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak
from reportlab.lib.enums import TA_LEFT, TA_CENTER
from reportlab.lib.colors import HexColor
import re
from pathlib import Path

def create_uat_pdf():
    """Create UAT checklist PDF using ReportLab"""
    
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
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=16,
        spaceAfter=20,
        textColor=HexColor('#2c3e50'),
        alignment=TA_CENTER
    )
    
    heading_style = ParagraphStyle(
        'CustomHeading',
        parent=styles['Heading2'],
        fontSize=12,
        spaceBefore=15,
        spaceAfter=10,
        textColor=HexColor('#34495e')
    )
    
    subheading_style = ParagraphStyle(
        'CustomSubheading',
        parent=styles['Heading3'],
        fontSize=10,
        spaceBefore=10,
        spaceAfter=5,
        textColor=HexColor('#2c3e50')
    )
    
    body_style = ParagraphStyle(
        'CustomBody',
        parent=styles['Normal'],
        fontSize=9,
        spaceBefore=3,
        spaceAfter=3
    )
    
    checkbox_style = ParagraphStyle(
        'Checkbox',
        parent=styles['Normal'],
        fontSize=9,
        leftIndent=20,
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
            story.append(Paragraph(title, title_style))
            story.append(Spacer(1, 12))
            
        # Main headings (## )
        elif line.startswith('## '):
            heading = line[3:].strip()
            # Remove emoji and format
            heading = re.sub(r'[🚀✅🎛️📤📋📊🛡️🎯]', '', heading).strip()
            story.append(Paragraph(heading, heading_style))
            
        # Subheadings (### )
        elif line.startswith('### '):
            subheading = line[4:].strip()
            story.append(Paragraph(subheading, subheading_style))
            
        # Checkboxes
        elif line.startswith('□'):
            checkbox_text = line.replace('□', '☐')
            story.append(Paragraph(checkbox_text, checkbox_style))
            
        # Results/Notes lines
        elif line.startswith('**Result:**') or line.startswith('**Notes:**'):
            story.append(Paragraph(line, body_style))
            
        # Horizontal rules
        elif line.startswith('---'):
            story.append(Spacer(1, 10))
            
        # Regular paragraphs
        elif line and not line.startswith('```') and not line.startswith('|'):
            # Clean up markdown formatting - fix bold tags
            cleaned = line
            # Handle bold text properly
            cleaned = re.sub(r'\*\*([^*]+)\*\*', r'<b>\1</b>', cleaned)
            cleaned = re.sub(r'`([^`]+)`', r'<font name="Courier">\1</font>', cleaned)
            
            # Handle special sections
            if 'Tester:' in line or 'Date:' in line or 'Environment:' in line or 'Duration:' in line:
                story.append(Paragraph(cleaned, body_style))
            elif line.startswith('*') and not line.startswith('**'):
                # Italic text at bottom
                cleaned = cleaned.replace('*', '<i>').replace('*', '</i>')
                story.append(Paragraph(cleaned, body_style))
            elif cleaned:
                story.append(Paragraph(cleaned, body_style))
    
    # Add final signature section
    story.append(PageBreak())
    story.append(Paragraph("Test Completion Summary", heading_style))
    story.append(Spacer(1, 12))
    
    signature_content = [
        "Tester Signature: ________________________________ Date: __________",
        "",
        "This document serves as official validation that the Automated Review Engine v1.0.0",
        "has been thoroughly tested and meets professional regulatory standards.",
        "",
        "For questions or support, contact: klaus.bang.andersen@gmail.com"
    ]
    
    for line in signature_content:
        if line:
            story.append(Paragraph(line, body_style))
        else:
            story.append(Spacer(1, 6))
    
    # Build PDF
    doc.build(story)
    
    print(f"✅ PDF created successfully: {pdf_file}")
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
