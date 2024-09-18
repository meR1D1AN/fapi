from fastapi import APIRouter, Depends, HTTPException, status

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from typing import List
from app.products.schemas import ProductCreate, ProductUpdate, ProductOut
from app.products.models import Product
from app.auth.models import User
from app.core.security import get_current_user
from app.db.session import get_db

router = APIRouter()


def is_admin(current_user: User = Depends(get_current_user)):
    """
    Проверяет, является ли пользователь администратором.
    Если пользователь не является администратором, генерируется исключение HTTPException
    с кодом 403 (Forbidden) и сообщением "Только администраторы могут получить доступ к этому ресурсу".
    Аргументы:
        current_user (User): Текущий пользователь, полученный из функции get_current_user.
    Возвращает:
        User
    """
    if not current_user.is_admin:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail="Только администраторы могут получить доступ к этому ресурсу")
    return current_user


@router.get("/products", response_model=List[ProductOut])
async def get_products(db: AsyncSession = Depends(get_db)) -> List[ProductOut]:
    """
    Возвращает список активных товаров.
    Активными считаются товары, у которых поле `is_active` равно `True`.
    Аргументы:
        db (AsyncSession, optional): Сеанс асинхронной базы данных. По умолчанию получается из зависимости get_db.
    Возвращает:
        List[ProductOut]: Список активных товаров.
    """
    stmt = select(Product).where(Product.is_active == True)
    result = await db.execute(stmt)
    products = result.scalars().all()
    return products


@router.post("/products", response_model=ProductOut)
async def create_product(
        product_data: ProductCreate,
        db: AsyncSession = Depends(get_db),
        current_user: User = Depends(is_admin)
) -> ProductOut:
    """
    Создает новый товар в базе данных.
    Доступно только администраторам.
    Аргументы:
        product_data (ProductCreate): Данные нового товара.
        db (AsyncSession, optional): Сеанс асинхронной базы данных. По умолчанию получается из зависимости get_db.
        current_user (User): Текущий авторизованный пользователь. Defaults to Depends(is_admin).
    Возвращает:
        ProductOut: Созданный товар.
    """
    new_product = Product(
        name=product_data.name,
        price=product_data.price,
        is_active=product_data.is_active
    )
    db.add(new_product)
    await db.commit()
    await db.refresh(new_product)
    return new_product


@router.put("/products/{product_id}", response_model=ProductUpdate)
async def update_product(
        product_id: int,
        product_data: ProductCreate,
        db: AsyncSession = Depends(get_db),
        current_user: User = Depends(is_admin)
) -> ProductUpdate:
    """
    Обновляет существующий товар в базе данных.
    Доступно только администраторам.
    Аргументы:
        product_id (int): ID товара для обновления.
        product_data (ProductUpdate): Данные для обновления товара.
        db (AsyncSession, optional): Сеанс асинхронной базы данных. По умолчанию получается из зависимости get_db.
        current_user (User): Текущий авторизованный пользователь. Defaults to Depends(is_admin).
    Исключения:
        HTTPException: Если товар не найден в базе данных.
    Возвращает:
        ProductOut: Обновленный товар.
    """
    stmt = select(Product).where(Product.id == product_id)
    result = await db.execute(stmt)
    product = result.scalars().first()

    if not product:
        raise HTTPException(status_code=404, detail="Товар не найден")

    product.name = product_data.name
    product.price = product_data.price
    product.is_active = product_data.is_active

    await db.commit()
    await db.refresh(product)
    return product


@router.delete("/products/{product_id}", response_model=dict)
async def delete_product(
        product_id: int,
        db: AsyncSession = Depends(get_db),
        current_user: User = Depends(is_admin)
)-> dict:
    """
    Удаляет товар из базы данных по его ID.
    Доступно только администраторам.
    Аргументы:
        product_id (int): ID товара для удаления.
        db (AsyncSession, optional): Сеанс асинхронной базы данных. По умолчанию получается из зависимости get_db.
        current_user (User, optional): Текущий пользователь. По умолчанию получается из зависимости is_admin.
    Исключения:
        HTTPException: Если товар с указанным идентификатором не найден.
    Возвращает:
        dict: Сообщение об успешном удалении товара.
    """
    stmt = select(Product).where(Product.id == product_id)
    result = await db.execute(stmt)
    product = result.scalars().first()

    if not product:
        raise HTTPException(status_code=404, detail="Товар не найден")

    await db.delete(product)
    await db.commit()
    return {"message": "Продукт успешно удален"}
