from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from app.auth.schemas import UserCreate
from app.auth.models import User
from app.auth.utils import hash_password
from app.db.session import get_db

router = APIRouter()


@router.post("/register", response_model=dict)
async def register_user(user_data: UserCreate, db: Session = Depends(get_db)):
    # Проверяем, существует ли пользователь с таким email или телефоном
    user = db.query(User).filter((User.email == user_data.email) | (User.phone == user_data.phone)).first()
    if user:
        raise HTTPException(status_code=400, detail="User with this email or phone already exists.")

    # Создаем нового пользователя
    new_user = User(
        full_name=user_data.full_name,
        email=user_data.email,
        phone=user_data.phone,
        hashed_password=hash_password(user_data.password)
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return {"message": "User successfully registered"}
