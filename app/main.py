from fastapi import FastAPI
from app.auth.routes import router as auth_router
from app.products.routes import router as product_router
from app.cart.routes import router as cart_router

app = FastAPI()

app.include_router(auth_router, prefix="/auth")
app.include_router(product_router, prefix="/products")
app.include_router(cart_router, prefix="/cart")
