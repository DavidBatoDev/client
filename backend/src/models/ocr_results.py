"""
OCR Results model for storing raw OCR processing results
"""

from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey, Boolean, Float, JSON
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from ..database.base import Base


class OCRResult(Base):
    """
    OCRResult model for storing raw OCR processing results
    """
    __tablename__ = "ocr_results"

    id = Column(Integer, primary_key=True, index=True)
    image_id = Column(Integer, ForeignKey("images.id"), nullable=False)
    
    # Processing information
    processor_type = Column(String(100), nullable=False)  # google_document_ai, tesseract, etc.
    processor_version = Column(String(50), nullable=True)
    processing_time = Column(Float, nullable=True)  # seconds
    
    # OCR results
    full_text = Column(Text, nullable=True)
    confidence_score = Column(Float, nullable=True)
    
    # Structured data
    text_blocks = Column(JSON, nullable=True)  # Array of text blocks with positions
    layout_elements = Column(JSON, nullable=True)  # Array of detected UI elements
    bounding_boxes = Column(JSON, nullable=True)  # Raw bounding box data
    
    # Google Document AI specific
    document_ai_response = Column(JSON, nullable=True)  # Raw response from Document AI
    
    # Processing metadata
    page_count = Column(Integer, default=1)
    detected_language = Column(String(10), nullable=True)
    rotation_angle = Column(Float, default=0.0)
    
    # Error handling
    processing_error = Column(Text, nullable=True)
    has_error = Column(Boolean, default=False)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    image = relationship("Image", back_populates="ocr_results")
    
    def __repr__(self):
        return f"<OCRResult(id={self.id}, image_id={self.image_id}, processor={self.processor_type})>" 