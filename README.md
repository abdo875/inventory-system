# Inventory Management System – DevOps Project

This project is a fully containerized, production-ready **Inventory Management System** deployed using a complete **DevOps pipeline**.  
The system provides simple inventory operations (Add / View / Delete products) and is fully monitored using Prometheus, Grafana, and cAdvisor.

This project is developed as part of the **DEPI DevOps Track Graduation Project**.

---

## 🚀 Features

- Add new products with name & quantity  
- View all stored products  
- Delete products by ID  
- Backend built with **FastAPI**  
- Frontend rendered with **Jinja2 (HTML templates)**  
- SQLite lightweight database  
- Fully Dockerized  
- CI/CD automation via Jenkins  
- Deployment on AWS EC2  
- Monitoring & metrics dashboard (Prometheus + Grafana)  
- System-level metrics via cAdvisor  
- Custom `/metrics` endpoint for FastAPI  

---

## 🏗️ Architecture Overview

(Architecture diagram text removed for txt formatting)

---

## 🧰 Tech Stack

### Backend
- FastAPI  
- SQLAlchemy  
- SQLite  
- Jinja2 Templates  

### DevOps
- Docker  
- Docker Compose  
- Jenkins CI/CD  
- AWS EC2  
- Ansible  

### Monitoring
- Prometheus  
- Grafana  
- cAdvisor  
- prometheus-fastapi-instrumentator  

---

## 📁 Project Structure

inventory-system/
│
├── backend/
│   ├── main.py
│   ├── models.py
│   ├── database.py
│   ├── crud.py
│   ├── schemas.py
│   ├── requirements.txt
│   ├── Dockerfile
│   ├── templates/
│   │    └── index.html
│   └── static/
│        └── style.css
│
└── monitoring/
    ├── docker-compose-monitor.yml
    └── prometheus.yml

---

## 🐳 Backend – Docker Build & Run

docker build -t inventory-backend .
docker run -d --name inventory-backend -p 8000:8000 inventory-backend

Access backend UI:
http://SERVER_IP:8000

---

## 📦 Monitoring Stack

cd /opt/monitoring
docker compose -f docker-compose-monitor.yml up -d

Prometheus → http://SERVER_IP:9090  
Grafana → http://SERVER_IP:3000  
cAdvisor → http://SERVER_IP:8080  

Grafana Login:
admin / admin

---

## 📡 Prometheus Config

global:
  scrape_interval: 15s

scrape_configs:
  - job_name: 'prometheus'
    static_configs:
      - targets: ['prometheus:9090']

  - job_name: 'cadvisor'
    static_configs:
      - targets: ['cadvisor:8080']

  - job_name: 'inventory-backend'
    metrics_path: /metrics
    static_configs:
      - targets: ['inventory-backend:8000']

---

## 📊 Grafana Dashboards

Recommended dashboard IDs:
8937 – Docker Monitor  
15172 – FastAPI Metrics  

---

## ⚙️ CI/CD with Jenkins

Pipeline Stages:
1. Clone repo  
2. Build Docker image  
3. Run tests  
4. Push image to Docker Hub  
5. Deploy to AWS EC2  

(Jenkinsfile omitted for txt format)

---

## ☁️ AWS Deployment

1. Launch EC2  
2. Install Docker  
3. Pull backend image  
4. Run container  
5. Launch monitoring stack  

---

## 🏁 Conclusion

This project demonstrates the entire DevOps lifecycle:
- Backend development  
- Containerization  
- CI/CD  
- Cloud deployment  
- Monitoring & observability  

---

## 👤 Author
Abdelrahman Mostafa