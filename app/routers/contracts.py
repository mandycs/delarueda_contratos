import os
import json
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, Request, Query
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from .. import auth, crud, models, schemas
from ..database import get_db
from ..services.pdf_service import create_professional_pdf
from ..services.file_service import save_uploaded_file, delete_file_if_exists, CONTRACTS_DIR
from ..services.email_service import email_service

router = APIRouter(prefix="/contracts", tags=["contracts"])


@router.post("/", response_model=schemas.Contract)
async def create_contract(
    client_data: str = Form(...),
    design_image: UploadFile = File(...),
    titulo_diseno: str = Form(None),
    puesto_empresa: str = Form(None),
    politica_confirmacion: str = Form(None),
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user)
):
    try:
        client_data_dict = json.loads(client_data)
        contract_create = schemas.ContractCreate(
            client_data=client_data_dict,
            titulo_diseno=titulo_diseno,
            puesto_empresa=puesto_empresa,
            politica_confirmacion=politica_confirmacion
        )
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid client_data format")

    # Save design image
    design_image_path = save_uploaded_file(design_image)

    # Create contract in database
    db_contract = crud.create_contract(db=db, contract=contract_create, design_image_path=design_image_path)

    # Generate unsigned PDF
    unsigned_pdf_filename = f"{db_contract.id}_unsigned.pdf"
    unsigned_pdf_path = os.path.join(CONTRACTS_DIR, unsigned_pdf_filename)

    try:
        create_professional_pdf(
            pdf_path=unsigned_pdf_path,
            client_name=db_contract.client_name,
            client_email=db_contract.client_email,
            design_image_path=design_image_path,
            titulo_diseno=db_contract.titulo_diseno,
            puesto_empresa=db_contract.puesto_empresa,
            politica_confirmacion=db_contract.politica_confirmacion
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Could not process design image: {e}")

    # Update contract with PDF path
    db_contract.unsigned_pdf_path = unsigned_pdf_path
    db.commit()
    db.refresh(db_contract)

    return db_contract


@router.get("/{contract_id}/preview")
async def preview_contract(contract_id: int, db: Session = Depends(get_db)):
    db_contract = crud.get_contract(db, contract_id=contract_id)
    if not db_contract or not db_contract.unsigned_pdf_path:
        raise HTTPException(status_code=404, detail="Contract not found or not yet processed")
    return FileResponse(db_contract.unsigned_pdf_path)


@router.post("/{contract_id}/sign")
async def sign_contract(
    request: Request,
    contract_id: int,
    signature_image: UploadFile = File(...),
    signed_by: str = Form(...),
    db: Session = Depends(get_db)
):
    db_contract = crud.get_contract(db, contract_id=contract_id)
    if not db_contract or not db_contract.unsigned_pdf_path:
        raise HTTPException(status_code=404, detail="Contract not found or not yet processed")

    # Save signature image
    signature_path = save_uploaded_file(signature_image)

    # Generate signed PDF
    signed_pdf_filename = f"{db_contract.id}_signed.pdf"
    signed_pdf_path = os.path.join(CONTRACTS_DIR, signed_pdf_filename)
    signed_at_str = datetime.utcnow().strftime("%d/%m/%Y %H:%M")
    
    try:
        create_professional_pdf(
            pdf_path=signed_pdf_path,
            client_name=db_contract.client_name,
            client_email=db_contract.client_email,
            design_image_path=db_contract.design_image_path,
            titulo_diseno=db_contract.titulo_diseno,
            puesto_empresa=db_contract.puesto_empresa,
            politica_confirmacion=db_contract.politica_confirmacion,
            signature_path=signature_path,
            signed_by=signed_by,
            signed_at_str=signed_at_str
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Could not process images: {e}")

    # Update contract with signature info
    db_contract.signed_pdf_path = signed_pdf_path
    db_contract.signed_at = datetime.utcnow()
    db_contract.signer_ip = request.client.host
    db_contract.signer_user_agent = request.headers.get("user-agent")
    db.commit()
    db.refresh(db_contract)

    # Send automatic confirmation email to client
    if db_contract.client_email:
        try:
            await email_service.send_contract_signed_confirmation(
                to_email=db_contract.client_email,
                client_name=db_contract.client_name,
                contract_id=db_contract.id,
                signed_pdf_path=signed_pdf_path,
                titulo_diseno=db_contract.titulo_diseno
            )
        except Exception as e:
            # Log the error but don't fail the contract signing
            print(f"Warning: Failed to send confirmation email: {str(e)}")

    return db_contract


@router.get("/{contract_id}/signed")
async def download_signed_contract(contract_id: int, db: Session = Depends(get_db)):
    db_contract = crud.get_contract(db, contract_id=contract_id)
    if not db_contract or not db_contract.signed_pdf_path:
        raise HTTPException(status_code=404, detail="Signed contract not found")
    return FileResponse(db_contract.signed_pdf_path)


@router.get("/", response_model=schemas.PaginatedContracts)
async def list_contracts(
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(10, ge=1, le=100, description="Number of items per page"),
    sort_by: str = Query('created_at', description="Sort by field"),
    sort_order: str = Query('desc', description="Sort order (asc or desc)"),
    search: str = Query(None, description="Search query for client name or email"),
    db: Session = Depends(get_db)
):
    # Calculate skip based on page
    skip = (page - 1) * page_size
    
    # Get contracts and total count
    contracts = crud.get_contracts(db, skip=skip, limit=page_size, sort_by=sort_by, sort_order=sort_order, search=search)
    total = crud.get_contracts_count(db, search=search)
    
    # Calculate pagination info
    total_pages = (total + page_size - 1) // page_size  # Ceiling division
    has_next = page < total_pages
    has_prev = page > 1
    
    # Create paginated response
    pagination_info = schemas.PaginationInfo(
        total=total,
        page=page,
        page_size=page_size,
        total_pages=total_pages,
        has_next=has_next,
        has_prev=has_prev
    )
    
    return schemas.PaginatedContracts(
        items=contracts,
        pagination=pagination_info
    )


@router.put("/{contract_id}", response_model=schemas.Contract)
async def update_contract(
    contract_id: int,
    contract_update: schemas.ContractUpdate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user)
):
    db_contract = crud.update_contract(db, contract_id, contract_update)
    if not db_contract:
        raise HTTPException(status_code=404, detail="Contract not found")
    
    # If client data or new fields were updated, regenerate unsigned PDF
    if (contract_update.client_name or contract_update.client_email or 
        contract_update.titulo_diseno or contract_update.puesto_empresa or 
        contract_update.politica_confirmacion):
        try:
            create_professional_pdf(
                pdf_path=db_contract.unsigned_pdf_path,
                client_name=db_contract.client_name,
                client_email=db_contract.client_email,
                design_image_path=db_contract.design_image_path,
                titulo_diseno=db_contract.titulo_diseno,
                puesto_empresa=db_contract.puesto_empresa,
                politica_confirmacion=db_contract.politica_confirmacion
            )
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Could not regenerate PDF: {e}")
    
    return db_contract


@router.delete("/{contract_id}")
async def delete_contract(
    contract_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user)
):
    db_contract = crud.delete_contract(db, contract_id)
    if not db_contract:
        raise HTTPException(status_code=404, detail="Contract not found")
    
    # Delete physical files
    delete_file_if_exists(db_contract.unsigned_pdf_path)
    delete_file_if_exists(db_contract.signed_pdf_path)
    delete_file_if_exists(db_contract.design_image_path)
    
    return {"message": "Contract deleted successfully"}


@router.post("/{contract_id}/send-invitation")
async def send_contract_invitation(
    contract_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user)
):
    """
    Send email invitation to client for contract signing
    """
    db_contract = crud.get_contract(db, contract_id=contract_id)
    if not db_contract:
        raise HTTPException(status_code=404, detail="Contract not found")
    
    if not db_contract.unsigned_pdf_path:
        raise HTTPException(status_code=400, detail="Contract PDF not yet generated")
    
    if not db_contract.client_email:
        raise HTTPException(status_code=400, detail="Client email not provided")
    
    try:
        success = await email_service.send_contract_invitation(
            to_email=db_contract.client_email,
            client_name=db_contract.client_name,
            contract_id=db_contract.id,
            titulo_diseno=db_contract.titulo_diseno
        )
        
        if success:
            return {"message": "Invitation email sent successfully", "email": db_contract.client_email}
        else:
            raise HTTPException(status_code=500, detail="Failed to send invitation email")
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Email service error: {str(e)}")


@router.post("/{contract_id}/resend-invitation")
async def resend_contract_invitation(
    contract_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user)
):
    """
    Resend email invitation to client for contract signing
    """
    db_contract = crud.get_contract(db, contract_id=contract_id)
    if not db_contract:
        raise HTTPException(status_code=404, detail="Contract not found")
    
    if not db_contract.unsigned_pdf_path:
        raise HTTPException(status_code=400, detail="Contract PDF not yet generated")
    
    if not db_contract.client_email:
        raise HTTPException(status_code=400, detail="Client email not provided")
    
    if db_contract.signed_pdf_path:
        raise HTTPException(status_code=400, detail="Contract already signed")
    
    try:
        success = await email_service.send_contract_invitation(
            to_email=db_contract.client_email,
            client_name=db_contract.client_name,
            contract_id=db_contract.id,
            titulo_diseno=db_contract.titulo_diseno
        )
        
        if success:
            return {"message": "Invitation email resent successfully", "email": db_contract.client_email}
        else:
            raise HTTPException(status_code=500, detail="Failed to resend invitation email")
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Email service error: {str(e)}")