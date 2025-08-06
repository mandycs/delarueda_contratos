import os
import uuid
import shutil
from fastapi import UploadFile


# Storage configuration
UPLOADS_DIR = "storage/uploads"
CONTRACTS_DIR = "storage/contracts"


def ensure_directories():
    """Ensure storage directories exist"""
    os.makedirs(UPLOADS_DIR, exist_ok=True)
    os.makedirs(CONTRACTS_DIR, exist_ok=True)


def save_uploaded_file(upload_file: UploadFile, directory: str = UPLOADS_DIR) -> str:
    """
    Save uploaded file and return the path
    
    Args:
        upload_file: The uploaded file
        directory: Directory to save file in
        
    Returns:
        str: Path to saved file
    """
    file_extension = upload_file.filename.split('.')[-1]
    filename = f"{uuid.uuid4()}.{file_extension}"
    file_path = os.path.join(directory, filename)
    
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(upload_file.file, buffer)
    
    return file_path


def delete_file_if_exists(file_path: str) -> bool:
    """
    Delete file if it exists
    
    Args:
        file_path: Path to file to delete
        
    Returns:
        bool: True if file was deleted or didn't exist, False if error occurred
    """
    try:
        if file_path and os.path.exists(file_path):
            os.remove(file_path)
        return True
    except Exception:
        return False