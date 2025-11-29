FROM python:3.10-slim

WORKDIR /app

# dependencies for bcrypt to build correctly
RUN apt-get update && apt-get install -y build-essential python3-dev libffi-dev

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
