from fastapi import APIRouter, Depends, HTTPException

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.auth.models import User
from app.cart.models import CartItem
from app.cart.schemas import CartItemCreate, CartOut, CartDelete
from app.products.models import Product
from app.db.session import get_db
from app.core.security import get_current_active_user

router = APIRouter()


@router.post("/cart", response_model=CartOut)
async def add_to_cart(
        item_data: CartItemCreate,
        db: AsyncSession = Depends(get_db),
        current_user: User = Depends(get_current_active_user)
) -> CartItem:
    """
    Добавляет товар в корзину пользователя.\n
    Аргументы:\n
        \t item_data (CartItemCreate): Данные товара для добавления в корзину.
        \t db (AsyncSession, optional): Сеанс асинхронной базы данных. По умолчанию получается из зависимости get_db.
        \t current_user (User): Текущий авторизованный пользователь. Defaults to Depends(get_current_active_user).
    Исключения:\n
        \t HTTPException: Если товар не найден в базе данных.
    Возвращает:\n
        \t CartItem: Объект добавленного товара в корзину.
    """
    stmt = select(Product).where(Product.id == item_data.product_id)
    result = await db.execute(stmt)
    product = result.scalars().first()

    if not product:
        raise HTTPException(status_code=404, detail="Товар не найден")

    cart_item = CartItem(
        product_id=item_data.product_id,
        user_id=current_user.id,
        quantity=item_data.quantity
    )
    db.add(cart_item)
    await db.commit()
    await db.refresh(cart_item)
    return cart_item


@router.get("/cart", response_model=list[CartOut])
async def get_cart(
        db: AsyncSession = Depends(get_db),
        current_user: User = Depends(get_current_active_user)
) -> list[CartItem]:
    """
    Возвращает содержимое корзины пользователя.\n
    Аргументы:\n
        \t db (AsyncSession, optional): Сеанс асинхронной базы данных. По умолчанию получается из зависимости get_db.
        \t current_user (User): Текущий авторизованный пользователь. Defaults to Depends(get_current_active_user).
    Возвращает:\n
        \t list[CartOut]: Список объектов товаров в корзине пользователя.
    """
    stmt = select(CartItem).where(CartItem.user_id == current_user.id)
    result = await db.execute(stmt)
    return result.scalars().all()


@router.delete("/cart/{item_id}", response_model=CartDelete)
async def remove_from_cart(
        item_id: int,
        db: AsyncSession = Depends(get_db),
        current_user: User = Depends(get_current_active_user)
) -> dict:
    """
    Удаляет товар из корзины пользователя.\n
    Аргументы:\n
        \t item_id (int): ID товара для удаления из корзины.
        \t db (AsyncSession): Сессия базы данных. Defaults to Depends(get_db).
        \t current_user (User): Текущий авторизованный пользователь. Defaults to Depends(get_current_active_user).
    Исключения:\n
        \t HTTPException: Если товар не найден в корзине пользователя.
    Возвращает:\n
        \t dict: Сообщение об успешном удалении товара из корзины.
    """
    stmt = select(CartItem).where(CartItem.id == item_id, CartItem.user_id == current_user.id)
    result = await db.execute(stmt)
    cart_item = result.scalars().first()

    if not cart_item:
        raise HTTPException(status_code=404, detail="Элемент корзины не найден")

    await db.delete(cart_item)
    await db.commit()
    return {"message": "Корзина очищена"}
