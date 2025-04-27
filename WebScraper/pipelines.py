# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, PageBreak, Preformatted,
    ListFlowable, ListItem
)
from reportlab.lib.units import inch
from reportlab.lib.enums import TA_LEFT, TA_CENTER
from collections import defaultdict

class WebscraperPipeline:
    def __init__(self):
        self.items = defaultdict(list)
        self.outline = []
        
        # Unit 0 and 1 page order
        self.page_order = {
            # Unit 0 pages
            'introduction': 1,
            'onboarding': 2,
            'discord101': 3,
            
            # Unit 1 pages
            'what-are-agents': 1,
            'what-are-llms': 2,
            'messages-and-special-tokens': 3,
            'tools': 4,
            'agent-steps-and-structure': 5,
            'thoughts': 6,
            'actions': 7,
            'observations': 8,
            'dummy-agent-library': 9,
            'tutorial': 10,
            'quiz1': 11,
            'quiz2': 12,
            'final-quiz': 13,
            'conclusion': 14
        }

    def process_item(self, item, spider):
        adapter = ItemAdapter(item)
        unit = adapter.get('unit', '')
        if unit:
            # Extract page name from URL
            page_name = item['url'].rstrip('/').split('/')[-1]
            # Get predefined order or use a high number for unknown pages
            order = self.page_order.get(page_name, 999)
            item['unit_order'] = order
            self.items[unit].append(item)
        else:
            depth = adapter.get('depth', 0)
            self.items[f"depth_{depth}"].append(item)
        return item
    
    def create_styles(self):
        styles = getSampleStyleSheet()
        
        # Modify existing heading style
        styles['Heading1'].fontSize = 24
        styles['Heading1'].spaceAfter = 22
        styles['Heading1'].spaceBefore = 22
        styles['Heading1'].alignment = TA_LEFT
        
        # Table of Contents style
        styles.add(
            ParagraphStyle(
                name='TOCEntry',
                parent=styles['Normal'],
                fontSize=12,
                leading=16,
                spaceBefore=6,
                spaceAfter=6,
            )
        )
        
        # Code block style with better formatting
        styles.add(
            ParagraphStyle(
                name='CodeBlock',
                fontName='Courier',
                fontSize=9,
                leading=12,
                textColor=colors.black,
                backColor=colors.lightgrey,
                leftIndent=20,
                rightIndent=20,
                spaceBefore=10,
                spaceAfter=10,
                firstLineIndent=0,
                borderWidth=1,
                borderColor=colors.grey,
                borderPadding=5
            )
        )
        
        # URL style
        styles.add(
            ParagraphStyle(
                name='SourceURL',
                parent=styles['Italic'],
                textColor=colors.blue,
                fontSize=10,
                spaceBefore=5,
                spaceAfter=20
            )
        )
        
        # List style with better indentation
        styles.add(
            ParagraphStyle(
                name='BulletPoint',
                parent=styles['Normal'],
                leftIndent=20,
                spaceBefore=5,
                spaceAfter=5,
                bulletIndent=10,
                firstLineIndent=0
            )
        )
        
        # Add custom heading styles for levels 2-6
        for i in range(2, 7):
            styles.add(
                ParagraphStyle(
                    name=f'CustomHeading{i}',
                    parent=styles['Heading1'],
                    fontSize=24-(i*2),
                    spaceAfter=22-(i*2),
                    spaceBefore=22-(i*2),
                    leftIndent=(i-1)*10  # Increase indentation for sub-headings
                )
            )
        
        return styles
    
    def process_content_block(self, block, styles):
        if block['type'] == 'heading':
            style_name = 'Heading1' if block['level'] == 1 else f'CustomHeading{block["level"]}'
            heading = Paragraph(
                block['content'],
                styles[style_name]
            )
            self.outline.append((block['content'], block['level']))
            return heading
            
        elif block['type'] == 'paragraph':
            return Paragraph(
                block['content'],
                styles['Normal']
            )
            
        elif block['type'] == 'code':
            # Add line numbers to code blocks
            lines = block['content'].split('\n')
            numbered_lines = [f'{i+1:<3} {line}' for i, line in enumerate(lines)]
            return Preformatted(
                '\n'.join(numbered_lines),
                styles['CodeBlock']
            )
            
        elif block['type'] == 'list':
            items = []
            for item_text in block['items']:
                items.append(
                    ListItem(
                        Paragraph(item_text, styles['BulletPoint']),
                        value='bullet'
                    )
                )
            return ListFlowable(
                items,
                bulletType='bullet',
                start='bullet',
                leftIndent=20,
                bulletFontSize=8,
                bulletOffsetY=2
            )
            
        return None

    def create_header_footer(self, canvas, doc):
        canvas.saveState()
        canvas.setFont('Times-Roman', 9)
        
        # Footer with page number
        canvas.drawString(doc.leftMargin, 0.75 * inch, "Hugging Face Agents Course")
        page_num = canvas.getPageNumber()
        canvas.drawRightString(doc.pagesize[0] - doc.rightMargin, 0.75 * inch,
                             f"Page {page_num}")
        
        canvas.restoreState()
    
    def create_toc(self, styles):
        content = [Paragraph("Table of Contents", styles['Heading1'])]
        
        for title, level in self.outline:
            indent = (level - 1) * 20
            content.append(
                Paragraph(
                    f"{'&nbsp;' * indent}{title}",
                    styles['TOCEntry']
                )
            )
        
        content.append(PageBreak())
        return content
    
    def close_spider(self, spider):
        doc = SimpleDocTemplate(
            "course_content.pdf",
            pagesize=letter,
            rightMargin=72,
            leftMargin=72,
            topMargin=72,
            bottomMargin=72
        )
        
        styles = self.create_styles()
        content = []
        
        # Add title page
        content.append(Paragraph("Hugging Face Agents Course", styles['Heading1']))
        content.append(Spacer(1, 30))
        content.append(PageBreak())
        
        main_content = []

        # Process content in unit order
        unit_keys = sorted([k for k in self.items.keys() if k.startswith('unit')], 
                         key=lambda x: int(x.replace('unit', '')))
        
        for unit in unit_keys:
            # Sort items within unit by their page_order
            unit_items = sorted(self.items[unit], 
                             key=lambda x: x.get('unit_order', float('inf')))
            
            # Add unit header
            main_content.append(Paragraph(f"Unit {unit.replace('unit', '')}", 
                                       styles['Heading1']))
            main_content.append(PageBreak())
            
            # Process items in order
            for item in unit_items:
                self._process_content_item(item, styles, main_content)

        # Add table of contents
        content.extend(self.create_toc(styles))
        
        # Add main content
        content.extend(main_content)
        
        # Build PDF
        doc.build(
            content,
            onFirstPage=self.create_header_footer,
            onLaterPages=self.create_header_footer
        )

    def _process_content_item(self, item, styles, main_content):
        if item['title']:
            main_content.append(Paragraph(item['title'], styles['Heading1']))
        
        main_content.append(
            Paragraph(f"Source: {item['url']}", styles['SourceURL'])
        )
        main_content.append(Spacer(1, 0.2 * inch))
        
        for block in item['content_blocks']:
            element = self.process_content_block(block, styles)
            if element:
                main_content.append(element)
                if block['type'] in ['heading', 'code']:
                    main_content.append(Spacer(1, 0.1 * inch))
        
        main_content.append(PageBreak())
