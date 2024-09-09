from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class ProductCreate(BaseModel):
    name: str
    price: int = Field(..., gt=0)  # Цена должна быть больше 0


class ProductUpdate(BaseModel):
    name: Optional[str]
    price: Optional[int] = Field(None, gt=0)
    is_active: Optional[bool]


class ProductOut(BaseModel):
    id: int
    name: str
    price: int
    created_at: datetime
    updated_at: datetime
    is_active: bool

    class Config:
        from_attributes = True
