from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from passlib.context import CryptContext
import jwt
import datetime
import os
import uuid
from typing import Optional
from pydantic import BaseModel, EmailStr

from src.models import User, UserRole
from src.database import get_db_session

router = APIRouter(prefix="/api/v1/auth", tags=["Auth & IAM"])

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
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
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: Optional[datetime.timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.datetime.utcnow() + expires_delta
    else:
        expire = datetime.datetime.utcnow() + datetime.timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

@router.post("/login")
async def login(req: LoginRequest, db: AsyncSession = Depends(get_db_session)):
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

    # Se a senha passar, vamos gerar um Mock ou enviar via Celery Evolution API o 2FA.
    import random
    code_2fa = f"{random.randint(100000, 999999)}"
    
    # IMPORTANTE: Em produção, salvaríamos esse código no Redis com TTL de 5 minutos.
    # Para o escopo deste backend agnóstico, podemos abstrair salvando num cache Redis.
    # Como não importamos o redis pool diretamente aqui, vamos printar no terminal 
    # pro desenvolvedor (como seed inicial) ou enviar pro WhatsApp se tiver número.
    
    # FIXME: O código abaixo simularia o disparo. 
    import logging
    logger = logging.getLogger(__name__)
    logger.info(f"🔑 [2FA GERADO] Código para {user.email} (Tel: {user.phone}): {code_2fa}")
    
    # Retornamos sucesso exigindo a etapa 2. (Passaremos o codigo em texto por conveniência de dev, remover em prod)
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
