# backend/crud.py
from typing import List, Optional
from sqlalchemy.orm import Session
from passlib.context import CryptContext

from models import User, Product, CartItem
from schemas import UserCreate, ProductCreate

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
MAX_PASSWORD_LENGTH = 72  # bcrypt limit


# -------- Password helpers --------
def get_password_hash(password: str) -> str:
    password = password[:MAX_PASSWORD_LENGTH]
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    plain_password = plain_password[:MAX_PASSWORD_LENGTH]
    return pwd_context.verify(plain_password, hashed_password)


# ========================= USERS =========================

def get_user_by_username(db: Session, username: str) -> Optional[User]:
    return db.query(User).filter(User.username == username).first()


def get_user(db: Session, user_id: int) -> Optional[User]:
    return db.query(User).filter(User.id == user_id).first()


def create_user(db: Session, user_in: UserCreate) -> User:
    # أول يوزر في الداتا بيز يبقى admin
    is_first_user = db.query(User).count() == 0

    hashed_password = get_password_hash(user_in.password)
    user = User(
        username=user_in.username,
        email=user_in.email,
        hashed_password=hashed_password,
        is_admin=is_first_user,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def authenticate_user(db: Session, username: str, password: str) -> Optional[User]:
    user = get_user_by_username(db, username)
    if not user:
        return None
    if not verify_password(password, user.hashed_password):
        return None
    return user


# ======================== PRODUCTS =======================

def get_products(db: Session) -> List[Product]:
    return db.query(Product).all()


def get_product(db: Session, product_id: int) -> Optional[Product]:
    return db.query(Product).filter(Product.id == product_id).first()


def create_product(db: Session, product_in: ProductCreate) -> Product:
    product = Product(**product_in.dict())
    db.add(product)
    db.commit()
    db.refresh(product)
    return product


def delete_product(db: Session, product_id: int) -> bool:
    product = get_product(db, product_id)
    if not product:
        return False
    db.delete(product)
    db.commit()
    return True


# ========================== CART =========================

def get_cart_items(db: Session, user_id: int) -> List[CartItem]:
    return (
        db.query(CartItem)
        .filter(CartItem.user_id == user_id)
        .join(CartItem.product)
        .all()
    )


def add_to_cart(db: Session, user_id: int, product_id: int, quantity: int = 1) -> CartItem:
    item = (
        db.query(CartItem)
        .filter(CartItem.user_id == user_id, CartItem.product_id == product_id)
        .first()
    )
    if item:
        item.quantity += quantity
    else:
        item = CartItem(user_id=user_id, product_id=product_id, quantity=quantity)
        db.add(item)

    db.commit()
    db.refresh(item)
    return item


def update_cart_item(db: Session, user_id: int, cart_item_id: int, quantity: int) -> Optional[CartItem]:
    item = (
        db.query(CartItem)
        .filter(CartItem.id == cart_item_id, CartItem.user_id == user_id)
        .first()
    )
    if not item:
        return None

    if quantity <= 0:
        db.delete(item)
        db.commit()
        return None

    item.quantity = quantity
    db.commit()
    db.refresh(item)
    return item


def remove_cart_item(db: Session, user_id: int, cart_item_id: int) -> bool:
    item = (
        db.query(CartItem)
        .filter(CartItem.id == cart_item_id, CartItem.user_id == user_id)
        .first()
    )
    if not item:
        return False

    db.delete(item)
    db.commit()
    return True


def clear_cart(db: Session, user_id: int) -> None:
    db.query(CartItem).filter(CartItem.user_id == user_id).delete()
    db.commit()
