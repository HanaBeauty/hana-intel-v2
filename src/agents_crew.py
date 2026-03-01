import os
import logging
from crewai import Agent, Task, Crew, Process
from .rag.tools import SearchCatalogTool
from .llm_factory import LLMFactory
from .tools.shopify_tool import ShopifyCustomerActivityTool, ShopifyAbandonedCartTool
from .tools.communication_tool import SendWhatsAppTool, SendEmailTool

logger = logging.getLogger(__name__)

class ContentLabCrew:
    """
    CrewAI: Esquadrão responsável por criar os e-mails e criativos.
    Esse é o Nível 2 na Hierarquia do Hana Intel 2.0.
    """
    
    def __init__(self):
        # Utilizando a nova fábrica de modelos para flexibilidade de custo e inteligência
        # Opções: "openai", "deepseek", "gemini"
        self.llm = LLMFactory.get_llm(provider="openai")

    def _create_agents(self):
        # O Agente Especialista em Copywriting recebe a ferramenta de busca, Shopify e Comunicação
        search_catalog_tool = SearchCatalogTool()
        shopify_history_tool = ShopifyCustomerActivityTool()
        shopify_cart_tool = ShopifyAbandonedCartTool()
        whatsapp_tool = SendWhatsAppTool()
        email_tool = SendEmailTool()
        
        copywriter = Agent(
            role='Senior Copywriter Hana Beauty',
            goal='Escrever e-mails de alta conversão, persuasivos e com tom de voz premium para clientes reais.',
            backstory='Você é especialista na indústria de beleza e cosméticos, conhecendo a fundo os produtos da Hana Beauty. Use o Catálogo para preços e a Shopify para descobrir se o cliente tem perfil VIP (LTV alto) ou se você deve criar uma mensagem de recall de carrinho abandonado. Quando a tarefa exigir ação imediata, utilize as as ferramentas de WhatsApp ou E-mail para enviar suas criações aos clientes.',
            verbose=False,
            allow_delegation=False,
            llm=self.llm,
            tools=[search_catalog_tool, shopify_history_tool, shopify_cart_tool, whatsapp_tool, email_tool]
        )
        return [copywriter]

    def process_campaign(self, strategy_directive: str) -> str:
        """
        Gera conteúdo baseado em uma diretiva enviada pela Hana AI Core (Manager).
        """
        if not self.llm:
            return "Demostração: Conteúdo gerado baseado em: " + strategy_directive

        logger.info(f"🎨 [CrewAI] Iniciando redação para diretiva: {strategy_directive[:50]}...")
        
        agents = self._create_agents()
        
        redacao_task = Task(
            description=f'Escreva 1 e-mail focado na seguinte estratégia aprovada pela CEO: {strategy_directive}. O e-mail deve ter assunto e corpo formatado para envio direto.',
            expected_output='1 Assunto de Email matador e o Corpo do e-mail em formato HTML limpo pronto para envio.',
            agent=agents[0]
        )

        crew = Crew(
            agents=agents,
            tasks=[redacao_task],
            process=Process.sequential
        )

        try:
            result = crew.kickoff()
            return str(result)
        except Exception as e:
            logger.error(f"❌ [CrewAI] Falha na redação: {e}")
            return f"Erro na IA Criativa: {str(e)}"

class SocialMediaCrew:
    """
    CrewAI: Esquadrão responsável por interações rápidas em Redes Sociais.
    Focado em SAC, engajamento e respostas de comentários (Instagram, Facebook).
    """
    
    def __init__(self):
        self.llm = LLMFactory.get_llm(provider="openai")

    def _create_agents(self):
        # O Agente de Redes Sociais recebe a ferramenta de busca para tirar dúvidas técnicas
        search_catalog_tool = SearchCatalogTool()
        
        community_manager = Agent(
            role='Community Manager Especialista Hana Beauty',
            goal='Atender clientes de forma empática, solucionando dúvidas apenas com informações reais do catálogo da loja.',
            backstory=(
                'Você é a voz oficial da Hana Beauty no WhatsApp e Redes Sociais. '
                'Sua especialidade técnica é alongamento de unhas, fibra de vidro e cílios. '
                'REGRAS CRÍTICAS DE SEGURANÇA (OBRIGATÓRIO):\n'
                '1. NUNCA FORNEÇA PREÇOS OU DESCRIÇÃO DE PRODUTOS SEM ANTES USAR A SEARCH CATALOG TOOL.\n'
                '2. SE A FERRAMENTA INDICAR QUE O PRODUTO NÃO EXISTE, diga educadamente que não trabalhamos com esse item atualmente.\n'
                '3. NUNCA CITE, MENCIONE OU INVENTE nomes de marcas concorrentes (como Vólia, Piubella, etc.).\n'
                '4. NUNCA ofereça descontos, a menos que autorizado explicitamente na ferramenta.\n'
                'Você tem tom de voz acolhedor, empático (usando os termos "Amor", "Maravilhosa" com moderação elegante) e foco sutil em vendas seguras.'
            ),
            verbose=False,
            allow_delegation=False,
            llm=self.llm,
            tools=[search_catalog_tool] 
        )
        return [community_manager]

    def process_social_comment(self, social_context: dict) -> str:
        """
        Inicia o agente social para responder um comentário específico recebido via N8N.
        """
        agents = self._create_agents()
        community_manager = agents[0]
        
        plataforma = social_context.get("plataforma", "Rede Social")
        usuario = social_context.get("usuario", "Cliente")
        comentario = social_context.get("comentario", "")
        
        reply_task = Task(
            description=(
                f'O usuário "{usuario}" comentou no {plataforma} da Hana Beauty: "{comentario}".\n'
                'Analise o sentimento e a intenção (Dúvida, Reclamação, Elogio, Preço).\n'
                'REGRAS PARA DÚVIDA DE PRODUTO: Você É OBRIGADO a consultar o catálogo com a ferramenta. '
                'Se o produto não constar no catálogo, de forma alguma sugira concorrentes ou minta o preço.\n'
                'Formule uma resposta humana, curta e empática. Retorne apenas o texto exato da resposta que deve ser publicada.'
            ),
            expected_output='Um parágrafo curto com a resposta perfeita pronta para ser enviada, contendo apenas produtos validados no catálogo.',
            agent=community_manager
        )
        
        crew = Crew(
            agents=agents,
            tasks=[reply_task],
            process=Process.sequential,
            verbose=True
        )
        
        try:
            result = crew.kickoff()
            return str(result)
        except Exception as e:
            logger.error(f"❌ [CrewAI Social] Falha: {e}")
            return f"Olá {usuario}! Poderia nos chamar no direct para te ajudarmos melhor?"

# Instâncias Globais Seguras para o Celery
crew_content_lab = ContentLabCrew()
crew_social_media = SocialMediaCrew()
