from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.products.schemas import ProductCreate, ProductUpdate, ProductOut
from app.products.models import Product
from app.auth.models import User
from app.core.security import get_current_user
from app.db.session import get_db

router = APIRouter()


# Проверяем, является ли пользователь администратором
def is_admin(user: User = Depends(get_current_user)):
    if not user.is_admin:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only admins can access this resource")
    return user


# Получение списка активных товаров
@router.get("/products", response_model=List[ProductOut])
async def get_products(db: Session = Depends(get_db)):
    products = db.query(Product).filter(Product.is_active == True).all()
    return products


# Создание товара (доступно только администраторам)
@router.post("/products", response_model=ProductOut)
async def create_product(product_data: ProductCreate, db: Session = Depends(get_db), admin: User = Depends(is_admin)):
    new_product = Product(**product_data.dict())
    db.add(new_product)
    db.commit()
    db.refresh(new_product)
    return new_product


# Обновление товара (доступно только администраторам)
@router.put("/products/{product_id}", response_model=ProductOut)
async def update_product(product_id: int, product_data: ProductUpdate, db: Session = Depends(get_db),
                         admin: User = Depends(is_admin)):
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found")

    for key, value in product_data.dict(exclude_unset=True).items():
        setattr(product, key, value)

    db.commit()
    db.refresh(product)
    return product


# Удаление товара (доступно только администраторам)
@router.delete("/products/{product_id}", response_model=dict)
async def delete_product(product_id: int, db: Session = Depends(get_db), admin: User = Depends(is_admin)):
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found")

    db.delete(product)
    db.commit()
    return {"message": "Product deleted successfully"}
