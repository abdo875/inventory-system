from fastapi import FastAPI, Depends, Request, Form, Response
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from prometheus_client import Counter, generate_latest, CONTENT_TYPE_LATEST

from database import SessionLocal, engine, Base
from models import Product

# Create tables
Base.metadata.create_all(bind=engine)

app = FastAPI()
Request_Count=Counter("backend_requests_total","Total requests",["route"])
templates = Jinja2Templates(directory="templates")

#Promethus Functions
#-------------------
@app.get("/metrics")
def metrics():
    return Response(generate_latest(),media_type=CONTENT_TYPE_LATEST) 


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
    Request_Count.labels(route="/").inc() #taking metrics from here
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


