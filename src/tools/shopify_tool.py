from pydantic import BaseModel, Field
from operator import itemgetter
from crewai.tools import BaseTool
from typing import Type
import requests
import logging
import os

logger = logging.getLogger(__name__)

class ShopifyCustomerActivityInput(BaseModel):
    email: str = Field(..., description="E-mail do cliente para buscar histórico e valor vitalício (LTV). Ex: cliente@email.com")

class ShopifyAbandonedCartInput(BaseModel):
    limit: int = Field(default=5, description="Número máximo de carrinhos abandonados recentes a retornar.")

class ShopifyCustomerActivityTool(BaseTool):
    name: str = "Buscar Histórico do Cliente na Shopify"
    description: str = (
        "Utilize esta ferramenta para buscar o histórico de pedidos, LTV (Lifetime Value) "
        "e a data do último pedido de um cliente específico pelo e-mail na loja da Hana Beauty."
    )
    args_schema: Type[BaseModel] = ShopifyCustomerActivityInput

    def _run(self, email: str) -> str:
        shop_url = os.getenv("SHOPIFY_STORE_URL")
        access_token = os.getenv("SHOPIFY_ACCESS_TOKEN")
        
        if not shop_url or not access_token:
            logger.warning("Faltam credenciais da Shopify. Mocking response.")
            return f"Mock: Cliente {email} possui LTV de R$ 450,00 e seu último pedido foi há 15 dias."

        headers = {
            "Content-Type": "application/json",
            "X-Shopify-Access-Token": access_token
        }
        
        # 1. Buscar Cliente pelo e-mail
        search_url = f"https://{shop_url}/admin/api/2024-01/customers/search.json?query=email:{email}"
        
        try:
            response = requests.get(search_url, headers=headers)
            response.raise_for_status()
            data = response.json()
            
            customers = data.get("customers", [])
            if not customers:
                return f"Cliente {email} não encontrado na base da Shopify."
                
            customer = customers[0]
            orders_count = customer.get("orders_count", 0)
            total_spent = customer.get("total_spent", "0.00")
            
            return (
                f"Cliente: {customer.get('first_name')} {customer.get('last_name')}\n"
                f"Total de Pedidos: {orders_count}\n"
                f"LTV (Total Gasto): R$ {total_spent}\n"
                f"Criado em: {customer.get('created_at')}"
            )
            
        except Exception as e:
            logger.error(f"Erro ao acessar Shopify API: {str(e)}")
            return f"Erro ao consultar a loja Shopify: {str(e)}"

class ShopifyAbandonedCartTool(BaseTool):
    name: str = "Buscar Carrinhos Abandonados Shopify"
    description: str = (
        "Utilize esta ferramenta para identificar checkouts que os clientes "
        "da Hana Beauty começaram mas não finalizaram (Carrinhos Abandonados)."
    )
    args_schema: Type[BaseModel] = ShopifyAbandonedCartInput

    def _run(self, limit: int = 5) -> str:
        shop_url = os.getenv("SHOPIFY_STORE_URL")
        access_token = os.getenv("SHOPIFY_ACCESS_TOKEN")
        
        if not shop_url or not access_token:
            logger.warning("Faltam credenciais da Shopify. Mocking response.")
            return (
                "Mock: 2 Carrinhos Abandonados Encontrados.\n"
                "1. E-mail: teste1@gmail.com - Produto: Pincel Oval.\n"
                "2. E-mail: teste2@gmail.com - Produto: Cola Amlash."
            )

        headers = {
            "Content-Type": "application/json",
            "X-Shopify-Access-Token": access_token
        }
        
        # 2. Buscar Checkouts Abandonados
        checkout_url = f"https://{shop_url}/admin/api/2024-01/checkouts.json?limit={limit}"
        
        try:
            response = requests.get(checkout_url, headers=headers)
            response.raise_for_status()
            data = response.json()
            
            checkouts = data.get("checkouts", [])
            if not checkouts:
                return "Nenhum carrinho abandonado encontrado recentemente."
                
            result = f"Encontrados {len(checkouts)} carrinhos abandonados:\n"
            for i, ck in enumerate(checkouts, 1):
                email = ck.get("email", ck.get("customer", {}).get("email", "Sem Email"))
                total_price = ck.get("total_price", "0.00")
                items = [item.get("title") for item in ck.get("line_items", [])]
                items_str = ", ".join(items) if items else "Itens não identificados"
                result += f"{i}. E-mail: {email} | Valor: R$ {total_price} | Produtos: {items_str}\n"
                
            return result
            
        except Exception as e:
            logger.error(f"Erro ao acessar Shopify Checkouts API: {str(e)}")
            return f"Erro ao consultar checkouts da Shopify: {str(e)}"
