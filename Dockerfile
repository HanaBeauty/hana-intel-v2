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

# Dependências estritamente tipadas, garantindo que o OOM não ocorrerá por backtracking
RUN pip install --no-cache-dir -r requirements.txt

# Copia todo o código fonte para dentro da imagem
COPY . .

# Garante que o script de inícialização unificado tem permissão de execução
COPY start.sh .
RUN chmod +x start.sh

# Expõe a porta que o FastAPI usará
EXPOSE 8000

# O comando padrão iniciará a API web e o Celery Worker no próprio container
CMD ["./start.sh"]
