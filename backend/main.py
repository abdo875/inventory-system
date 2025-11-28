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
Request_Count = Counter("backend_requests_total", "Total requests", ["route"])
templates = Jinja2Templates(directory="templates")

# Prometheus Functions
# -------------------
@app.get("/metrics")
def metrics():
    return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)

# Dependency for DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# --------------------------
# Home Page - Default (home.html)
# --------------------------
@app.get("/", response_class=HTMLResponse)
def home(request: Request, db: Session = Depends(get_db)):
    Request_Count.labels(route="/").inc()
    products = db.query(Product).all()
    return templates.TemplateResponse("home.html", {"request": request, "products": products})

# --------------------------
# Admin/Special Page - Accessible via special link (index.html)
# --------------------------
@app.get("/admin/dashboard", response_class=HTMLResponse)
def admin_dashboard(request: Request, db: Session = Depends(get_db)):
    Request_Count.labels(route="/admin/dashboard").inc()
    products = db.query(Product).all()
    return templates.TemplateResponse("index.html", {"request": request, "products": products})

# Alternative: Use a secret token in the URL
@app.get("/special/{secret_token}", response_class=HTMLResponse)
def special_page(secret_token: str, request: Request, db: Session = Depends(get_db)):
    # Only allow access if the secret token matches
    VALID_TOKEN = "my-secret-12345"  # Change this to your secret
    
    if secret_token != VALID_TOKEN:
        return RedirectResponse(url="/", status_code=303)
    
    Request_Count.labels(route="/special").inc()
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
# Shopping Cart Page
# --------------------------
@app.get("/cart",response_class=HTMLResponse)
def shopping_cart(request:Request,db:Session=Depends(get_db)):
    Request_Count.labels(route="/cart").inc()
    products=db.query(Product).all()
    return templates.TemplateResponse("cart.html",{"request":request,"products":products})


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
