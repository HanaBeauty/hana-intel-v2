import os
import logging
from langchain_openai import ChatOpenAI
from langchain_google_genai import ChatGoogleGenerativeAI
from typing import Optional

logger = logging.getLogger(__name__)

class LLMFactory:
    """
    Fábrica responsável por alternar entre os cérebros de IA do projeto Hana Intel 2.0.
    Permite instanciar OpenAI, Gemini ou DeepSeek nativamente.
    """
    
    @staticmethod
    def get_llm(provider: str = "openai", model_name: Optional[str] = None):
        if provider == "openai":
            api_key = os.getenv("OPENAI_API_KEY")
            model = model_name or "gpt-4o-mini"
            if not api_key:
                error_msg = "OPENAI_API_KEY ausente em produção!"
                logger.warning(error_msg)
                try:
                    import redis
                    import json
                    redis_url = os.getenv("REDIS_URL", "redis://localhost:6379/0")
                    r = redis.Redis.from_url(redis_url, decode_responses=True)
                    log_entry = {"time": "Agora", "origin": "LLM_FACTORY", "action": "AUTH_ERROR", "dest": error_msg}
                    r.lpush("dashboard_logs", json.dumps(log_entry))
                    r.ltrim("dashboard_logs", 0, 19)
                except:
                    pass
                return None
            return ChatOpenAI(model=model, api_key=api_key, temperature=0.7)
            
        elif provider == "deepseek":
            api_key = os.getenv("DEEPSEEK_API_KEY")
            model = model_name or "deepseek-chat"
            # DeepSeek utiliza o formato padrão de API da OpenAI através de uma base_url
            if not api_key:
                logger.warning("DEEPSEEK_API_KEY ausente.")
                return None
            return ChatOpenAI(
                model=model, 
                api_key=api_key, 
                base_url="https://api.deepseek.com", 
                temperature=0.7
            )
            
        elif provider == "gemini":
            api_key = os.getenv("GEMINI_API_KEY")
            model = model_name or "gemini-1.5-flash"
            if not api_key:
                logger.warning("GEMINI_API_KEY ausente.")
                return None
            return ChatGoogleGenerativeAI(model=model, google_api_key=api_key, temperature=0.7)
            
        else:
            raise ValueError(f"Provedor LLM '{provider}' não suportado.")
