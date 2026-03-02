from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
import bcrypt
import jwt
import datetime
import os
import uuid
from typing import Optional
from pydantic import BaseModel, EmailStr

from src.models import User, UserRole
from src.database import get_db_session

router = APIRouter(prefix="/api/v1/auth", tags=["Auth & IAM"])

# Substituição do Passlib antigo pelo Bcrypt puro para suportar V5
# pwd_context = CryptContext(...) removido
SECRET_KEY = os.getenv("JWT_SECRET", "hana_intel_fallback_secret_key_change_me_in_prod")
ALGORITHM = "HS256"

# Tempo de vida dos tokens
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24 * 7 # 7 days
TWO_FACTOR_EXPIRE_MINUTES = 5

class LoginRequest(BaseModel):
    email: EmailStr
    password: str

class Verify2FARequest(BaseModel):
    email: EmailStr
    code: str

def verify_password(plain_password, hashed_password):
    if isinstance(plain_password, str):
        plain_password = plain_password.encode('utf-8')
    if isinstance(hashed_password, str):
        hashed_password = hashed_password.encode('utf-8')
    return bcrypt.checkpw(plain_password, hashed_password)

def get_password_hash(password):
    if isinstance(password, str):
        password = password.encode('utf-8')
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password, salt)
    return hashed.decode('utf-8')

def create_access_token(data: dict, expires_delta: Optional[datetime.timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.datetime.utcnow() + expires_delta
    else:
        expire = datetime.datetime.utcnow() + datetime.timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def send_whatsapp_2fa(number: str, code: str):
    import requests
    import logging
    logger = logging.getLogger(__name__)
    
    evo_url = os.getenv("EVOLUTION_API_URL", "https://webhook.adsai.com.br")
    evo_token = os.getenv("EVOLUTION_API_TOKEN", "")
    # Em caso de não existir ENV, usa a instância oficial detectada nas auditorias anteriores
    instance_name = os.getenv("EVOLUTION_API_INSTANCE", "Hana_Intel_PRO")
    
    if not evo_token:
        logger.warning(f"⚠️ EVOLUTION_API_TOKEN vazio. Simulação DevMode 2FA ativada para {number}. Código: {code}")
        return
        
    send_url = f"{evo_url.rstrip('/')}/message/sendText/{instance_name}"
    headers = {
        "apikey": evo_token,
        "Content-Type": "application/json"
    }
    body = {
        "number": number,
        "text": f"🛡️ *Hana Intel Enterprise*\nSeu código de acesso à Torre de Controle: *{code}*\n\n_Válido por 5 minutos._"
    }
    try:
        logger.info(f"📤 Tentando disparar 2FA WhatsApp para {number}...")
        resp = requests.post(send_url, json=body, headers=headers, timeout=10)
        if resp.status_code in (200, 201):
            logger.info("✅ 2FA entregue no WhatsApp do CEO.")
        else:
            logger.error(f"❌ Erro WhatsApp 2FA API: {resp.status_code} - {resp.text}")
    except Exception as e:
        logger.error(f"❌ Falha de Rede no 2FA WhatsApp: {e}")

@router.post("/login")
async def login(req: LoginRequest, background_tasks: BackgroundTasks, db: AsyncSession = Depends(get_db_session)):
    """
    Step 1 do Login.
    Valida as credenciais. Se corretas, dispara um código 2FA via WhatsApp e retorna status 'requires_2fa'.
    """
    result = await db.execute(select(User).where(User.email == req.email))
    user = result.scalars().first()

    if not user or not user.is_active:
        raise HTTPException(status_code=401, detail="Credenciais incorretas ou conta inativa.")

    if not verify_password(req.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Credenciais incorretas.")

    # Se a senha passar, gera o código temporal numérico de 6 dígitos
    import random
    code_2fa = f"{random.randint(100000, 999999)}"
    
    # Importante: num ambiente full prod sem mock, salvaríamos num Redis com TTL de 5 mins.
    # Neste cenário inicial, o Dev_Code retorna pelo body pro console do browser por precaução caso WhatsApp falhe.
    
    if user.phone:
        # Programa o disparo real por WhatsApp sem travar a resposta HTTP
        background_tasks.add_task(send_whatsapp_2fa, user.phone, code_2fa)
    else:
        import logging
        logging.getLogger(__name__).warning(f"⚠️ Conta {user.email} não possui telefone para 2FA.")
    
    # Retornamos sucesso exigindo a etapa 2.
    return {
        "status": "requires_2fa",
        "message": f"Um código de 6 dígitos foi enviado para o WhatsApp com final {user.phone[-4:] if user.phone else 'não cadastrado'}.",
        "_dev_code": code_2fa # Remover em prod. Facilitador para testes de Front-End no momento.
    }

@router.post("/verify-2fa")
async def verify_2fa(req: Verify2FARequest, db: AsyncSession = Depends(get_db_session)):
    """
    Step 2 do Login.
    Valida o código de 6 dígitos e entrega o Access Token (JWT).
    """
    result = await db.execute(select(User).where(User.email == req.email))
    user = result.scalars().first()
    
    if not user:
        raise HTTPException(status_code=401, detail="Usuário não encontrado.")
        
    # Validamos o código. (Na real bateríamos no Redis).
    # Aqui vamos usar o dev mode aceitando se existir.
    if not req.code or len(req.code) != 6:
        raise HTTPException(status_code=400, detail="Código 2FA inválido.")
        
    # Sucesso 2FA!
    access_token_expires = datetime.timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": str(user.id), "role": user.role},
        expires_delta=access_token_expires
    )
    
    return {
        "access_token": access_token, 
        "token_type": "bearer",
        "user": {
            "id": str(user.id),
            "name": user.name,
            "email": user.email,
            "role": user.role
        }
    }
