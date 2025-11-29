# backend/main.py

import os
import shutil
import time
from typing import Optional

from fastapi import (
    FastAPI,
    Depends,
    Request,
    Form,
    HTTPException,
    UploadFile,
    File,
)
from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from sqlalchemy.orm import Session

from database import Base, engine, get_db
from models import User, Product, CartItem
import crud
import schemas

app = FastAPI()

# إنشاء الجداول
Base.metadata.create_all(bind=engine)

# static + templates
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

COOKIE_NAME = "user_id"
UPLOAD_DIR = "static/uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)


# ====================== Helpers ======================

def get_current_user_id(request: Request) -> Optional[int]:
    user_id = request.cookies.get(COOKIE_NAME)
    if not user_id:
        return None
    try:
        return int(user_id)
    except ValueError:
        return None


def ensure_user(request: Request, db: Session) -> Optional[User]:
    user_id = get_current_user_id(request)
    if not user_id:
        return None
    return crud.get_user(db, user_id)


def ensure_admin(request: Request, db: Session) -> User:
    user = ensure_user(request, db)
    if not user or not user.is_admin:
        raise HTTPException(status_code=403, detail="Admins only")
    return user


# ==================== Auth pages =====================

@app.get("/signup", response_class=HTMLResponse)
def signup_page(request: Request):
    return templates.TemplateResponse("signup.html", {"request": request})


@app.post("/signup")
def signup(
    request: Request,
    username: str = Form(...),
    email: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db),
):
    if crud.get_user_by_username(db, username):
        return templates.TemplateResponse(
            "signup.html",
            {"request": request, "error": "Username already taken"},
            status_code=400,
        )

    user_in = schemas.UserCreate(username=username, email=email, password=password)
    user = crud.create_user(db, user_in)

    resp = RedirectResponse(url="/", status_code=303)
    resp.set_cookie(COOKIE_NAME, str(user.id), httponly=True)
    return resp


@app.get("/login", response_class=HTMLResponse)
def login_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})


@app.post("/login")
def login(
    request: Request,
    username: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db),
):
    user = crud.authenticate_user(db, username, password)
    if not user:
        return templates.TemplateResponse(
            "login.html",
            {"request": request, "error": "Invalid username or password"},
            status_code=400,
        )

    resp = RedirectResponse(url="/", status_code=303)
    resp.set_cookie(COOKIE_NAME, str(user.id), httponly=True)
    return resp


@app.get("/logout")
def logout():
    resp = RedirectResponse(url="/", status_code=303)
    resp.delete_cookie(COOKIE_NAME)
    return resp


# ======================= Pages ========================

@app.get("/", response_class=HTMLResponse)
def home(request: Request, db: Session = Depends(get_db)):
    products = crud.get_products(db)
    user = ensure_user(request, db)
    return templates.TemplateResponse(
        "home.html",
        {"request": request, "products": products, "user": user},
    )


@app.get("/product/{product_id}", response_class=HTMLResponse)
def product_detail(
    product_id: int, request: Request, db: Session = Depends(get_db)
):
    product = crud.get_product(db, product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    user = ensure_user(request, db)
    return templates.TemplateResponse(
        "product.html",
        {"request": request, "product": product, "user": user},
    )


@app.get("/cart", response_class=HTMLResponse)
def cart_page(request: Request, db: Session = Depends(get_db)):
    user = ensure_user(request, db)
    if not user:
        return RedirectResponse(url="/login", status_code=303)

    items = crud.get_cart_items(db, user.id)
    subtotal = sum(i.product.price * i.quantity for i in items)

    return templates.TemplateResponse(
        "cart.html",
        {
            "request": request,
            "items": items,
            "subtotal": subtotal,
            "user": user,
        },
    )


@app.post("/checkout", response_class=HTMLResponse)
def checkout(request: Request, db: Session = Depends(get_db)):
    user = ensure_user(request, db)
    if not user:
        return RedirectResponse(url="/login", status_code=303)

    items = crud.get_cart_items(db, user.id)
    subtotal = sum(i.product.price * i.quantity for i in items)
    crud.clear_cart(db, user.id)

    return templates.TemplateResponse(
        "checkout_success.html",
        {"request": request, "amount": subtotal, "user": user},
    )


# ===================== Admin pages =====================

@app.get("/admin/dashboard", response_class=HTMLResponse)
def admin_dashboard(request: Request, db: Session = Depends(get_db)):
    admin = ensure_admin(request, db)
    products = crud.get_products(db)
    return templates.TemplateResponse(
        "admin_dashboard.html",
        {"request": request, "products": products, "user": admin},
    )


@app.get("/admin/products/new", response_class=HTMLResponse)
def admin_new_product_page(request: Request, db: Session = Depends(get_db)):
    admin = ensure_admin(request, db)
    return templates.TemplateResponse(
        "admin_product_form.html",
        {"request": request, "user": admin},
    )


@app.post("/admin/products/new")
def admin_create_product(
    request: Request,
    name: str = Form(...),
    description: str = Form(""),
    price: float = Form(...),
    stock: int = Form(0),
    image: UploadFile = File(None),
    db: Session = Depends(get_db),
):
    admin = ensure_admin(request, db)

    image_url = None
    if image and image.filename:
        ext = os.path.splitext(image.filename)[1]
        filename = f"{int(time.time())}{ext}"
        file_path = os.path.join(UPLOAD_DIR, filename)
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(image.file, buffer)
        image_url = f"/static/uploads/{filename}"

    product_in = schemas.ProductCreate(
        name=name,
        description=description,
        price=price,
        stock=stock,
        image_url=image_url,
    )
    crud.create_product(db, product_in)

    return RedirectResponse(url="/admin/dashboard", status_code=303)


@app.post("/admin/products/{product_id}/delete")
def admin_delete_product(
    product_id: int,
    request: Request,
    db: Session = Depends(get_db),
):
    admin = ensure_admin(request, db)
    ok = crud.delete_product(db, product_id)
    if not ok:
        raise HTTPException(status_code=404, detail="Product not found")
    return RedirectResponse(url="/admin/dashboard", status_code=303)


# ===================== Cart API (AJAX) =====================

@app.post("/api/cart/add", response_model=schemas.CartItemOut)
async def api_cart_add(
    data: schemas.CartItemBase,
    request: Request,
    db: Session = Depends(get_db),
):
    user = ensure_user(request, db)
    if not user:
        raise HTTPException(status_code=401, detail="Not logged in")

    product = crud.get_product(db, data.product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    item = crud.add_to_cart(db, user.id, data.product_id, data.quantity)
    return schemas.CartItemOut(
        id=item.id,
        quantity=item.quantity,
        product=item.product,
    )


@app.post("/api/cart/update", response_model=schemas.CartItemOut)
async def api_cart_update(
    data: schemas.CartItemUpdate,
    request: Request,
    db: Session = Depends(get_db),
):
    user = ensure_user(request, db)
    if not user:
        raise HTTPException(status_code=401, detail="Not logged in")

    item = crud.update_cart_item(db, user.id, data.cart_item_id, data.quantity)
    if not item:
        raise HTTPException(status_code=404, detail="Cart item not found")

    return schemas.CartItemOut(
        id=item.id,
        quantity=item.quantity,
        product=item.product,
    )


@app.post("/api/cart/remove")
async def api_cart_remove(
    data: schemas.CartItemRemove,
    request: Request,
    db: Session = Depends(get_db),
):
    user = ensure_user(request, db)
    if not user:
        raise HTTPException(status_code=401, detail="Not logged in")

    ok = crud.remove_cart_item(db, user.id, data.cart_item_id)
    if not ok:
        raise HTTPException(status_code=404, detail="Cart item not found")

    return JSONResponse({"success": True})


@app.get("/api/cart/summary", response_model=schemas.CartSummary)
async def api_cart_summary(
    request: Request,
    db: Session = Depends(get_db),
):
    user = ensure_user(request, db)
    if not user:
        raise HTTPException(status_code=401, detail="Not logged in")

    items = crud.get_cart_items(db, user.id)
    subtotal = sum(i.product.price * i.quantity for i in items)
    items_out = [
        schemas.CartItemOut(
            id=i.id,
            quantity=i.quantity,
            product=i.product,
        )
        for i in items
    ]

    return schemas.CartSummary(items=items_out, subtotal=subtotal)
