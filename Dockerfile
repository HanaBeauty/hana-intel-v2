# ----------------------------------------
# 1. ESTÁGIO DE BUILD DO FRONTEND (REACT)
# ----------------------------------------
FROM node:20-slim AS frontend-builder
WORKDIR /app/frontend

# Instala dependências e compila
COPY frontend/package*.json ./
RUN npm install
COPY frontend .
RUN npm run build

# ----------------------------------------
# 2. ESTÁGIO DE BUILD DO BACKEND (PYTHON)
# ----------------------------------------
FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

WORKDIR /app

RUN apt-get update && apt-get install -y gcc libpq-dev && rm -rf /var/lib/apt/lists/*

ENV PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PIP_DEFAULT_TIMEOUT=120

COPY requirements.txt .
RUN pip install --upgrade pip setuptools wheel
RUN pip install --no-cache-dir -r requirements.txt

# Copia código fonte do Python
COPY . .

# Copia a pasta de build do React (Dashboard V2)
COPY --from=frontend-builder /app/frontend/dist /app/frontend/dist

COPY start.sh .
RUN chmod +x start.sh

EXPOSE 8000
CMD ["./start.sh"]
