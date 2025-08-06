from sqlalchemy.orm import Session
from . import models, auth, schemas

def get_user_by_username(db: Session, username: str):
    return db.query(models.DBUser).filter(models.DBUser.username == username).first()

def create_user(db: Session, user: schemas.UserCreate):
    hashed_password = auth.get_password_hash(user.password)
    db_user = models.DBUser(
        username=user.username,
        email=user.email,
        full_name=user.full_name,
        hashed_password=hashed_password
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def get_contract(db: Session, contract_id: int):
    return db.query(models.DBContract).filter(models.DBContract.id == contract_id, models.DBContract.deleted_at.is_(None)).first()

def get_contracts(db: Session, skip: int = 0, limit: int = 100, sort_by: str = 'created_at', sort_order: str = 'desc', search: str = None):
    query = db.query(models.DBContract).filter(models.DBContract.deleted_at.is_(None))
    
    if search:
        query = query.filter(
            models.DBContract.client_name.ilike(f"%{search}%") |
            models.DBContract.client_email.ilike(f"%{search}%")
        )
    
    order_column = getattr(models.DBContract, sort_by, models.DBContract.created_at)
    if sort_order == 'desc':
        query = query.order_by(order_column.desc())
    else:
        query = query.order_by(order_column.asc())
        
    return query.offset(skip).limit(limit).all()


def get_contracts_count(db: Session, search: str = None):
    query = db.query(models.DBContract).filter(models.DBContract.deleted_at.is_(None))
    
    if search:
        query = query.filter(
            models.DBContract.client_name.ilike(f"%{search}%") |
            models.DBContract.client_email.ilike(f"%{search}%")
        )
        
    return query.count()

def create_contract(db: Session, contract: schemas.ContractCreate, design_image_path: str):
    db_contract = models.DBContract(
        client_name=contract.client_data.name,
        client_email=contract.client_data.email,
        design_image_path=design_image_path,
        titulo_diseno=contract.titulo_diseno,
        puesto_empresa=contract.puesto_empresa,
        politica_confirmacion=contract.politica_confirmacion
    )
    db.add(db_contract)
    db.commit()
    db.refresh(db_contract)
    return db_contract

def update_contract(db: Session, contract_id: int, contract_update: schemas.ContractUpdate):
    db_contract = get_contract(db, contract_id)
    if not db_contract:
        return None
    
    update_data = contract_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_contract, field, value)
    
    db.commit()
    db.refresh(db_contract)
    return db_contract

def delete_contract(db: Session, contract_id: int):
    from datetime import datetime
    db_contract = get_contract(db, contract_id)
    if not db_contract:
        return None
    
    db_contract.deleted_at = datetime.utcnow()
    db.commit()
    return db_contract


def get_default_text(db: Session, key: str):
    return db.query(models.DBDefaultText).filter(models.DBDefaultText.key == key).first()


def get_default_texts(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.DBDefaultText).offset(skip).limit(limit).all()


def create_default_text(db: Session, default_text: schemas.DefaultTextCreate):
    db_default_text = models.DBDefaultText(
        key=default_text.key,
        content=default_text.content
    )
    db.add(db_default_text)
    db.commit()
    db.refresh(db_default_text)
    return db_default_text


def update_default_text(db: Session, key: str, default_text_update: schemas.DefaultTextUpdate):
    from datetime import datetime
    db_default_text = get_default_text(db, key)
    if not db_default_text:
        return None
    
    db_default_text.content = default_text_update.content
    db_default_text.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(db_default_text)
    return db_default_text


def delete_default_text(db: Session, key: str):
    db_default_text = get_default_text(db, key)
    if not db_default_text:
        return None
    
    db.delete(db_default_text)
    db.commit()
    return db_default_text
