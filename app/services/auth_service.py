from sqlalchemy.orm import Session

from app.models.user import User
from app.core.security import hash_password


def register_user(
    db: Session,
    email: str,
    password: str,
    full_name: str
):
    user = User(
        email=email,
        password=hash_password(password),
        full_name=full_name
    )

    db.add(user)
    db.commit()
    db.refresh(user)

    return user


def get_user_by_email(db: Session, email: str):
    return db.query(User).filter(User.email == email).first()


def authenticate_user(db: Session, email: str, password: str):
    user = get_user_by_email(db, email)

    if not user:
        return None

    from app.core.security import verify_password

    if not verify_password(password, user.password):
        return None

    return user