from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import relationship
from pydantic import BaseModel, Field, ConfigDict
from typing import Optional
from uuid import UUID, uuid4
from datetime import datetime

from .database import Base

# --- SQLAlchemy Models ---

class DBUser(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True)
    full_name = Column(String)
    hashed_password = Column(String)
    disabled = Column(Boolean, default=False)

class DBContract(Base):
    __tablename__ = "contracts"

    id = Column(Integer, primary_key=True, index=True)
    client_name = Column(String, index=True)
    client_email = Column(String, index=True)
    design_image_path = Column(String)
    titulo_diseno = Column(String, nullable=True)
    puesto_empresa = Column(String, nullable=True)
    politica_confirmacion = Column(Text, nullable=True)
    unsigned_pdf_path = Column(String, nullable=True)
    signed_pdf_path = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    signed_at = Column(DateTime, nullable=True)
    signer_ip = Column(String, nullable=True)
    signer_user_agent = Column(String, nullable=True)
    deleted_at = Column(DateTime, nullable=True)


class DBDefaultText(Base):
    __tablename__ = "default_texts"

    id = Column(Integer, primary_key=True, index=True)
    key = Column(String, unique=True, index=True)
    content = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class User(BaseModel):
    id: int
    username: str
    email: Optional[str] = None
    full_name: Optional[str] = None
    disabled: Optional[bool] = None

    model_config = ConfigDict(from_attributes=True)
