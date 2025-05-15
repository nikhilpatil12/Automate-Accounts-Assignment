# Receipt Processing System

This system automates the processing of scanned receipts using OCR/AI techniques. It provides a REST API for uploading, validating, and extracting information from PDF receipts.

## Prerequisites

- Python 3.8+
- Tesseract OCR
- Poppler (for PDF processing)

### Installing Prerequisites

#### macOS
```bash
brew install tesseract
brew install poppler
```

#### Ubuntu/Debian
```bash
sudo apt-get update
sudo apt-get install tesseract-ocr
sudo apt-get install poppler-utils
```

## Setup

1. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Initialize the database:
```bash
python app/init_db.py
```

4. Start the server:
```bash
uvicorn app.main:app --reload
```

The API will be available at http://localhost:8000

## API Documentation

### POST /upload
Upload a PDF receipt file.

Request:
- Multipart form data with 'file' field containing the PDF

Response:
```json
{
    "id": "1",
    "file_name": "receipt.pdf",
    "is_valid": true,
    "created_at": "2024-02-20T12:00:00"
}
```

### POST /validate/{file_id}
Validate an uploaded PDF file.

Response:
```json
{
    "id": "1",
    "is_valid": true,
    "invalid_reason": null
}
```

### POST /process/{file_id}
Process a receipt using OCR to extract information.

Response:
```json
{
    "id": "1",
    "merchant_name": "Store Name",
    "total_amount": 123.45,
    "purchased_at": "2024-02-20T12:00:00"
}
```

### GET /receipts
List all processed receipts.

Response:
```json
{
    "receipts": [
        {
            "id": "1",
            "merchant_name": "Store Name",
            "total_amount": 123.45,
            "purchased_at": "2024-02-20T12:00:00"
        }
    ]
}
```

### GET /receipts/{id}
Get details of a specific receipt.

Response:
```json
{
    "id": "1",
    "merchant_name": "Store Name",
    "total_amount": 123.45,
    "purchased_at": "2024-02-20T12:00:00",
    "file_path": "/path/to/receipt.pdf"
}
```

## Project Structure

```
.
├── app/
│   ├── __init__.py
│   ├── main.py
│   ├── database.py
│   ├── models.py
│   ├── schemas.py
│   └── services/
│       ├── __init__.py
│       ├── ocr.py
│       └── pdf.py
├── receipts/
├── requirements.txt
└── README.md
``` 