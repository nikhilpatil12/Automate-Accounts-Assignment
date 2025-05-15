import pytesseract
from pdf2image import convert_from_path
import re
from datetime import datetime
from typing import Optional, Dict, Any
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class OCRService:
    @staticmethod
    def extract_text_from_pdf(file_path: str) -> str:
        """Convert PDF to image and extract text using Tesseract OCR."""
        try:
            # Convert PDF to image
            images = convert_from_path(file_path)
            
            # Extract text from each page
            text = ""
            for image in images:
                text += pytesseract.image_to_string(image)
            
            return text
        except Exception as e:
            logger.error(f"Error extracting text from PDF: {str(e)}")
            raise

    @staticmethod
    def extract_receipt_info(text: str) -> Dict[str, Any]:
        """Extract relevant information from the OCR text."""
        result = {
            "merchant_name": None,
            "total_amount": None,
            "purchased_at": None,
            "items": []
        }

        # Split text into lines
        lines = text.split('\n')
        
        # Try to find merchant name (usually in the first few lines)
        for line in lines[:5]:
            if line.strip() and not any(word in line.lower() for word in ['receipt', 'invoice', 'tel', 'phone']):
                result["merchant_name"] = line.strip()
                break

        # Find total amount - only match "Total:" (case insensitive)
        total_patterns = [
            r'total\s:\s*[\$£€]?\s*(\d+[.,]\d{2})',  # matches "Total: $123.45"
            r'total\s:\s*[\$£€]?\s*(\d{1,3}(?:,\d{3})*\.\d{2})',  # matches "Total: $1,234.56"
            r'total\s:\s*(\d+[.,]\d{2})',  # matches "Total: 123.45"
            r'total\s:\s*(\d{1,3}(?:,\d{3})*\.\d{2})',  # matches "Total: 1,234.56"

            r'total\s*[\$£€]?\s*(\d+[.,]\d{2})',  # matches "Total $123.45"
            r'total\s*[\$£€]?\s*(\d{1,3}(?:,\d{3})*\.\d{2})',  # matches "Total $1,234.56"
            r'total\s*(\d+[.,]\d{2})',  # matches "Total 123.45"
            r'total\s*(\d{1,3}(?:,\d{3})*\.\d{2})',  # matches "Total 1,234.56"
        ]
        
        max_total = 0
        for pattern in total_patterns:
            matches = re.finditer(pattern, text.lower())
            for match in matches:
                try:
                    amount = float(match.group(1).replace(',', ''))
                    if amount > max_total:
                        max_total = amount
                        result["total_amount"] = amount
                    # Remove the break to find all matches, and then return the highest amount
                    # break
                except ValueError:
                    continue
            # Remove the break to find all matches, and then return the highest amount
            # if result["total_amount"]:
            #     break

        # Find date in mm/dd/yy or mm/dd/yyyy format
        date_patterns = [
            r'(\d{1,2}/\d{1,2}/\d{4})',  # matches both 3/10/2024 and 03/10/2024
            r'(\d{1,2}/\d{1,2}/\d{2})',  # matches both 3/10/24 and 03/10/24
        ]

        for pattern in date_patterns:
            matches = re.finditer(pattern, text)
            for match in matches:
                try:
                    date_str = match.group(1)
                    if len(date_str.split('/')[-1]) == 2:
                        # Convert 2-digit year to 4-digit year
                        month, day, year = date_str.split('/')
                        year = int(year)
                        # Assume years 00-69 are 2000s, 70-99 are 1900s
                        if year < 70:
                            year += 2000
                        else:
                            year += 1900
                        date_str = f"{month}/{day}/{year}"
                    
                    result["purchased_at"] = datetime.strptime(date_str, '%m/%d/%Y')
                    break
                except ValueError:
                    continue
            if result["purchased_at"]:
                break

        # Extract items (this is a basic implementation)
        item_pattern = r'(\d+)\s*[xX]\s*[\$£€]?\s*(\d+[.,]\d{2})'
        for line in lines:
            match = re.search(item_pattern, line)
            if match:
                try:
                    quantity = float(match.group(1))
                    unit_price = float(match.group(2).replace(',', '.'))
                    description = line.split(match.group(0))[0].strip()
                    if description:
                        result["items"].append({
                            "description": description,
                            "quantity": quantity,
                            "unit_price": unit_price,
                            "total_price": quantity * unit_price
                        })
                except ValueError:
                    continue

        return result 