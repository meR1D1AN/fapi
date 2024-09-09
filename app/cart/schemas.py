from pydantic import BaseModel
from typing import List


class CartItemCreate(BaseModel):
    product_id: int
    quantity: int = 1


class CartItemOut(BaseModel):
    product_id: int
    quantity: int


class CartOut(BaseModel):
    items: List[CartItemOut]
    total_price: int

    class Config:
        orm_mode = True
