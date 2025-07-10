"""
Layout Pydantic schemas
"""

from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import datetime


class LayoutElementBase(BaseModel):
    """
    Base layout element schema
    """
    element_type: str
    element_id: str
    x: float
    y: float
    width: float
    height: float
    content: Optional[str] = None
    font_size: Optional[float] = None
    font_family: Optional[str] = None
    font_weight: Optional[str] = None
    text_align: Optional[str] = None
    background_color: Optional[str] = None
    text_color: Optional[str] = None
    border_color: Optional[str] = None
    border_width: Optional[float] = None
    border_radius: Optional[float] = None
    opacity: float = 1.0
    rotation: float = 0.0
    z_index: int = 0
    confidence_score: Optional[float] = None
    original_category: Optional[str] = None
    is_visible: bool = True
    is_locked: bool = False
    metadata: Optional[Dict[str, Any]] = None


class LayoutElementCreate(LayoutElementBase):
    """
    Schema for creating a layout element
    """
    pass


class LayoutElementUpdate(BaseModel):
    """
    Schema for updating a layout element
    """
    x: Optional[float] = None
    y: Optional[float] = None
    width: Optional[float] = None
    height: Optional[float] = None
    content: Optional[str] = None
    font_size: Optional[float] = None
    font_family: Optional[str] = None
    font_weight: Optional[str] = None
    text_align: Optional[str] = None
    background_color: Optional[str] = None
    text_color: Optional[str] = None
    border_color: Optional[str] = None
    border_width: Optional[float] = None
    border_radius: Optional[float] = None
    opacity: Optional[float] = None
    rotation: Optional[float] = None
    z_index: Optional[int] = None
    is_visible: Optional[bool] = None
    is_locked: Optional[bool] = None
    metadata: Optional[Dict[str, Any]] = None


class LayoutElementResponse(LayoutElementBase):
    """
    Schema for layout element response
    """
    id: int
    layout_id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class LayoutBase(BaseModel):
    """
    Base layout schema
    """
    name: str
    description: Optional[str] = None
    canvas_width: int
    canvas_height: int
    is_active: bool = True
    is_template: bool = False
    layout_data: Optional[Dict[str, Any]] = None


class LayoutCreate(LayoutBase):
    """
    Schema for creating a layout
    """
    elements: Optional[List[LayoutElementCreate]] = []


class LayoutUpdate(BaseModel):
    """
    Schema for updating a layout
    """
    name: Optional[str] = None
    description: Optional[str] = None
    canvas_width: Optional[int] = None
    canvas_height: Optional[int] = None
    is_active: Optional[bool] = None
    is_template: Optional[bool] = None
    layout_data: Optional[Dict[str, Any]] = None


class LayoutResponse(LayoutBase):
    """
    Schema for layout response
    """
    id: int
    user_id: int
    image_id: int
    version: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    elements: List[LayoutElementResponse] = []
    
    class Config:
        from_attributes = True


class LayoutCanvasUpdate(BaseModel):
    """
    Schema for updating canvas layout
    """
    elements: List[LayoutElementUpdate]
    canvas_width: Optional[int] = None
    canvas_height: Optional[int] = None
    layout_data: Optional[Dict[str, Any]] = None 