from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.auth.schemas import UserCreate
from app.auth.models import User
from app.auth.utils import hash_password
from app.db.session import get_db

router = APIRouter()


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
