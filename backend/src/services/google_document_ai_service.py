"""
Google Document AI service for OCR processing
"""

from google.cloud import documentai
from google.api_core.client_options import ClientOptions
from typing import Dict, Any, List, Optional, Tuple
from loguru import logger
import asyncio
from datetime import datetime
import time

from ..config.settings import get_settings

# Initialize settings
settings = get_settings()


class GoogleDocumentAIService:
    """
    Google Document AI service for OCR processing
    """
    
    def __init__(self):
        self.project_id = settings.GOOGLE_PROJECT_ID
        self.location = settings.GOOGLE_DOCUMENT_AI_LOCATION
        self.processor_id = settings.GOOGLE_DOCUMENT_AI_PROCESSOR_ID
        
        # Initialize Document AI client
        client_options = ClientOptions(api_endpoint=f"{self.location}-documentai.googleapis.com")
        self.client = documentai.DocumentProcessorServiceClient(client_options=client_options)
        
        # Create processor name
        self.processor_name = self.client.processor_path(
            self.project_id, self.location, self.processor_id
        )
    
    async def process_image(self, image_content: bytes, mime_type: str) -> Dict[str, Any]:
        """
        Process an image using Google Document AI
        """
        try:
            start_time = time.time()
            
            # Create the document
            document = documentai.RawDocument(
                content=image_content,
                mime_type=mime_type
            )
            
            # Create the request
            request = documentai.ProcessRequest(
                name=self.processor_name,
                raw_document=document
            )
            
            # Process the document
            logger.info(f"Processing image with Document AI...")
            result = self.client.process_document(request=request)
            
            processing_time = time.time() - start_time
            
            # Extract information from the result
            document_response = result.document
            
            # Extract text
            full_text = document_response.text
            
            # Extract text blocks with positions
            text_blocks = self._extract_text_blocks(document_response)
            
            # Extract layout elements
            layout_elements = self._extract_layout_elements(document_response)
            
            # Extract bounding boxes
            bounding_boxes = self._extract_bounding_boxes(document_response)
            
            # Calculate confidence score
            confidence_score = self._calculate_confidence_score(document_response)
            
            # Detect language
            detected_language = self._detect_language(document_response)
            
            logger.info(f"Document AI processing completed in {processing_time:.2f}s")
            
            return {
                "success": True,
                "processing_time": processing_time,
                "full_text": full_text,
                "confidence_score": confidence_score,
                "text_blocks": text_blocks,
                "layout_elements": layout_elements,
                "bounding_boxes": bounding_boxes,
                "detected_language": detected_language,
                "page_count": len(document_response.pages),
                "raw_response": self._serialize_document_response(document_response)
            }
            
        except Exception as e:
            logger.error(f"Error processing image with Document AI: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def _extract_text_blocks(self, document: documentai.Document) -> List[Dict[str, Any]]:
        """
        Extract text blocks with positions from document
        """
        text_blocks = []
        
        for page in document.pages:
            for block in page.blocks:
                # Get text content
                text_content = self._get_text_from_segment(document.text, block.layout.text_anchor)
                
                # Get bounding box
                bounding_box = self._get_bounding_box(block.layout.bounding_poly)
                
                # Get confidence score
                confidence = block.layout.confidence if hasattr(block.layout, 'confidence') else 0.0
                
                text_blocks.append({
                    "text": text_content,
                    "confidence": confidence,
                    "bounding_box": bounding_box,
                    "page_number": page.page_number if hasattr(page, 'page_number') else 1
                })
        
        return text_blocks
    
    def _extract_layout_elements(self, document: documentai.Document) -> List[Dict[str, Any]]:
        """
        Extract layout elements from document
        """
        layout_elements = []
        
        for page in document.pages:
            # Extract paragraphs
            for paragraph in page.paragraphs:
                text_content = self._get_text_from_segment(document.text, paragraph.layout.text_anchor)
                bounding_box = self._get_bounding_box(paragraph.layout.bounding_poly)
                confidence = paragraph.layout.confidence if hasattr(paragraph.layout, 'confidence') else 0.0
                
                layout_elements.append({
                    "type": "paragraph",
                    "text": text_content,
                    "confidence": confidence,
                    "bounding_box": bounding_box,
                    "page_number": page.page_number if hasattr(page, 'page_number') else 1
                })
            
            # Extract lines
            for line in page.lines:
                text_content = self._get_text_from_segment(document.text, line.layout.text_anchor)
                bounding_box = self._get_bounding_box(line.layout.bounding_poly)
                confidence = line.layout.confidence if hasattr(line.layout, 'confidence') else 0.0
                
                layout_elements.append({
                    "type": "line",
                    "text": text_content,
                    "confidence": confidence,
                    "bounding_box": bounding_box,
                    "page_number": page.page_number if hasattr(page, 'page_number') else 1
                })
            
            # Extract words
            for word in page.tokens:
                text_content = self._get_text_from_segment(document.text, word.layout.text_anchor)
                bounding_box = self._get_bounding_box(word.layout.bounding_poly)
                confidence = word.layout.confidence if hasattr(word.layout, 'confidence') else 0.0
                
                layout_elements.append({
                    "type": "word",
                    "text": text_content,
                    "confidence": confidence,
                    "bounding_box": bounding_box,
                    "page_number": page.page_number if hasattr(page, 'page_number') else 1
                })
        
        return layout_elements
    
    def _extract_bounding_boxes(self, document: documentai.Document) -> List[Dict[str, Any]]:
        """
        Extract all bounding boxes from document
        """
        bounding_boxes = []
        
        for page in document.pages:
            # Process all detected elements
            for block in page.blocks:
                bounding_box = self._get_bounding_box(block.layout.bounding_poly)
                bounding_boxes.append({
                    "type": "block",
                    "bounding_box": bounding_box,
                    "page_number": page.page_number if hasattr(page, 'page_number') else 1
                })
        
        return bounding_boxes
    
    def _get_text_from_segment(self, text: str, text_anchor: documentai.Document.TextAnchor) -> str:
        """
        Extract text from text anchor segment
        """
        if not text_anchor or not text_anchor.text_segments:
            return ""
        
        # Get the text segment
        segment = text_anchor.text_segments[0]
        start_index = segment.start_index if hasattr(segment, 'start_index') else 0
        end_index = segment.end_index if hasattr(segment, 'end_index') else len(text)
        
        return text[start_index:end_index]
    
    def _get_bounding_box(self, bounding_poly: documentai.BoundingPoly) -> Dict[str, float]:
        """
        Convert bounding poly to bounding box coordinates
        """
        if not bounding_poly or not bounding_poly.vertices:
            return {"x": 0, "y": 0, "width": 0, "height": 0}
        
        vertices = bounding_poly.vertices
        
        # Calculate bounding box from vertices
        x_coords = [v.x for v in vertices if hasattr(v, 'x')]
        y_coords = [v.y for v in vertices if hasattr(v, 'y')]
        
        if not x_coords or not y_coords:
            return {"x": 0, "y": 0, "width": 0, "height": 0}
        
        min_x = min(x_coords)
        max_x = max(x_coords)
        min_y = min(y_coords)
        max_y = max(y_coords)
        
        return {
            "x": min_x,
            "y": min_y,
            "width": max_x - min_x,
            "height": max_y - min_y
        }
    
    def _calculate_confidence_score(self, document: documentai.Document) -> float:
        """
        Calculate average confidence score for the document
        """
        confidences = []
        
        for page in document.pages:
            for block in page.blocks:
                if hasattr(block.layout, 'confidence'):
                    confidences.append(block.layout.confidence)
        
        if not confidences:
            return 0.0
        
        return sum(confidences) / len(confidences)
    
    def _detect_language(self, document: documentai.Document) -> Optional[str]:
        """
        Detect language from document
        """
        # This is a simplified language detection
        # In a real implementation, you might use Google's language detection API
        return "en"  # Default to English
    
    def _serialize_document_response(self, document: documentai.Document) -> Dict[str, Any]:
        """
        Serialize document response for storage
        """
        # Convert document to a serializable format
        # This is a simplified version - you might want to store more details
        return {
            "text": document.text,
            "page_count": len(document.pages),
            "processed_at": datetime.now().isoformat()
        }
    
    async def process_layout_extraction(self, image_content: bytes, mime_type: str) -> Dict[str, Any]:
        """
        Process image specifically for layout extraction
        """
        try:
            # Process with Document AI
            result = await self.process_image(image_content, mime_type)
            
            if not result["success"]:
                return result
            
            # Convert to layout elements for canvas
            canvas_elements = self._convert_to_canvas_elements(result)
            
            return {
                "success": True,
                "canvas_elements": canvas_elements,
                "processing_time": result["processing_time"],
                "confidence_score": result["confidence_score"]
            }
            
        except Exception as e:
            logger.error(f"Error in layout extraction: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def _convert_to_canvas_elements(self, ocr_result: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Convert OCR results to canvas elements
        """
        canvas_elements = []
        
        for element in ocr_result.get("layout_elements", []):
            # Determine element type based on content and dimensions
            element_type = self._determine_element_type(element)
            
            # Create canvas element
            canvas_element = {
                "type": element_type,
                "x": element["bounding_box"]["x"],
                "y": element["bounding_box"]["y"],
                "width": element["bounding_box"]["width"],
                "height": element["bounding_box"]["height"],
                "content": element.get("text", ""),
                "confidence": element.get("confidence", 0.0),
                "original_category": element.get("type", "text")
            }
            
            # Add styling based on element type
            if element_type == "text":
                canvas_element.update({
                    "font_size": self._estimate_font_size(element["bounding_box"]),
                    "font_family": "Arial",
                    "text_color": "#000000"
                })
            elif element_type == "rectangle":
                canvas_element.update({
                    "background_color": "#f0f0f0",
                    "border_color": "#cccccc",
                    "border_width": 1
                })
            elif element_type == "circle":
                canvas_element.update({
                    "background_color": "#e0e0e0",
                    "border_color": "#cccccc",
                    "border_width": 1
                })
            
            canvas_elements.append(canvas_element)
        
        return canvas_elements
    
    def _determine_element_type(self, element: Dict[str, Any]) -> str:
        """
        Determine canvas element type based on OCR element
        """
        bbox = element["bounding_box"]
        width = bbox["width"]
        height = bbox["height"]
        text = element.get("text", "").strip()
        
        # If it has text, it's a text element
        if text:
            return "text"
        
        # If it's roughly square, it might be a circle (avatar, icon)
        aspect_ratio = width / height if height > 0 else 1
        if 0.8 <= aspect_ratio <= 1.2 and min(width, height) > 20:
            return "circle"
        
        # Otherwise, it's a rectangle
        return "rectangle"
    
    def _estimate_font_size(self, bounding_box: Dict[str, float]) -> int:
        """
        Estimate font size based on bounding box height
        """
        height = bounding_box["height"]
        
        # Rough estimation: font size is approximately 70% of height
        font_size = int(height * 0.7)
        
        # Clamp to reasonable range
        return max(8, min(72, font_size))


# Global Google Document AI service instance
google_doc_ai_service = GoogleDocumentAIService() 