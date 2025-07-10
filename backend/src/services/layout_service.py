"""
Layout service for processing OCR results into canvas layouts
"""

from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from loguru import logger
import uuid
from datetime import datetime

from ..models.layouts import Layout, LayoutElement
from ..models.images import Image
from ..models.ocr_results import OCRResult
from ..models.users import User


class LayoutService:
    """
    Service for processing OCR results into canvas layouts
    """
    
    def __init__(self):
        pass
    
    def create_layout_from_ocr(
        self,
        db: Session,
        user_id: int,
        image_id: int,
        ocr_result: OCRResult,
        layout_name: str = None
    ) -> Layout:
        """
        Create a layout from OCR results
        """
        try:
            # Get image dimensions
            image = db.query(Image).filter(Image.id == image_id).first()
            if not image:
                raise ValueError("Image not found")
            
            # Create layout
            layout = Layout(
                user_id=user_id,
                image_id=image_id,
                name=layout_name or f"Layout for {image.original_filename}",
                description=f"Auto-generated layout from OCR processing",
                canvas_width=image.width or 800,
                canvas_height=image.height or 600,
                is_active=True,
                is_template=False,
                layout_data=self._create_layout_data(ocr_result)
            )
            
            db.add(layout)
            db.commit()
            db.refresh(layout)
            
            # Create layout elements from OCR results
            elements = self._create_elements_from_ocr(ocr_result, layout.id)
            
            for element in elements:
                db.add(element)
            
            db.commit()
            
            logger.info(f"Created layout with {len(elements)} elements from OCR result")
            return layout
            
        except Exception as e:
            logger.error(f"Error creating layout from OCR: {e}")
            raise
    
    def _create_layout_data(self, ocr_result: OCRResult) -> Dict[str, Any]:
        """
        Create layout data from OCR result
        """
        return {
            "ocr_metadata": {
                "processor_type": ocr_result.processor_type,
                "confidence_score": ocr_result.confidence_score,
                "processing_time": ocr_result.processing_time,
                "detected_language": ocr_result.detected_language,
                "created_at": datetime.now().isoformat()
            },
            "canvas_settings": {
                "background_color": "#ffffff",
                "grid_enabled": True,
                "grid_size": 10,
                "snap_to_grid": True
            }
        }
    
    def _create_elements_from_ocr(
        self,
        ocr_result: OCRResult,
        layout_id: int
    ) -> List[LayoutElement]:
        """
        Create layout elements from OCR result
        """
        elements = []
        
        # Process text blocks
        if ocr_result.text_blocks:
            for i, text_block in enumerate(ocr_result.text_blocks):
                element = self._create_text_element(text_block, layout_id, i)
                elements.append(element)
        
        # Process layout elements (UI components)
        if ocr_result.layout_elements:
            for i, layout_element in enumerate(ocr_result.layout_elements):
                element = self._create_ui_element(layout_element, layout_id, i)
                elements.append(element)
        
        return elements
    
    def _create_text_element(
        self,
        text_block: Dict[str, Any],
        layout_id: int,
        index: int
    ) -> LayoutElement:
        """
        Create a text element from OCR text block
        """
        bbox = text_block.get("bounding_box", {})
        
        return LayoutElement(
            layout_id=layout_id,
            element_type="text",
            element_id=f"text_{index}_{uuid.uuid4().hex[:8]}",
            x=bbox.get("x", 0),
            y=bbox.get("y", 0),
            width=bbox.get("width", 100),
            height=bbox.get("height", 20),
            content=text_block.get("text", ""),
            font_size=self._estimate_font_size(bbox),
            font_family="Arial",
            font_weight="normal",
            text_align="left",
            text_color="#000000",
            background_color="transparent",
            opacity=1.0,
            rotation=0.0,
            z_index=index,
            confidence_score=text_block.get("confidence", 0.0),
            original_category="text_block",
            is_visible=True,
            is_locked=False,
            metadata={
                "ocr_source": "text_block",
                "page_number": text_block.get("page_number", 1)
            }
        )
    
    def _create_ui_element(
        self,
        ui_element: Dict[str, Any],
        layout_id: int,
        index: int
    ) -> LayoutElement:
        """
        Create a UI element from OCR layout element
        """
        bbox = ui_element.get("bounding_box", {})
        element_type = self._determine_element_type(ui_element)
        
        return LayoutElement(
            layout_id=layout_id,
            element_type=element_type,
            element_id=f"{element_type}_{index}_{uuid.uuid4().hex[:8]}",
            x=bbox.get("x", 0),
            y=bbox.get("y", 0),
            width=bbox.get("width", 100),
            height=bbox.get("height", 100),
            content=ui_element.get("text", ""),
            font_size=self._estimate_font_size(bbox) if ui_element.get("text") else None,
            font_family="Arial" if ui_element.get("text") else None,
            font_weight="normal" if ui_element.get("text") else None,
            text_align="center" if ui_element.get("text") else None,
            text_color="#000000" if ui_element.get("text") else None,
            background_color=self._get_default_background_color(element_type),
            border_color=self._get_default_border_color(element_type),
            border_width=1.0,
            border_radius=self._get_default_border_radius(element_type),
            opacity=1.0,
            rotation=0.0,
            z_index=index + 1000,  # UI elements above text
            confidence_score=ui_element.get("confidence", 0.0),
            original_category=ui_element.get("type", "unknown"),
            is_visible=True,
            is_locked=False,
            metadata={
                "ocr_source": "layout_element",
                "page_number": ui_element.get("page_number", 1)
            }
        )
    
    def _determine_element_type(self, ui_element: Dict[str, Any]) -> str:
        """
        Determine element type based on OCR element properties
        """
        bbox = ui_element.get("bounding_box", {})
        width = bbox.get("width", 0)
        height = bbox.get("height", 0)
        text = ui_element.get("text", "").strip()
        element_type = ui_element.get("type", "").lower()
        
        # If it has text, it's likely a text element
        if text and len(text) > 0:
            return "text"
        
        # Check aspect ratio for circles (avatars, icons)
        if width > 0 and height > 0:
            aspect_ratio = width / height
            if 0.8 <= aspect_ratio <= 1.2 and min(width, height) > 20:
                return "circle"
        
        # Check for specific UI element types
        if "button" in element_type:
            return "rectangle"
        elif "avatar" in element_type or "profile" in element_type:
            return "circle"
        elif "icon" in element_type:
            return "circle"
        
        # Default to rectangle
        return "rectangle"
    
    def _estimate_font_size(self, bbox: Dict[str, Any]) -> int:
        """
        Estimate font size based on bounding box height
        """
        height = bbox.get("height", 20)
        
        # Rough estimation: font size is approximately 70% of height
        font_size = int(height * 0.7)
        
        # Clamp to reasonable range
        return max(8, min(72, font_size))
    
    def _get_default_background_color(self, element_type: str) -> str:
        """
        Get default background color for element type
        """
        color_map = {
            "text": "transparent",
            "rectangle": "#f0f0f0",
            "circle": "#e0e0e0"
        }
        return color_map.get(element_type, "#f0f0f0")
    
    def _get_default_border_color(self, element_type: str) -> str:
        """
        Get default border color for element type
        """
        color_map = {
            "text": "transparent",
            "rectangle": "#cccccc",
            "circle": "#cccccc"
        }
        return color_map.get(element_type, "#cccccc")
    
    def _get_default_border_radius(self, element_type: str) -> float:
        """
        Get default border radius for element type
        """
        radius_map = {
            "text": 0.0,
            "rectangle": 4.0,
            "circle": 50.0  # Will be adjusted based on dimensions
        }
        return radius_map.get(element_type, 0.0)
    
    def update_layout_from_canvas(
        self,
        db: Session,
        layout_id: int,
        canvas_elements: List[Dict[str, Any]]
    ) -> Layout:
        """
        Update layout from canvas elements
        """
        try:
            layout = db.query(Layout).filter(Layout.id == layout_id).first()
            if not layout:
                raise ValueError("Layout not found")
            
            # Clear existing elements
            db.query(LayoutElement).filter(
                LayoutElement.layout_id == layout_id
            ).delete()
            
            # Create new elements
            for element_data in canvas_elements:
                element = LayoutElement(
                    layout_id=layout_id,
                    **element_data
                )
                db.add(element)
            
            # Update layout version
            layout.version += 1
            layout.layout_data = {
                **layout.layout_data,
                "last_updated": datetime.now().isoformat(),
                "element_count": len(canvas_elements)
            }
            
            db.commit()
            db.refresh(layout)
            
            logger.info(f"Updated layout {layout_id} with {len(canvas_elements)} elements")
            return layout
            
        except Exception as e:
            logger.error(f"Error updating layout from canvas: {e}")
            raise
    
    def export_layout_to_json(self, layout: Layout) -> Dict[str, Any]:
        """
        Export layout to JSON format
        """
        return {
            "layout": {
                "id": layout.id,
                "name": layout.name,
                "description": layout.description,
                "canvas_width": layout.canvas_width,
                "canvas_height": layout.canvas_height,
                "version": layout.version,
                "created_at": layout.created_at.isoformat(),
                "layout_data": layout.layout_data
            },
            "elements": [
                {
                    "id": element.id,
                    "element_id": element.element_id,
                    "type": element.element_type,
                    "x": element.x,
                    "y": element.y,
                    "width": element.width,
                    "height": element.height,
                    "content": element.content,
                    "styling": {
                        "font_size": element.font_size,
                        "font_family": element.font_family,
                        "font_weight": element.font_weight,
                        "text_align": element.text_align,
                        "text_color": element.text_color,
                        "background_color": element.background_color,
                        "border_color": element.border_color,
                        "border_width": element.border_width,
                        "border_radius": element.border_radius
                    },
                    "transform": {
                        "opacity": element.opacity,
                        "rotation": element.rotation,
                        "z_index": element.z_index
                    },
                    "state": {
                        "is_visible": element.is_visible,
                        "is_locked": element.is_locked
                    },
                    "metadata": element.metadata
                }
                for element in layout.elements
            ]
        }


# Global layout service instance
layout_service = LayoutService() 