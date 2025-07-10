"""
OCR router
"""

from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime

from ..database.connection import get_db_session
from ..schemas.ocr_schemas import OCRProcessRequest, OCRProcessResponse, OCRResultResponse
from ..models.users import User
from ..models.images import Image
from ..models.ocr_results import OCRResult
from ..services.google_document_ai_service import google_doc_ai_service
from ..services.supabase_service import supabase_service
from .auth import get_current_user_dependency

router = APIRouter()


@router.post("/process/{image_id}", response_model=OCRProcessResponse)
async def process_image_ocr(
    image_id: int,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user_dependency),
    db: Session = Depends(get_db_session)
):
    """
    Process image with OCR
    """
    # Get image
    image = db.query(Image).filter(
        Image.id == image_id,
        Image.user_id == current_user.id
    ).first()
    
    if not image:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Image not found"
        )
    
    # Check if already processed
    existing_result = db.query(OCRResult).filter(
        OCRResult.image_id == image_id
    ).first()
    
    if existing_result:
        return OCRProcessResponse(
            success=True,
            processing_time=existing_result.processing_time,
            ocr_result=OCRResultResponse.from_orm(existing_result)
        )
    
    # Update image status
    image.processing_status = "processing"
    db.commit()
    
    try:
        # Get image content from Supabase Storage
        # Note: In a real implementation, you'd fetch the image content
        # For now, we'll simulate with a placeholder
        image_content = b""  # This should be fetched from storage
        
        # Process with Google Document AI
        ocr_result = await google_doc_ai_service.process_layout_extraction(
            image_content=image_content,
            mime_type=image.content_type
        )
        
        if not ocr_result["success"]:
            # Update image status
            image.processing_status = "failed"
            image.processing_error = ocr_result["error"]
            db.commit()
            
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"OCR processing failed: {ocr_result['error']}"
            )
        
        # Create OCR result record
        ocr_result_record = OCRResult(
            image_id=image_id,
            processor_type="google_document_ai",
            processing_time=ocr_result["processing_time"],
            confidence_score=ocr_result["confidence_score"],
            text_blocks=[],  # Would be populated from actual OCR result
            layout_elements=[],  # Would be populated from actual OCR result
            bounding_boxes=[],  # Would be populated from actual OCR result
            has_error=False
        )
        
        db.add(ocr_result_record)
        
        # Update image status
        image.processing_status = "completed"
        image.is_processed = True
        image.processed_at = datetime.utcnow()
        
        db.commit()
        db.refresh(ocr_result_record)
        
        return OCRProcessResponse(
            success=True,
            processing_time=ocr_result["processing_time"],
            ocr_result=OCRResultResponse.from_orm(ocr_result_record),
            canvas_elements=ocr_result.get("canvas_elements", [])
        )
        
    except Exception as e:
        # Update image status
        image.processing_status = "failed"
        image.processing_error = str(e)
        db.commit()
        
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"OCR processing failed: {str(e)}"
        )


@router.get("/results/{image_id}", response_model=OCRResultResponse)
async def get_ocr_result(
    image_id: int,
    current_user: User = Depends(get_current_user_dependency),
    db: Session = Depends(get_db_session)
):
    """
    Get OCR result for an image
    """
    # Verify image ownership
    image = db.query(Image).filter(
        Image.id == image_id,
        Image.user_id == current_user.id
    ).first()
    
    if not image:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Image not found"
        )
    
    # Get OCR result
    ocr_result = db.query(OCRResult).filter(
        OCRResult.image_id == image_id
    ).first()
    
    if not ocr_result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="OCR result not found"
        )
    
    return OCRResultResponse.from_orm(ocr_result)


@router.get("/results/", response_model=List[OCRResultResponse])
async def list_ocr_results(
    skip: int = 0,
    limit: int = 10,
    current_user: User = Depends(get_current_user_dependency),
    db: Session = Depends(get_db_session)
):
    """
    List OCR results for user's images
    """
    # Get user's images
    user_image_ids = db.query(Image.id).filter(
        Image.user_id == current_user.id
    ).subquery()
    
    # Get OCR results for user's images
    ocr_results = db.query(OCRResult).filter(
        OCRResult.image_id.in_(user_image_ids)
    ).offset(skip).limit(limit).all()
    
    return [OCRResultResponse.from_orm(result) for result in ocr_results]


@router.delete("/results/{image_id}")
async def delete_ocr_result(
    image_id: int,
    current_user: User = Depends(get_current_user_dependency),
    db: Session = Depends(get_db_session)
):
    """
    Delete OCR result for an image
    """
    # Verify image ownership
    image = db.query(Image).filter(
        Image.id == image_id,
        Image.user_id == current_user.id
    ).first()
    
    if not image:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Image not found"
        )
    
    # Delete OCR result
    ocr_result = db.query(OCRResult).filter(
        OCRResult.image_id == image_id
    ).first()
    
    if not ocr_result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="OCR result not found"
        )
    
    db.delete(ocr_result)
    
    # Reset image processing status
    image.processing_status = "pending"
    image.is_processed = False
    image.processed_at = None
    
    db.commit()
    
    return {"message": "OCR result deleted successfully"} 