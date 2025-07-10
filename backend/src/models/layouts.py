"""
Layout models for storing canvas layouts and elements
"""

from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey, Boolean, Float, JSON
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from ..database.base import Base


class Layout(Base):
    """
    Layout model for storing canvas layouts
    """
    __tablename__ = "layouts"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    image_id = Column(Integer, ForeignKey("images.id"), nullable=False)
    
    # Layout information
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    version = Column(Integer, default=1)
    
    # Canvas dimensions
    canvas_width = Column(Integer, nullable=False)
    canvas_height = Column(Integer, nullable=False)
    
    # Layout state
    is_active = Column(Boolean, default=True)
    is_template = Column(Boolean, default=False)
    layout_data = Column(JSON, nullable=True)  # Store complete layout as JSON
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    user = relationship("User", back_populates="layouts")
    image = relationship("Image", back_populates="layouts")
    elements = relationship("LayoutElement", back_populates="layout", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Layout(id={self.id}, name={self.name}, user_id={self.user_id})>"


class LayoutElement(Base):
    """
    LayoutElement model for storing individual layout elements
    """
    __tablename__ = "layout_elements"

    id = Column(Integer, primary_key=True, index=True)
    layout_id = Column(Integer, ForeignKey("layouts.id"), nullable=False)
    
    # Element identification
    element_type = Column(String(50), nullable=False)  # rectangle, circle, text, image
    element_id = Column(String(255), nullable=False)  # unique identifier within layout
    
    # Position and size
    x = Column(Float, nullable=False)
    y = Column(Float, nullable=False)
    width = Column(Float, nullable=False)
    height = Column(Float, nullable=False)
    
    # Element properties
    content = Column(Text, nullable=True)  # text content for text elements
    font_size = Column(Float, nullable=True)
    font_family = Column(String(100), nullable=True)
    font_weight = Column(String(20), nullable=True)
    text_align = Column(String(20), nullable=True)
    
    # Colors and styles
    background_color = Column(String(20), nullable=True)
    text_color = Column(String(20), nullable=True)
    border_color = Column(String(20), nullable=True)
    border_width = Column(Float, nullable=True)
    border_radius = Column(Float, nullable=True)
    
    # Additional properties
    opacity = Column(Float, default=1.0)
    rotation = Column(Float, default=0.0)
    z_index = Column(Integer, default=0)
    
    # OCR-related data
    confidence_score = Column(Float, nullable=True)
    original_category = Column(String(100), nullable=True)  # button, username, etc.
    
    # Element state
    is_visible = Column(Boolean, default=True)
    is_locked = Column(Boolean, default=False)
    
    # Metadata
    metadata = Column(JSON, nullable=True)  # Additional element-specific data
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    layout = relationship("Layout", back_populates="elements")
    
    def __repr__(self):
        return f"<LayoutElement(id={self.id}, type={self.element_type}, layout_id={self.layout_id})>" 