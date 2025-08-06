from typing import List
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from .. import auth, crud, schemas
from ..database import get_db

router = APIRouter(prefix="/default-texts", tags=["default-texts"])


@router.get("/", response_model=List[schemas.DefaultText])
async def list_default_texts(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user = Depends(auth.get_current_user)
):
    return crud.get_default_texts(db, skip=skip, limit=limit)


@router.get("/{key}", response_model=schemas.DefaultText)
async def get_default_text(
    key: str,
    db: Session = Depends(get_db)
):
    db_default_text = crud.get_default_text(db, key=key)
    if not db_default_text:
        raise HTTPException(status_code=404, detail="Default text not found")
    return db_default_text


@router.post("/", response_model=schemas.DefaultText)
async def create_default_text(
    default_text: schemas.DefaultTextCreate,
    db: Session = Depends(get_db),
    current_user = Depends(auth.get_current_user)
):
    db_default_text = crud.get_default_text(db, key=default_text.key)
    if db_default_text:
        raise HTTPException(status_code=400, detail="Default text with this key already exists")
    return crud.create_default_text(db=db, default_text=default_text)


@router.put("/{key}", response_model=schemas.DefaultText)
async def update_default_text(
    key: str,
    default_text_update: schemas.DefaultTextUpdate,
    db: Session = Depends(get_db),
    current_user = Depends(auth.get_current_user)
):
    db_default_text = crud.update_default_text(db, key, default_text_update)
    if not db_default_text:
        raise HTTPException(status_code=404, detail="Default text not found")
    return db_default_text


@router.delete("/{key}")
async def delete_default_text(
    key: str,
    db: Session = Depends(get_db),
    current_user = Depends(auth.get_current_user)
):
    db_default_text = crud.delete_default_text(db, key)
    if not db_default_text:
        raise HTTPException(status_code=404, detail="Default text not found")
    return {"message": "Default text deleted successfully"}