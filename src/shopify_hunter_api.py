import os
import httpx
import logging
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

class ShopifyHunterAPI:
    """
    Abstração da API da Shopify para o Celery Hunter (Caçador de Oportunidades).
    """
    def __init__(self):
        self.store_url = os.getenv("SHOPIFY_STORE_URL")
        self.access_token = os.getenv("SHOPIFY_ACCESS_TOKEN")
        self.api_version = "2024-01"
        
        if self.store_url:
            self.base_url = f"https://{self.store_url}/admin/api/{self.api_version}"
        else:
            self.base_url = None

    def _get_headers(self):
        return {
            "X-Shopify-Access-Token": self.access_token,
            "Content-Type": "application/json"
        }

    async def fetch_abandoned_checkouts(self, limit=10, hours_ago=168):
        """Busca checkouts abandonados recentes (últimos 7 dias)."""
        if not self.base_url or not self.access_token:
            logger.warning("Faltam credenciais da Shopify (Hunter).")
            return []

        # Calcula a data a partir da qual buscar
        created_at_min = (datetime.utcnow() - timedelta(hours=hours_ago)).isoformat()
        url = f"{self.base_url}/checkouts.json?created_at_min={created_at_min}&limit={limit}"
        
        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(url, headers=self._get_headers(), timeout=15.0)
                response.raise_for_status()
                data = response.json()
                
                checkouts = data.get("checkouts", [])
                
                # Telemetria de Auditoria
                try:
                    import redis
                    import json
                    r = redis.Redis.from_url(os.getenv("REDIS_URL", "redis://localhost:6379/0"), decode_responses=True)
                    log_entry = {"time": "Agora", "origin": "SHOPIFY_API", "action": "FETCH_CHECKOUTS", "dest": f"Encontrados: {len(checkouts)}"}
                    r.lpush("dashboard_logs", json.dumps(log_entry))
                    r.ltrim("dashboard_logs", 0, 19)
                except:
                    pass
                opportunities = []
                
                for ck in checkouts:
                    email = ck.get("email") or ck.get("customer", {}).get("email")
                    phone = ck.get("phone") or ck.get("customer", {}).get("phone")
                    
                    if not email and not phone:
                        continue
                        
                    first_name = ck.get("customer", {}).get("first_name", "Cliente")
                    total_price = ck.get("total_price", "0.00")
                    items = [item.get("title") for item in ck.get("line_items", [])]
                    
                    opportunities.append({
                        "type": "abandoned_cart",
                        "customer_name": first_name,
                        "email": email,
                        "phone": phone,
                        "total_price": total_price,
                        "items": items,
                        "raw_data": ck
                    })
                    
                return opportunities
            except Exception as e:
                logger.error(f"Erro ao buscar checkouts abandonados: {str(e)}")
                return []

    async def fetch_inactive_vip_customers(self, limit=10, days_inactive=7):
        """Busca clientes VIPs que não compram há algum tempo (últimos 7 dias)."""
        if not self.base_url or not self.access_token:
            return []

        url = f"{self.base_url}/customers.json?limit=50"
        
        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(url, headers=self._get_headers(), timeout=15.0)
                response.raise_for_status()
                data = response.json()
                
                customers = data.get("customers", [])
                
                # Telemetria de Auditoria
                try:
                    import redis
                    import json
                    r = redis.Redis.from_url(os.getenv("REDIS_URL", "redis://localhost:6379/0"), decode_responses=True)
                    log_entry = {"time": "Agora", "origin": "SHOPIFY_API", "action": "FETCH_VIP", "dest": f"Total na Base: {len(customers)}"}
                    r.lpush("dashboard_logs", json.dumps(log_entry))
                    r.ltrim("dashboard_logs", 0, 19)
                except:
                    pass
                opportunities = []
                
                cutoff_date = datetime.utcnow() - timedelta(days=days_inactive)
                
                for cust in customers:
                    # Filtro de VIP e inatividade
                    orders_count = cust.get("orders_count", 0)
                    total_spent = float(cust.get("total_spent", "0.0"))
                    
                    last_order_str = cust.get("last_order_name") 
                    # Na API de customer, a data do ultimo pedido pode vir de outras formas.
                    # Vamos simplificar simulando a checagem da data `updated_at` (quando o perfil teve atividade)
                    updated_at_str = cust.get("updated_at")
                    
                    if not updated_at_str:
                        continue
                        
                    updated_at = datetime.fromisoformat(updated_at_str.replace("Z", "+00:00")).replace(tzinfo=None)
                    
                    if total_spent > 100.0 and updated_at < cutoff_date:
                        opportunities.append({
                            "type": "inactive_vip",
                            "customer_name": cust.get("first_name", "Cliente VIP"),
                            "email": cust.get("email"),
                            "phone": cust.get("phone"),
                            "total_spent": total_spent,
                            "days_inactive": (datetime.utcnow() - updated_at).days
                        })
                        
                        if len(opportunities) >= limit:
                            break
                            
                return opportunities
            except Exception as e:
                logger.error(f"Erro ao buscar clientes inativos: {str(e)}")
                return []

shopify_hunter_api = ShopifyHunterAPI()
