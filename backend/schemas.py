# backend/schemas.py
from typing import Optional, List
from pydantic import BaseModel, EmailStr


# ========================= USERS =========================

class UserCreate(BaseModel):
    username: str
    email: EmailStr
    password: str


class UserLogin(BaseModel):
    username: str
    password: str


class UserOut(BaseModel):
    id: int
    username: str
    email: EmailStr

    class Config:
        from_attributes = True


# ======================== PRODUCTS =======================

class ProductBase(BaseModel):
    name: str
    description: Optional[str] = None
    price: float
    image_url: Optional[str] = None
    stock: int = 0


class ProductCreate(ProductBase):
    pass


class Product(ProductBase):
    id: int

    class Config:
        from_attributes = True


# ========================== CART =========================

class CartItemBase(BaseModel):
    product_id: int
    quantity: int = 1


class CartItemUpdate(BaseModel):
    cart_item_id: int
    quantity: int


class CartItemRemove(BaseModel):
    cart_item_id: int


class CartItemProduct(BaseModel):
    id: int
    name: str
    price: float
    image_url: Optional[str]

    class Config:
        from_attributes = True


class CartItemOut(BaseModel):
    id: int
    product: CartItemProduct
    quantity: int

    class Config:
        from_attributes = True


class CartSummary(BaseModel):
    items: List[CartItemOut]
    subtotal: float
