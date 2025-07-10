"""
Layouts router
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from ..database.connection import get_db_session
from ..schemas.layout_schemas import (
    LayoutCreate, LayoutUpdate, LayoutResponse, LayoutCanvasUpdate,
    LayoutElementCreate, LayoutElementUpdate, LayoutElementResponse
)
from ..models.users import User
from ..models.images import Image
from ..models.layouts import Layout, LayoutElement
from .auth import get_current_user_dependency

router = APIRouter()


@router.post("/", response_model=LayoutResponse)
async def create_layout(
    layout_data: LayoutCreate,
    current_user: User = Depends(get_current_user_dependency),
    db: Session = Depends(get_db_session)
):
    """
    Create a new layout
    """
    # Create layout
    layout = Layout(
        user_id=current_user.id,
        image_id=layout_data.image_id,
        name=layout_data.name,
        description=layout_data.description,
        canvas_width=layout_data.canvas_width,
        canvas_height=layout_data.canvas_height,
        is_active=layout_data.is_active,
        is_template=layout_data.is_template,
        layout_data=layout_data.layout_data
    )
    
    db.add(layout)
    db.commit()
    db.refresh(layout)
    
    # Create elements if provided
    if layout_data.elements:
        for element_data in layout_data.elements:
            element = LayoutElement(
                layout_id=layout.id,
                **element_data.dict()
            )
            db.add(element)
        
        db.commit()
    
    # Load elements for response
    db.refresh(layout)
    
    return LayoutResponse.from_orm(layout)


@router.get("/", response_model=List[LayoutResponse])
async def list_layouts(
    skip: int = 0,
    limit: int = 10,
    image_id: int = None,
    current_user: User = Depends(get_current_user_dependency),
    db: Session = Depends(get_db_session)
):
    """
    List user's layouts
    """
    query = db.query(Layout).filter(Layout.user_id == current_user.id)
    
    if image_id:
        query = query.filter(Layout.image_id == image_id)
    
    layouts = query.offset(skip).limit(limit).all()
    
    return [LayoutResponse.from_orm(layout) for layout in layouts]


@router.get("/{layout_id}", response_model=LayoutResponse)
async def get_layout(
    layout_id: int,
    current_user: User = Depends(get_current_user_dependency),
    db: Session = Depends(get_db_session)
):
    """
    Get specific layout by ID
    """
    layout = db.query(Layout).filter(
        Layout.id == layout_id,
        Layout.user_id == current_user.id
    ).first()
    
    if not layout:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Layout not found"
        )
    
    return LayoutResponse.from_orm(layout)


@router.put("/{layout_id}", response_model=LayoutResponse)
async def update_layout(
    layout_id: int,
    layout_data: LayoutUpdate,
    current_user: User = Depends(get_current_user_dependency),
    db: Session = Depends(get_db_session)
):
    """
    Update layout
    """
    layout = db.query(Layout).filter(
        Layout.id == layout_id,
        Layout.user_id == current_user.id
    ).first()
    
    if not layout:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Layout not found"
        )
    
    # Update fields
    for field, value in layout_data.dict(exclude_unset=True).items():
        setattr(layout, field, value)
    
    # Increment version
    layout.version += 1
    
    db.commit()
    db.refresh(layout)
    
    return LayoutResponse.from_orm(layout)


@router.put("/{layout_id}/canvas", response_model=LayoutResponse)
async def update_layout_canvas(
    layout_id: int,
    canvas_data: LayoutCanvasUpdate,
    current_user: User = Depends(get_current_user_dependency),
    db: Session = Depends(get_db_session)
):
    """
    Update layout canvas with elements
    """
    layout = db.query(Layout).filter(
        Layout.id == layout_id,
        Layout.user_id == current_user.id
    ).first()
    
    if not layout:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Layout not found"
        )
    
    # Update canvas dimensions if provided
    if canvas_data.canvas_width:
        layout.canvas_width = canvas_data.canvas_width
    if canvas_data.canvas_height:
        layout.canvas_height = canvas_data.canvas_height
    if canvas_data.layout_data:
        layout.layout_data = canvas_data.layout_data
    
    # Update elements
    for element_data in canvas_data.elements:
        element = db.query(LayoutElement).filter(
            LayoutElement.layout_id == layout_id,
            LayoutElement.element_id == element_data.element_id
        ).first()
        
        if element:
            # Update existing element
            for field, value in element_data.dict(exclude_unset=True).items():
                if field != "element_id":  # Don't update the ID
                    setattr(element, field, value)
        else:
            # Create new element
            element = LayoutElement(
                layout_id=layout_id,
                **element_data.dict()
            )
            db.add(element)
    
    # Increment version
    layout.version += 1
    
    db.commit()
    db.refresh(layout)
    
    return LayoutResponse.from_orm(layout)


@router.delete("/{layout_id}")
async def delete_layout(
    layout_id: int,
    current_user: User = Depends(get_current_user_dependency),
    db: Session = Depends(get_db_session)
):
    """
    Delete a layout
    """
    layout = db.query(Layout).filter(
        Layout.id == layout_id,
        Layout.user_id == current_user.id
    ).first()
    
    if not layout:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Layout not found"
        )
    
    db.delete(layout)
    db.commit()
    
    return {"message": "Layout deleted successfully"}


@router.post("/{layout_id}/elements", response_model=LayoutElementResponse)
async def create_layout_element(
    layout_id: int,
    element_data: LayoutElementCreate,
    current_user: User = Depends(get_current_user_dependency),
    db: Session = Depends(get_db_session)
):
    """
    Create a new layout element
    """
    # Verify layout ownership
    layout = db.query(Layout).filter(
        Layout.id == layout_id,
        Layout.user_id == current_user.id
    ).first()
    
    if not layout:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Layout not found"
        )
    
    # Create element
    element = LayoutElement(
        layout_id=layout_id,
        **element_data.dict()
    )
    
    db.add(element)
    db.commit()
    db.refresh(element)
    
    return LayoutElementResponse.from_orm(element)


@router.get("/{layout_id}/elements", response_model=List[LayoutElementResponse])
async def list_layout_elements(
    layout_id: int,
    current_user: User = Depends(get_current_user_dependency),
    db: Session = Depends(get_db_session)
):
    """
    List elements for a layout
    """
    # Verify layout ownership
    layout = db.query(Layout).filter(
        Layout.id == layout_id,
        Layout.user_id == current_user.id
    ).first()
    
    if not layout:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Layout not found"
        )
    
    elements = db.query(LayoutElement).filter(
        LayoutElement.layout_id == layout_id
    ).all()
    
    return [LayoutElementResponse.from_orm(element) for element in elements]


@router.delete("/{layout_id}/elements/{element_id}")
async def delete_layout_element(
    layout_id: int,
    element_id: int,
    current_user: User = Depends(get_current_user_dependency),
    db: Session = Depends(get_db_session)
):
    """
    Delete a layout element
    """
    # Verify layout ownership
    layout = db.query(Layout).filter(
        Layout.id == layout_id,
        Layout.user_id == current_user.id
    ).first()
    
    if not layout:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Layout not found"
        )
    
    # Delete element
    element = db.query(LayoutElement).filter(
        LayoutElement.id == element_id,
        LayoutElement.layout_id == layout_id
    ).first()
    
    if not element:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Element not found"
        )
    
    db.delete(element)
    db.commit()
    
    return {"message": "Element deleted successfully"} 