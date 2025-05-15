import os
from typing import Tuple
import logging
from pdf2image import convert_from_path
from pdf2image.exceptions import PDFPageCountError
import hashlib

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class PDFService:
    @staticmethod
    def calculate_file_hash(file_content: bytes) -> str:
        """Calculate SHA-256 hash of file content."""
        return hashlib.sha256(file_content).hexdigest()

    @staticmethod
    def validate_pdf(file_path: str) -> Tuple[bool, str]:
        """
        Validate if the file is a valid PDF and can be processed.
        Returns a tuple of (is_valid, reason).
        """
        try:
            # Check if file exists
            if not os.path.exists(file_path):
                return False, "File does not exist"

            # Check file extension
            if not file_path.lower().endswith('.pdf'):
                return False, "File is not a PDF"

            # Check file size (max 10MB)
            if os.path.getsize(file_path) > 10 * 1024 * 1024:
                return False, "File size exceeds 10MB limit"

            # Try to convert first page to image to validate PDF
            convert_from_path(file_path, first_page=1, last_page=1)
            
            return True, ""

        except PDFPageCountError:
            return False, "Invalid PDF format or empty PDF"
        except Exception as e:
            logger.error(f"Error validating PDF: {str(e)}")
            return False, f"Error validating PDF: {str(e)}"

    @staticmethod
    def save_uploaded_file(file_content: bytes, file_name: str, upload_dir: str = "receipts") -> str:
        """
        Save an uploaded file to the specified directory.
        Returns the file path.
        """
        try:
            # Create upload directory if it doesn't exist
            os.makedirs(upload_dir, exist_ok=True)

            # Generate unique filename using hash
            file_hash = PDFService.calculate_file_hash(file_content)
            extension = os.path.splitext(file_name)[1]
            new_file_name = f"{file_hash}{extension}"
            file_path = os.path.join(upload_dir, new_file_name)

            # Save the file if it doesn't exist
            if not os.path.exists(file_path):
                with open(file_path, "wb") as f:
                    f.write(file_content)

            return file_path

        except Exception as e:
            logger.error(f"Error saving file: {str(e)}")
            raise 