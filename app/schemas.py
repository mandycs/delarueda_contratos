from pydantic import BaseModel, EmailStr, ConfigDict
from typing import Optional, List

class ClientData(BaseModel):
    name: str
    email: EmailStr

class ContractCreate(BaseModel):
    client_data: ClientData
    titulo_diseno: Optional[str] = None
    puesto_empresa: Optional[str] = None
    politica_confirmacion: Optional[str] = None

class ContractUpdate(BaseModel):
    client_name: Optional[str] = None
    client_email: Optional[EmailStr] = None
    titulo_diseno: Optional[str] = None
    puesto_empresa: Optional[str] = None
    politica_confirmacion: Optional[str] = None

class Contract(BaseModel):
    id: int
    client_name: str
    client_email: EmailStr
    design_image_path: str
    titulo_diseno: Optional[str] = None
    puesto_empresa: Optional[str] = None
    politica_confirmacion: Optional[str] = None
    unsigned_pdf_path: Optional[str] = None
    signed_pdf_path: Optional[str] = None
    signer_ip: Optional[str] = None
    signer_user_agent: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)

class UserCreate(BaseModel):
    username: str
    email: Optional[str] = None
    full_name: Optional[str] = None
    password: str

class PaginationInfo(BaseModel):
    total: int
    page: int
    page_size: int
    total_pages: int
    has_next: bool
    has_prev: bool

class PaginatedContracts(BaseModel):
    items: List[Contract]
    pagination: PaginationInfo


class DefaultTextCreate(BaseModel):
    key: str
    content: str


class DefaultTextUpdate(BaseModel):
    content: str


class DefaultText(BaseModel):
    id: int
    key: str
    content: str

    model_config = ConfigDict(from_attributes=True)
