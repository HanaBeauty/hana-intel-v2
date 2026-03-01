#!/bin/bash

# Inicia o Celery Worker em background (esconde os logs detalhados para não poluir o console, ou os deixa com -l info)
echo "Iniciando Celery Worker..."
celery -A src.celery_app worker -l info &

# Inicia o servidor Web FastAPI em foreground
echo "Iniciando FastAPI..."
uvicorn src.main:app --host 0.0.0.0 --port 8000
