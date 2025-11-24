from fastapi import FastAPI, Depends, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from database import SessionLocal, engine, Base
from models import Product

# Create tables
Base.metadata.create_all(bind=engine)

app = FastAPI()
templates = Jinja2Templates(directory="templates")

# Dependency for DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# --------------------------
# Home Page - Show Products
# --------------------------
@app.get("/", response_class=HTMLResponse)
def home(request: Request, db: Session = Depends(get_db)):
    products = db.query(Product).all()
    return templates.TemplateResponse("index.html", {"request": request, "products": products})


# --------------------------
# Add Product (HTML Form)
# --------------------------
@app.post("/add")
def add_product(
    name: str = Form(...),
    quantity: int = Form(...),
    db: Session = Depends(get_db)
):
    product = Product(name=name, quantity=quantity)
    db.add(product)
    db.commit()
    return RedirectResponse(url="/", status_code=303)


# --------------------------
# Delete Product (HTML Form)
# --------------------------
@app.post("/delete")
def delete_product(
    pid: int = Form(...),
    db: Session = Depends(get_db)
):
    product = db.query(Product).filter(Product.id == pid).first()
    if product:
        db.delete(product)
        db.commit()
    return RedirectResponse(url="/", status_code=303)
