#!/usr/bin/env python3
"""
UAT Test Plan PDF Converter
Converts the comprehensive User Acceptance Test Plan from Markdown to PDF format
"""

from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_JUSTIFY
from reportlab.lib.colors import HexColor
import re
from pathlib import Path

def create_uat_plan_pdf():
    """Create comprehensive UAT plan PDF"""
    
    # File paths
    base_dir = Path(__file__).parent
    md_file = base_dir / "docs" / "user_acceptance_test_plan.md"
    pdf_file = base_dir / "docs" / "User_Acceptance_Test_Plan_v1.0.0.pdf"
    
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
        parent=styles['Title'],
        fontSize=16,
        spaceAfter=20,
        alignment=TA_CENTER,
        textColor=HexColor('#2c3e50')
    )
    
    subtitle_style = ParagraphStyle(
        'Subtitle',
        parent=styles['Normal'],
        fontSize=10,
        spaceAfter=15,
        alignment=TA_CENTER,
        textColor=HexColor('#7f8c8d')
    )
    
    heading1_style = ParagraphStyle(
        'Heading1',
        parent=styles['Heading1'],
        fontSize=13,
        spaceBefore=20,
        spaceAfter=10,
        textColor=HexColor('#2c3e50')
    )
    
    heading2_style = ParagraphStyle(
        'Heading2',
        parent=styles['Heading2'],
        fontSize=11,
        spaceBefore=15,
        spaceAfter=8,
        textColor=HexColor('#34495e')
    )
    
    heading3_style = ParagraphStyle(
        'Heading3',
        parent=styles['Heading3'],
        fontSize=10,
        spaceBefore=12,
        spaceAfter=6,
        textColor=HexColor('#2c3e50')
    )
    
    heading4_style = ParagraphStyle(
        'Heading4',
        parent=styles['Heading4'],
        fontSize=9,
        spaceBefore=10,
        spaceAfter=5,
        textColor=HexColor('#34495e')
    )
    
    body_style = ParagraphStyle(
        'Body',
        parent=styles['Normal'],
        fontSize=9,
        spaceBefore=3,
        spaceAfter=3,
        alignment=TA_JUSTIFY
    )
    
    bullet_style = ParagraphStyle(
        'Bullet',
        parent=styles['Normal'],
        fontSize=9,
        leftIndent=20,
        spaceBefore=2,
        spaceAfter=2
    )
    
    code_style = ParagraphStyle(
        'Code',
        parent=styles['Normal'],
        fontSize=8,
        leftIndent=30,
        rightIndent=30,
        spaceBefore=5,
        spaceAfter=5,
        backColor=HexColor('#f8f9fa')
    )
    
    checkbox_style = ParagraphStyle(
        'Checkbox',
        parent=styles['Normal'],
        fontSize=9,
        leftIndent=15,
        spaceBefore=1,
        spaceAfter=1
    )
    
    # Parse content and create story
    story = []
    lines = content.split('\n')
    
    in_code_block = False
    code_lines = []
    
    for i, line in enumerate(lines):
        original_line = line
        line = line.strip()
        
        # Handle code blocks
        if line.startswith('```'):
            if in_code_block:
                # End code block
                if code_lines:
                    code_text = '\n'.join(code_lines)
                    story.append(Paragraph(code_text, code_style))
                    code_lines = []
                in_code_block = False
            else:
                # Start code block
                in_code_block = True
            continue
        
        if in_code_block:
            code_lines.append(original_line)
            continue
        
        if not line:
            continue
            
        # Title (# at start)
        if line.startswith('# ') and i < 5:  # Only first few lines as main title
            title = line[2:].strip()
            title = re.sub(r'\*\*([^*]+)\*\*', r'\1', title)
            story.append(Paragraph(title, title_style))
            story.append(Spacer(1, 10))
            
        # Main headings (## )
        elif line.startswith('## '):
            heading = line[3:].strip()
            # Remove emoji and clean formatting
            heading = re.sub(r'[🎯📋🧪📝📊🎯📞]', '', heading).strip()
            heading = re.sub(r'\*\*([^*]+)\*\*', r'\1', heading)
            story.append(Paragraph(heading, heading1_style))
            
        # Sub headings (### )
        elif line.startswith('### '):
            subheading = line[4:].strip()
            subheading = re.sub(r'\*\*([^*]+)\*\*', r'\1', subheading)
            story.append(Paragraph(subheading, heading2_style))
            
        # Sub-sub headings (#### )
        elif line.startswith('#### '):
            subsubheading = line[5:].strip()
            subsubheading = re.sub(r'\*\*([^*]+)\*\*', r'\1', subsubheading)
            story.append(Paragraph(subsubheading, heading3_style))
            
        # Bullet points and lists
        elif line.startswith('- ') or line.startswith('* '):
            bullet_text = line[2:].strip()
            # Handle emoji bullets and clean formatting
            bullet_text = re.sub(r'\*\*([^*]+)\*\*', r'\1', bullet_text)
            bullet_text = re.sub(r'`([^`]+)`', r'\1', bullet_text)
            story.append(Paragraph(f"• {bullet_text}", bullet_style))
            
        # Checkboxes
        elif line.startswith('□'):
            checkbox_text = line.replace('□', '☐')
            checkbox_text = re.sub(r'\*\*([^*]+)\*\*', r'\1', checkbox_text)
            story.append(Paragraph(checkbox_text, checkbox_style))
            
        # Numbered lists
        elif re.match(r'^\d+\.', line):
            story.append(Paragraph(line, bullet_style))
            
        # Horizontal rules
        elif line.startswith('---'):
            story.append(Spacer(1, 10))
            
        # Version info and metadata (at top)
        elif line.startswith('**Version:**') or line.startswith('**Date:**') or line.startswith('**Author:**') or line.startswith('**Purpose:**'):
            clean_line = re.sub(r'\*\*([^*]+)\*\*', r'\1', line)
            story.append(Paragraph(clean_line, subtitle_style))
            
        # Regular paragraphs
        elif line and not line.startswith('`'):
            # Clean up all markdown formatting
            cleaned = line
            cleaned = re.sub(r'\*\*([^*]+)\*\*', r'\1', cleaned)
            cleaned = re.sub(r'\*([^*]+)\*', r'\1', cleaned)
            cleaned = re.sub(r'`([^`]+)`', r'\1', cleaned)
            
            # Handle special markers
            if line.startswith('✅') or line.startswith('❌') or line.startswith('⚠️'):
                story.append(Paragraph(cleaned, bullet_style))
            elif cleaned.strip():
                story.append(Paragraph(cleaned, body_style))
    
    # Add footer information
    story.append(PageBreak())
    story.append(Paragraph("Document Information", heading2_style))
    story.append(Spacer(1, 10))
    
    footer_info = [
        "Document: User Acceptance Test Plan",
        "Version: 1.0.0",
        "Generated: July 26, 2025",
        "Author: Klaus Bang Andersen",
        "Contact: klaus.bang.andersen@gmail.com",
        "",
        "This document validates the Automated Review Engine v1.0.0",
        "for production deployment in regulatory environments."
    ]
    
    for info in footer_info:
        if info:
            story.append(Paragraph(info, body_style))
        else:
            story.append(Spacer(1, 6))
    
    # Build PDF
    doc.build(story)
    
    print(f"✅ PDF created successfully: {pdf_file}")
    if pdf_file.exists():
        print(f"📄 File size: {pdf_file.stat().st_size / 1024:.1f} KB")
    
    return pdf_file

if __name__ == "__main__":
    try:
        pdf_path = create_uat_plan_pdf()
        print(f"\n🎉 User Acceptance Test Plan PDF is ready!")
        print(f"📍 Location: {pdf_path}")
        print(f"🔗 Full path: {pdf_path.absolute()}")
    except Exception as e:
        print(f"❌ Error creating PDF: {e}")
        import traceback
        traceback.print_exc()
