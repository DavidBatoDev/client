from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.platypus import Paragraph
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_RIGHT
import json
import os
import fitz  # PyMuPDF

def convert_coordinates(y_coord, page_height):
    """Convert normalized y-coordinate to PDF coordinate system."""
    return page_height * (1 - y_coord)

def draw_rounded_rect(c, x, y, width, height, radius):
    """Draw a rounded rectangle that doesn't interfere with text positioning."""
    if radius <= 0:
        c.rect(x, y, width, height, fill=1, stroke=0)
        return
    
    # For small radii or boxes, just draw regular rectangle
    if radius > min(width, height) / 2:
        radius = min(width, height) / 2
    
    # Draw main rectangle (center part)
    c.rect(x + radius, y, width - 2*radius, height, fill=1, stroke=0)
    c.rect(x, y + radius, width, height - 2*radius, fill=1, stroke=0)
    
    # Draw corner circles to create rounded effect
    c.circle(x + radius, y + radius, radius, fill=1, stroke=0)
    c.circle(x + width - radius, y + radius, radius, fill=1, stroke=0)
    c.circle(x + radius, y + height - radius, radius, fill=1, stroke=0)
    c.circle(x + width - radius, y + height - radius, radius, fill=1, stroke=0)

def draw_rounded_border(c, x, y, width, height, radius):
    """Draw a rounded border that matches the rounded rectangle."""
    if radius <= 0:
        c.rect(x, y, width, height, fill=0, stroke=1)
        return
    
    # For small radii or boxes, just draw regular rectangle border
    if radius > min(width, height) / 2:
        radius = min(width, height) / 2
    
    # Draw main rectangle borders (center part)
    c.line(x + radius, y, x + width - radius, y)  # Top
    c.line(x + radius, y + height, x + width - radius, y + height)  # Bottom
    c.line(x, y + radius, x, y + height - radius)  # Left
    c.line(x + width, y + radius, x + width, y + height - radius)  # Right
    
    # Draw corner arcs to create rounded effect
    c.arc(x, y + height - 2*radius, x + 2*radius, y + height, 90, 180)  # Bottom-left
    c.arc(x + width - 2*radius, y + height - 2*radius, x + width, y + height, 0, 90)  # Bottom-right
    c.arc(x + width - 2*radius, y, x + width, y + 2*radius, 270, 360)  # Top-right
    c.arc(x, y, x + 2*radius, y + 2*radius, 180, 270)  # Top-left

def detect_image_regions(pdf_path, page_num=None):
    """Detect image regions in the PDF."""
    doc = fitz.open(pdf_path)
    image_regions = []
    
    page_range = range(doc.page_count)
    if page_num is not None and 0 <= page_num < doc.page_count:
        page_range = [page_num]
        
    for p_num in page_range:
        page = doc[p_num]
        image_list = page.get_images()
        
        for img_index, img in enumerate(image_list):
            # Get image rectangle
            img_rect = page.get_image_rects(img[0])
            if img_rect:
                for rect in img_rect:
                    # Convert to normalized coordinates
                    page_rect = page.rect
                    normalized_rect = {
                        "x": rect.x0 / page_rect.width,
                        "y": rect.y0 / page_rect.height,
                        "width": (rect.x1 - rect.x0) / page_rect.width,
                        "height": (rect.y1 - rect.y0) / page_rect.height,
                        "page": p_num
                    }
                    image_regions.append(normalized_rect)
    
    doc.close()
    return image_regions

def draw_image_outline(c, x, y, width, height):
    """Draw an outline around image regions."""
    # Draw a dashed border around image
    c.setStrokeColorRGB(0.7, 0.7, 0.7)  # Light gray
    c.setLineWidth(2)
    c.setDash(5, 3)  # Dashed line pattern
    c.rect(x - 2, y - 2, width + 4, height + 4, fill=0, stroke=1)
    c.setDash()  # Reset to solid line

def generate_styled_pdf(layout_json_path, output_path, original_pdf_path=None, page_num=None):
    """Generate a PDF file from enhanced layout with styling."""
    # Load the layout data
    with open(layout_json_path, 'r', encoding='utf-8') as f:
        layout_data = json.load(f)

    # Detect image regions if original PDF is provided
    image_regions = []
    if original_pdf_path and os.path.exists(original_pdf_path):
        image_regions = detect_image_regions(original_pdf_path, page_num=page_num)

    # Set up the PDF canvas
    page_width, page_height = letter
    c = canvas.Canvas(output_path, pagesize=letter)
    
    # Get a sample style sheet
    styles = getSampleStyleSheet()

    # Draw image outlines first (so they appear behind text)
    for img_region in image_regions:
        img_x = img_region['x'] * page_width
        img_y = convert_coordinates(img_region['y'] + img_region['height'], page_height)
        img_width = img_region['width'] * page_width
        img_height = img_region['height'] * page_height
        
        draw_image_outline(c, img_x, img_y, img_width, img_height)

    # Sort entities by y-coordinate
    entities = [e for e in layout_data['entities'] if e['bounding_poly'] is not None]
    entities.sort(key=lambda e: e['bounding_poly']['vertices'][0]['y'])

    # Process each entity
    for entity in entities:
        if not entity['bounding_poly']:
            continue

        # Get vertices
        vertices = entity['bounding_poly']['vertices']
        
        # Calculate coordinates
        x1 = vertices[0]['x'] * page_width
        y1 = convert_coordinates(vertices[0]['y'], page_height)
        x2 = vertices[1]['x'] * page_width
        y2 = convert_coordinates(vertices[1]['y'], page_height)
        x3 = vertices[2]['x'] * page_width
        y3 = convert_coordinates(vertices[2]['y'], page_height)
        x4 = vertices[3]['x'] * page_width
        y4 = convert_coordinates(vertices[3]['y'], page_height)

        # Calculate box dimensions
        box_width = x2 - x1
        box_height = abs(y1 - y4)
        box_y = min(y1, y2, y3, y4)

        # Get styling
        style = entity.get('style', {})
        bg_color = style.get('background_color', [0.95, 0.95, 0.95])
        text_color = style.get('text_color', [0, 0, 0])
        border_radius = style.get('border_radius', 0)
        has_border = style.get('has_border', False)
        border_color = style.get('border_color', [0.8, 0.8, 0.8])
        padding = style.get('padding', 8)
        font_weight = style.get('font_weight', 'normal')
        alignment_str = style.get('alignment', 'left')

        # Set font sizes based on entity type for visual hierarchy
        entity_type = entity.get('type', 'unknown')
        if entity_type == 'MessengerTextBox':
            font_size = 14
        elif entity_type == 'audience_name':
            font_size = 15
        elif entity_type in ['chat_time', 'chat_label', 'chat_reply', 'replied to']:
            font_size = 10
        else:
            font_size = 12

        # Only apply background boxes and rounded corners to MessengerTextBox entities
        if entity['type'] != 'MessengerTextBox':
            bg_color = None  # No background for non-MessengerTextBox entities
            border_radius = 0
            has_border = False
        else:
            # Add border for MessengerTextBox entities
            has_border = True
            border_color = [0.7, 0.7, 0.7]  # Medium gray border
            border_radius = 6  # Slightly reduced rounded corners
            # Override any style border_radius to ensure rounded corners
            style['border_radius'] = border_radius

        # Determine font name
        if font_weight == 'bold':
            font_name = 'Helvetica-Bold'
        else:
            font_name = 'Helvetica'

        # Map alignment string to ReportLab alignment enum
        if alignment_str == 'center':
            alignment = TA_CENTER
        elif alignment_str == 'right':
            alignment = TA_RIGHT
        else:
            alignment = TA_LEFT

        # Create ParagraphStyle
        p_style = ParagraphStyle(
            name='CustomStyle',
            parent=styles['Normal'],
            fontName=font_name,
            fontSize=font_size,
            leading=font_size * 1.2,
            textColor=f'rgb({text_color[0]},{text_color[1]},{text_color[2]})',
            alignment=alignment,
            leftIndent=0,
            rightIndent=0,
            spaceBefore=0,
            spaceAfter=0,
        )

        # Create the paragraph to measure it
        p_text = entity['text'].replace('\n', '<br/>')
        p = Paragraph(p_text, p_style)
        text_render_width = box_width
        w_text, h_text = p.wrapOn(c, text_render_width, 10000)

        if entity['type'] == 'MessengerTextBox':
            # Calculate dimensions for the padded box
            expanded_padding = padding
            expanded_width = box_width + (2 * expanded_padding)
            expanded_height = h_text + (2 * expanded_padding)
            
            # Calculate position for the padded box, keeping it vertically centered
            # relative to the original bounding box
            expanded_x = x1 - expanded_padding
            expanded_y = box_y + (box_height - expanded_height) / 2 # Center vertically
            
            # Draw background
            if bg_color:
                c.setFillColorRGB(*bg_color)
                if border_radius > 0:
                    c.roundRect(expanded_x, expanded_y, expanded_width, expanded_height, border_radius, fill=1, stroke=0)
                else:
                    c.rect(expanded_x, expanded_y, expanded_width, expanded_height, fill=1, stroke=0)
            
            # Draw border
            if has_border:
                c.setStrokeColorRGB(*border_color)
                c.setLineWidth(1)
                if border_radius > 0:
                    c.roundRect(expanded_x, expanded_y, expanded_width, expanded_height, border_radius, fill=0, stroke=1)
                else:
                    c.rect(expanded_x, expanded_y, expanded_width, expanded_height, fill=0, stroke=1)

            # Calculate text position inside the padded box
            text_draw_x = x1
            text_draw_y = expanded_y + expanded_padding
            
            # Draw the paragraph
            p.drawOn(c, text_draw_x, text_draw_y)
        else:
            # For other elements, center the text vertically in the original bounding box
            text_draw_x = x1
            text_draw_y = box_y + (box_height - h_text) / 2
            p.drawOn(c, text_draw_x, text_draw_y)

    # Save the PDF
    c.save()
    print(f"✅ Styled PDF exported to {output_path}")

def main():
    # File paths
    layout_json_path = "enhanced_layout.json"
    original_pdf_path = "temp/test2.pdf"  # Path to original PDF for image detection
    output_dir = "layout_output"
    
    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)
    
    # Generate PDF
    output_path = os.path.join(output_dir, "styled_document.pdf")
    generate_styled_pdf(layout_json_path, output_path, original_pdf_path)

if __name__ == "__main__":
    main() 