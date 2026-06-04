from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.services.auth_service import register_user, authenticate_user, get_user_by_email
from app.core.security import create_access_token
from app.schemas.user import UserCreate, UserOut, Token, UserLogin


router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=UserOut)
def register(payload: UserCreate, db: Session = Depends(get_db)):
    existing = get_user_by_email(db, payload.email)

    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )

    user = register_user(db, payload.email, payload.password, payload.full_name)

    return user


@router.post("/login", response_model=Token)
def login(payload: UserLogin, db: Session = Depends(get_db)):
    user = authenticate_user(db, payload.email, payload.password)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"}
        )

    token_data = {"sub": str(user.id), "email": user.email}

    access_token = create_access_token(token_data)

    return {"access_token": access_token, "token_type": "bearer"}