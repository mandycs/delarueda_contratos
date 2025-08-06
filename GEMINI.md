# Gemini Project Context: Contract Signing Microservice

## Project Overview

The goal of this project is to develop a backend microservice to manage the workflow of signing contracts or designs that are initially created on a frontend application. The service will handle receiving a design image, incorporating client data, generating a PDF document, providing endpoints for preview and signing, and storing the final signed document with its metadata.

## Key Functionalities & API Endpoints

The microservice will expose a RESTful API to handle the contract signing flow:

### 1. Submit Initial Design and Data
Receives the client-generated design and associated data.

- **Endpoint:** `POST /contracts/`
- **Request Body:**
  ```json
  {
    "client_data": {
      "name": "Mandy Vega",
      "email": "mandy@ejemplo.com"
    },
    "design_image": "<file>",
    "photo_reference": "<optional_file>"
  }
  ```

### 2. Preview Generated Contract
Allows for the preview of the generated, unsigned PDF document.

- **Endpoint:** `GET /contracts/{contract_id}/preview`
- **Response:** The contract as a rendered PDF or an image preview.

### 3. Sign the Contract
Receives the client's signature as an image and embeds it into the PDF.

- **Endpoint:** `POST /contracts/{contract_id}/sign`
- **Request Body:**
  ```json
  {
    "signature_image": "<file>",
    "signed_by": "Mandy Vega"
  }
  ```
- **Note:** The service should store traceability information like IP address, user-agent, and a timestamp.

### 4. Download Signed Contract
Provides the final, signed PDF document.

- **Endpoint:** `GET /contracts/{contract_id}/signed`
- **Response:** The signed PDF file.

## Recommended Technology Stack

- **Web Framework:** FastAPI
- **PDF Generation:** ReportLab, FPDF, or a combination of Pillow + PyPDF2
- **Image Handling:** Pillow or pdf2image
- **Database:** MongoDB (for flexible metadata) or PostgreSQL
- **Storage:** Local filesystem or a cloud solution like Amazon S3
- **Unique IDs / Hashing:** UUID and hashlib for tracking

## Building and Running

**1. Activate Virtual Environment:**
```bash
source venv/bin/activate
```

**2. Install Dependencies:**
```bash
# It is recommended to create a requirements.txt file
pip install fastapi uvicorn "python-multipart" Pillow reportlab pymongo
```

**3. Run the Application:**
```bash
# TODO: Create the main application file (e.g., main.py)
uvicorn main:app --reload
```

**4. Run Tests:**
```bash
# TODO: Set up a testing framework like pytest
pytest
```

## Development Conventions

- **API:** Follow the RESTful principles outlined in the endpoints above.
- **Code Style:** Adhere to PEP 8 standards for Python code.
- **Dependencies:** Manage all Python dependencies within the `venv` virtual environment and list them in a `requirements.txt` file.
- **IDs:** Use UUIDs for `contract_id` to ensure uniqueness.
