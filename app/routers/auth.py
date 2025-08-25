from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from datetime import timedelta

from .. import auth, crud, models
from ..database import get_db
from ..config import settings
from ..logger import get_logger, log_security_event

router = APIRouter(tags=["authentication"])
logger = get_logger(__name__)


@router.post("/token")
async def login_for_access_token(
    request: Request,
    form_data: OAuth2PasswordRequestForm = Depends(), 
    db: Session = Depends(get_db)
):
    client_ip = request.client.host if request.client else "unknown"
    
    user = crud.get_user_by_username(db, username=form_data.username)
    if not user or not auth.verify_password(form_data.password, user.hashed_password):
        log_security_event(
            logger,
            "LOGIN_FAILED",
            f"Failed login attempt for username: {form_data.username}",
            ip_address=client_ip
        )
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    log_security_event(
        logger,
        "LOGIN_SUCCESS",
        f"Successful login for user: {user.username}",
        user_id=str(user.id),
        ip_address=client_ip
    )
    
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = auth.create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}


@router.get("/users/me/", response_model=models.User)
async def read_users_me(current_user: models.User = Depends(auth.get_current_user), db: Session = Depends(get_db)):
    user = crud.get_user_by_username(db, username=current_user['username'])
    return user