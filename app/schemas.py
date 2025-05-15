from pydantic import BaseModel
from datetime import datetime
from typing import List, Optional

class ReceiptFileBase(BaseModel):
    file_name: str
    file_path: str
    file_hash: str

class ReceiptFileCreate(ReceiptFileBase):
    pass

class ReceiptFile(ReceiptFileBase):
    id: int
    is_valid: Optional[bool] = None
    invalid_reason: Optional[str] = None
    is_processed: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class ReceiptItemBase(BaseModel):
    description: Optional[str] = None
    quantity: Optional[float] = None
    unit_price: Optional[float] = None
    total_price: Optional[float] = None

class ReceiptItemCreate(ReceiptItemBase):
    pass

class ReceiptItem(ReceiptItemBase):
    id: int
    receipt_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class ReceiptBase(BaseModel):
    purchased_at: Optional[datetime] = None
    merchant_name: Optional[str] = None
    total_amount: Optional[float] = None

class ReceiptCreate(ReceiptBase):
    receipt_file_id: int

class Receipt(ReceiptBase):
    id: int
    receipt_file_id: int
    created_at: datetime
    updated_at: datetime
    # items: List[ReceiptItem] = []

    class Config:
        from_attributes = True

class ValidationResponse(BaseModel):
    id: int
    is_valid: bool
    invalid_reason: Optional[str] = None

class ProcessingResponse(BaseModel):
    id: int
    merchant_name: Optional[str]
    total_amount: Optional[float]
    purchased_at: Optional[datetime] 