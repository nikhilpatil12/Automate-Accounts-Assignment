from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from .database import Base

class ReceiptFile(Base):
    __tablename__ = "receipt_file"

    id = Column(Integer, primary_key=True, index=True)
    file_name = Column(String, nullable=False)
    file_path = Column(String, nullable=False)
    file_hash = Column(String, nullable=False, unique=True, index=True)
    is_valid = Column(Boolean, default=None)
    invalid_reason = Column(String, nullable=True)
    is_processed = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    receipt = relationship("Receipt", back_populates="receipt_file", uselist=False)

class Receipt(Base):
    __tablename__ = "receipt"

    id = Column(Integer, primary_key=True, index=True)
    receipt_file_id = Column(Integer, ForeignKey("receipt_file.id"), unique=True)
    purchased_at = Column(DateTime, nullable=True)
    merchant_name = Column(String, nullable=True)
    total_amount = Column(Float, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    receipt_file = relationship("ReceiptFile", back_populates="receipt")

    # Additional fields for receipt items
#     items = relationship("ReceiptItem", back_populates="receipt")

# class ReceiptItem(Base):
#     __tablename__ = "receipt_item"

#     id = Column(Integer, primary_key=True, index=True)
#     receipt_id = Column(Integer, ForeignKey("receipt.id"))
#     description = Column(String, nullable=True)
#     quantity = Column(Float, nullable=True)
#     unit_price = Column(Float, nullable=True)
#     total_price = Column(Float, nullable=True)
#     created_at = Column(DateTime, default=datetime.utcnow)
#     updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

#     receipt = relationship("Receipt", back_populates="items") 