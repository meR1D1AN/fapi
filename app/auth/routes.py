from fastapi import APIRouter, HTTPException, Depends, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm

from datetime import timedelta

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.auth.schemas import UserCreate, Token
from app.auth.models import User
from app.core.security import (
    authenticate_user,
    create_access_token,
    hash_password,
    get_current_active_user,
    ACCESS_TOKEN_EXPIRE_MINUTES
)
from app.db.session import get_db

router = APIRouter()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")


@router.post("/register", response_model=dict)
async def register_user(user_data: UserCreate, db: AsyncSession = Depends(get_db)):
    # Проверяем, существует ли пользователь с таким email или телефоном
    stmt = select(User).where((User.email == user_data.email) | (User.phone == user_data.phone))
    result = await db.execute(stmt)
    user = result.scalars().first()

    if user:
        raise HTTPException(status_code=400, detail="Пользователь с таким email или телефоном уже существует.")

    # Создаем нового пользователя
    new_user = User(
        full_name=user_data.full_name,
        email=user_data.email,
        phone=user_data.phone,
        hashed_password=hash_password(user_data.password)
    )

    db.add(new_user)  # Добавляем пользователя в базу данных
    await db.commit()  # Фиксируем транзакцию
    await db.refresh(new_user)  # Обновляем объект из базы

    return {"message": "Пользователь успешно зарегистрирован"}


@router.post("/login", response_model=Token)
async def login_for_access_token(db: AsyncSession = Depends(get_db), form_data: OAuth2PasswordRequestForm = Depends()):
    user = await authenticate_user(db, email=form_data.username, password=form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email, phone or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(data={"sub": str(user.id)}, expires_delta=access_token_expires)
    return {"access_token": access_token, "token_type": "bearer"}


@router.get("/users/me", response_model=User)
async def read_users_me(current_user: User = Depends(get_current_active_user)):
    return current_user
