# Usamos uma imagem Python oficial leve
FROM python:3.11-slim

# Evita que o Python grave arquivos .pyc no disco e força os logs a aparecerem no container
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

WORKDIR /app

# Instala dependências do sistema necessárias para compilar bibliotecas (como asyncpg e pgvector)
RUN apt-get update && apt-get install -y gcc libpq-dev && rm -rf /var/lib/apt/lists/*

# Copia os requisitos e instala
# Configurações do PIP para economizar Memória RAM no Build (OOM Killer Defense)
ENV PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PIP_DEFAULT_TIMEOUT=120

# Copia os requisitos
COPY requirements.txt .

# Atualiza pip e ferramentas essenciais primeiro
RUN pip install --upgrade pip setuptools wheel

# Instala em duas levas para evitar estourar a RAM (OOM) no dependency resolver
RUN head -n 10 requirements.txt > req_base.txt && pip install -r req_base.txt
RUN tail -n +11 requirements.txt > req_heavy.txt && pip install -r req_heavy.txt

# Copia todo o código fonte para dentro da imagem
COPY . .

# Expõe a porta que o FastAPI usará
EXPOSE 8000

# O comando padrão iniciará a API web. 
# No Coolify, para criar o Worker, você fará um "Override" do comando de start para: celery -A src.celery_app worker -l info
CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]
