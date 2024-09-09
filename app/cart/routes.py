from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.auth.models import User
from app.cart.models import CartItem
from app.cart.schemas import CartItemCreate, CartOut
from app.products.models import Product
from app.db.session import get_db
from app.core.security import get_current_user

router = APIRouter()


# Добавление товаров в корзину
@router.post("/cart", response_model=CartOut)
async def add_to_cart(item: CartItemCreate, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    product = db.query(Product).filter(Product.id == item.product_id, Product.is_active == True).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    cart_item = db.query(CartItem).filter(CartItem.product_id == item.product_id, CartItem.user_id == user.id).first()
    if cart_item:
        cart_item.quantity += item.quantity
    else:
        cart_item = CartItem(product_id=item.product_id, user_id=user.id, quantity=item.quantity)
        db.add(cart_item)

    db.commit()
    return await get_cart(user, db)


# Получение содержимого корзины
@router.get("/cart", response_model=CartOut)
async def get_cart(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    items = db.query(CartItem).filter(CartItem.user_id == user.id).all()
    total_price = sum([item.quantity * item.product.price for item in items])
    return CartOut(
        items=[{"product_id": item.product_id, "quantity": item.quantity} for item in items],
        total_price=total_price
    )


# Очистка корзины
@router.delete("/cart", response_model=dict)
async def clear_cart(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    db.query(CartItem).filter(CartItem.user_id == user.id).delete()
    db.commit()
    return {"message": "Cart cleared"}
