#!/bin/bash
# Script de Backup Incremental do PostgreSQL (Hana Intel V3 Enterprise)
# Projetado para ser configurado como "Cronjob" no Coolify ou no S.O local

# O diretório precisa estar mapeado com Valumes no Docker se quiser perenidade
BACKUP_DIR="./backups"
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
DB_NAME="hana_intel"
DB_USER="postgres"
DB_HOST="localhost"
DB_PORT="5432"
FILENAME="$BACKUP_DIR/backup_${DB_NAME}_${TIMESTAMP}.sql"

mkdir -p "$BACKUP_DIR"

echo "⏳ [Hana Enterprise] Iniciando extração (pg_dump) do banco $DB_NAME..."
# Usa as variaveis de ambiente ou os falbacks locais
export PGPASSWORD=${DB_PASSWORD:-"postgres"} 

pg_dump -U "$DB_USER" -h "$DB_HOST" -p "$DB_PORT" "$DB_NAME" > "$FILENAME"

if [ $? -eq 0 ]; then
    echo "✅ Backup lógico realizado com sucesso: $FILENAME"
    
    # Compactação imediata para economizar disco do Cloud
    gzip "$FILENAME"
    echo "🗜️  Compactado para: $FILENAME.gz"
    
    # Rotatividade de Dados: Mantém os backups dos últimos 7 dias, exclui o resto (Governance)
    ls -t $BACKUP_DIR/*.gz | tail -n +8 | xargs -I {} rm -- {}
    echo "🧹 Rotatividade concluída (Mantendo os 7 backups mais recentes)."
else
    echo "❌ Falha massiva ao realizar backup corporativo!"
    exit 1
fi
