"""
OCR Pydantic schemas
"""

from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import datetime


class OCRResultBase(BaseModel):
    """
    Base OCR result schema
    """
    processor_type: str
    processor_version: Optional[str] = None
    processing_time: Optional[float] = None
    full_text: Optional[str] = None
    confidence_score: Optional[float] = None
    page_count: int = 1
    detected_language: Optional[str] = None
    rotation_angle: float = 0.0
    has_error: bool = False
    processing_error: Optional[str] = None


class OCRResultCreate(OCRResultBase):
    """
    Schema for creating an OCR result
    """
    image_id: int
    text_blocks: Optional[List[Dict[str, Any]]] = None
    layout_elements: Optional[List[Dict[str, Any]]] = None
    bounding_boxes: Optional[List[Dict[str, Any]]] = None
    document_ai_response: Optional[Dict[str, Any]] = None


class OCRResultResponse(OCRResultBase):
    """
    Schema for OCR result response
    """
    id: int
    image_id: int
    text_blocks: Optional[List[Dict[str, Any]]] = None
    layout_elements: Optional[List[Dict[str, Any]]] = None
    bounding_boxes: Optional[List[Dict[str, Any]]] = None
    document_ai_response: Optional[Dict[str, Any]] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class OCRProcessRequest(BaseModel):
    """
    Schema for OCR processing request
    """
    image_id: int
    processor_type: str = "google_document_ai"
    options: Optional[Dict[str, Any]] = None


class OCRProcessResponse(BaseModel):
    """
    Schema for OCR processing response
    """
    success: bool
    processing_time: Optional[float] = None
    ocr_result: Optional[OCRResultResponse] = None
    canvas_elements: Optional[List[Dict[str, Any]]] = None
    error: Optional[str] = None


class TextBlock(BaseModel):
    """
    Schema for text block
    """
    text: str
    confidence: float
    bounding_box: Dict[str, float]
    page_number: int = 1


class LayoutElement(BaseModel):
    """
    Schema for layout element
    """
    type: str
    text: Optional[str] = None
    confidence: float
    bounding_box: Dict[str, float]
    page_number: int = 1


class BoundingBox(BaseModel):
    """
    Schema for bounding box
    """
    x: float
    y: float
    width: float
    height: float


class CanvasElement(BaseModel):
    """
    Schema for canvas element
    """
    type: str
    x: float
    y: float
    width: float
    height: float
    content: Optional[str] = None
    confidence: float
    original_category: Optional[str] = None
    font_size: Optional[int] = None
    font_family: Optional[str] = None
    text_color: Optional[str] = None
    background_color: Optional[str] = None
    border_color: Optional[str] = None
    border_width: Optional[float] = None 