from sqlalchemy.orm import Session
from app.models.user import User
from app.schemas.user import UserCreate, UserUpdate
from typing import Optional, List

def get_user(db: Session, user_id: int) -> Optional[User]:
    return db.query(User).filter(User.id == user_id).first()

def get_user_by_username(db: Session, name: str) -> Optional[User]:
    return db.query(User).filter(User.name == name).first()

def get_user_by_email(db: Session, email: str) -> Optional[User]:
    return db.query(User).filter(User.email == email).first()

def get_users(db: Session, page: int = 0, page_size: int = 10) -> List[User]:
    offset = page * page_size
    return db.query(User).offset(offset).limit(page_size).all()

def create_user(db: Session, user_in: UserCreate) -> User:
    from app.core.security import get_password_hash
    user = User(
        email=user_in.email,
        name=user_in.name,
        password=get_password_hash(user_in.password),
        is_active=user_in.is_active,
        is_superuser=user_in.is_superuser,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

def update_user(db: Session, db_user: User, user_in: UserUpdate) -> User:
    from app.core.security import get_password_hash
    update_data = user_in.dict(exclude_unset=True)
    
    if "password" in update_data:
        hashed_password = get_password_hash(update_data["password"])
        del update_data["password"]
        update_data["hashed_password"] = hashed_password
    
    for field, value in update_data.items():
        setattr(db_user, field, value)
    
    db.commit()
    db.refresh(db_user)
    return db_user

def delete_user(db: Session, user_id: int) -> User:
    user = db.query(User).filter(User.id == user_id).first()
    db.delete(user)
    db.commit()
    return user