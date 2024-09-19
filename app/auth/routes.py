from fastapi import APIRouter, HTTPException, Depends, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm

from datetime import timedelta

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.auth.schemas import UserCreate, Token, UserOut, UserRegister
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


@router.post("/register", response_model=UserRegister)
async def register_user(
        user_data: UserCreate,
        db: AsyncSession = Depends(get_db)
) -> dict:
    """
    Обработчик POST-запроса для регистрации нового пользователя.\n
    Аргументы:\n
        \t user_data (UserCreate): Данные нового пользователя.
        \t db (AsyncSession, optional): Сеанс асинхронной базы данных. По умолчанию получается из зависимости get_db.
    Исключения:\n
        \t HTTPException: Если пользователь с таким email или телефоном уже существует.
    Возвращает: \n
        \t dict: Сообщение об успешной регистрации.\n
    """
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
async def login_for_access_token(
        db: AsyncSession = Depends(get_db),
        form_data: OAuth2PasswordRequestForm = Depends()
) -> dict:
    """
    Обработчик POST-запроса на получение токена доступа.\n
    Аутентифицирует пользователя по email и паролю, а затем выдаёт токен доступа.\n
    Аргументы:\n
        \t db (AsyncSession, optional): Сеанс асинхронной базы данных. По умолчанию получается из зависимости get_db.
        \t form_data (OAuth2PasswordRequestForm): Форма аутентификации.
    Исключения:\n
        \t HTTPException: Если аутентификация не удалась.
    Возвращает:\n
        \t dict: Токен доступа и тип токена.
    """
    user = await authenticate_user(db, email=form_data.username, password=form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Неправильный email, телефон или пароль",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(data={"sub": str(user.id)}, expires_delta=access_token_expires)
    return {"access_token": access_token, "token_type": "bearer"}


# @router.get("/users/me", response_model=User)
# async def read_users_me(current_user: User = Depends(get_current_active_user)):
#     """
#     Возвращает информацию о текущем авторизованном пользователе.
#     Аргументы:
#         current_user (User): Текущий пользователь, полученный из токена доступа.
#     Возвращает:
#         User
#     """
#     return current_user

@router.get("/users/{user_id}", response_model=UserOut)
async def get_user_by_id(
        user_id: int,
        db: AsyncSession = Depends(get_db),
        current_user: User = Depends(get_current_active_user)
) -> UserOut:
    """
    Возвращает информацию о пользователе по его ID.\n
    Если пользователь не администратор, то может получить информацию только о себе.\n
    Аргументы:\n
        \t user_id (int): ID пользователя, информацию о котором нужно получить.
        \t db (AsyncSession, optional): Сеанс асинхронной базы данных. По умолчанию получается из зависимости get_db.
        \t current_user (User): Текущий авторизованный пользователь, полученный из токена доступа.
    Исключения:\n
        \t HTTPException: Если пользователь не администратор и пытается получить информацию о другом пользователе.
        \t HTTPException: Если пользователь с указанным ID не найден.
    Возвращает:\n
        \t UserOut: Информация о пользователе.
    """
    if user_id != current_user.id and not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Нет доступа к этим данным")

    stmt = select(User).where(User.id == user_id)
    result = await db.execute(stmt)
    user = result.scalars().first()

    if not user:
        raise HTTPException(status_code=404, detail="Пользователь не найден")

    return user
