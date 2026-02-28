import os
from langchain_openai import ChatOpenAI
from langchain_core.prompts import PromptTemplate

# Placeholder simples do LangChain para inicializar a IA
class HanaAICoreManager:
    def __init__(self):
        self.api_key = os.getenv("OPENAI_API_KEY")
        # Por padrão usa o GPT-4o-mini para respostas rápidas de API, mas pode ser configurado.
        if self.api_key:
            self.llm = ChatOpenAI(temperature=0.7, model="gpt-4o-mini", api_key=self.api_key)
        else:
            self.llm = None

    async def process_intent(self, user_intent: str) -> dict:
        if not self.llm:
            return {
                "status": "warning",
                "message": "API Key não configurada. MODO DEMO",
                "response": f"Intenção recebida: '{user_intent}'. Configure a OPENAI_API_KEY para respostas reais."
            }
        
        prompt = PromptTemplate(
            input_variables=["intent"],
            template="Você é a Hana AI Core 2.0. O usuário pediu: {intent}. Responda de forma executiva e direta confirmando o recebimento da tarefa."
        )
        
        chain = prompt | self.llm
        
        try:
            # invocação assíncrona
            result = await chain.ainvoke({"intent": user_intent})
            return {
                "status": "success",
                "message": "Intenção processada com sucesso via LangChain.",
                "response": result.content
            }
        except Exception as e:
            return {
                "status": "error",
                "message": f"Erro ao processar intenção: {str(e)}"
            }

manager = HanaAICoreManager()
