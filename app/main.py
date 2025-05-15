from fastapi import FastAPI, File, UploadFile, HTTPException, Depends
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
import os
from typing import List
import logging

from . import models, schemas
from .database import engine, get_db
from .services.pdf import PDFService
from .services.ocr import OCRService

# Create database tables
models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="Receipt Processing System")

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@app.post("/upload", response_model=schemas.ReceiptFile)
async def upload_receipt(
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    """Upload a receipt file."""
    try:
        if not file.filename.lower().endswith('.pdf'):
            raise HTTPException(status_code=400, detail="Only PDF files are allowed")

        # Read file content and calculate hash
        file_content = await file.read()
        file_hash = PDFService.calculate_file_hash(file_content)

        # Check for existing receipt with same hash
        existing_file = db.query(models.ReceiptFile).filter(
            models.ReceiptFile.file_hash == file_hash
        ).first()

        if existing_file:
            logger.info(f"Duplicate receipt detected with hash: {file_hash}")
            return existing_file

        # Save the uploaded file
        file_path = PDFService.save_uploaded_file(file_content, file.filename)

        # Create database entry
        db_file = models.ReceiptFile(
            file_name=file.filename,
            file_path=file_path,
            file_hash=file_hash
        )
        db.add(db_file)
        db.commit()
        db.refresh(db_file)

        return db_file

    except Exception as e:
        logger.error(f"Error uploading file: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/validate/{file_id}", response_model=schemas.ValidationResponse)
def validate_receipt(file_id: int, db: Session = Depends(get_db)):
    """Validate a receipt file."""
    try:
        db_file = db.query(models.ReceiptFile).filter(models.ReceiptFile.id == file_id).first()
        if not db_file:
            raise HTTPException(status_code=404, detail="Receipt file not found")

        is_valid, reason = PDFService.validate_pdf(db_file.file_path)
        
        # Update database
        db_file.is_valid = is_valid
        db_file.invalid_reason = reason if not is_valid else None
        db.commit()
        db.refresh(db_file)

        return {
            "id": db_file.id,
            "is_valid": is_valid,
            "invalid_reason": reason if not is_valid else None
        }

    except Exception as e:
        logger.error(f"Error validating file: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/process/{file_id}", response_model=schemas.ProcessingResponse)
def process_receipt(file_id: int, db: Session = Depends(get_db)):
    """Process a receipt file using OCR."""
    try:
        db_file = db.query(models.ReceiptFile).filter(models.ReceiptFile.id == file_id).first()
        if not db_file:
            raise HTTPException(status_code=404, detail="Receipt file not found")

        if not db_file.is_valid:
            raise HTTPException(status_code=400, detail="Cannot process invalid file")

        # Extract text using OCR
        text = OCRService.extract_text_from_pdf(db_file.file_path)
        receipt_info = OCRService.extract_receipt_info(text)

        # Create or update receipt record
        db_receipt = db.query(models.Receipt).filter(
            models.Receipt.receipt_file_id == file_id
        ).first()

        if not db_receipt:
            db_receipt = models.Receipt(
                receipt_file_id=file_id,
                purchased_at=receipt_info["purchased_at"],
                merchant_name=receipt_info["merchant_name"],
                total_amount=receipt_info["total_amount"]
            )
            db.add(db_receipt)
        else:
            db_receipt.purchased_at = receipt_info["purchased_at"]
            db_receipt.merchant_name = receipt_info["merchant_name"]
            db_receipt.total_amount = receipt_info["total_amount"]

        # Mark file as processed
        db_file.is_processed = True
        
        db.commit()
        db.refresh(db_receipt)

        return {
            "id": db_receipt.id,
            "merchant_name": db_receipt.merchant_name,
            "total_amount": db_receipt.total_amount,
            "purchased_at": db_receipt.purchased_at
        }

    except Exception as e:
        logger.error(f"Error processing file: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/receipts", response_model=List[schemas.Receipt])
def list_receipts(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """List all processed receipts."""
    receipts = db.query(models.Receipt).offset(skip).limit(limit).all()
    return receipts

@app.get("/receipts/{receipt_id}", response_model=schemas.Receipt)
def get_receipt(receipt_id: int, db: Session = Depends(get_db)):
    """Get details of a specific receipt."""
    receipt = db.query(models.Receipt).filter(models.Receipt.id == receipt_id).first()
    if not receipt:
        raise HTTPException(status_code=404, detail="Receipt not found")
    return receipt 