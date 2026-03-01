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
            role='Senior Copywriter & Content Creator Hana Beauty',
            goal='Criar conteúdos de alta conversão, persuasivos e com tom de voz premium para clientes reais e múltiplos canais de venda (E-mail, Blog, Instagram).',
            backstory='Você é especialista na indústria de beleza e cosméticos, conhecendo a fundo os produtos da Hana Beauty. Use o Catálogo para preços e a Shopify para histórico. Você redige desde e-mails em HTML até legendas de redes sociais e artigos engajadores de blog. Quando a tarefa exigir envio individual, utilize as ferramentas de WhatsApp ou E-mail para enviar suas criações aos clientes.',
            verbose=False,
            allow_delegation=False,
            llm=self.llm,
            tools=[search_catalog_tool, shopify_history_tool, shopify_cart_tool, whatsapp_tool, email_tool]
        )
        return [copywriter]

    def process_campaign(self, strategy_directive: str, content_type: str = "conteúdo geral") -> str:
        """
        Gera conteúdo baseado em uma diretiva enviada pela Hana AI Core (Manager).
        """
        if not self.llm:
            return f"Demostração: Conteúdo gerado ({content_type}) baseado em: " + strategy_directive

        logger.info(f"🎨 [CrewAI] Iniciando redação ({content_type}) para diretiva: {strategy_directive[:50]}...")
        
        agents = self._create_agents()
        
        redacao_task = Task(
            description=f'Escreva um(a) {content_type} focado na seguinte estratégia aprovada pela CEO: {strategy_directive}. O texto deve estar formatado para o canal específico (ex: HTML se for e-mail, markdown se for blog, hashtags e emojis se for rede social).',
            expected_output=f'O conteúdo final formatado adequadamente como um(a) {content_type}, polido, persuasivo e pronto para publicação ou envio.',
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
            role='Consultora Especialista Premium Hana Beauty',
            goal='Atuar como uma consultora premium, descobrindo a necessidade da cliente para recomendar produtos e soluções de alta performance para o seu salão, de forma consultiva e elegante.',
            backstory=(
                'Você é a Consultora Oficial da Hana Beauty no WhatsApp e Redes Sociais. '
                'Sua especialidade técnica é o mercado de beleza de alto padrão: alongamento de unhas, fibra de vidro e cílios. '
                'Seu cliente alvo são profissionais de alta performance, gerentes e proprietários de salão. '
                'Nossos produtos são desenvolvidos e fabricados no JAPÃO com extremo rigor de qualidade. '
                'Nós não vendemos "produtos baratos" e NUNCA abordamos os clientes pelo preço. Nós entregamos Qualidade, Segurança e Altíssimo Retorno Financeiro. '
                '(Exemplo: enquanto um adesivo comum da concorrência gera 3 a 5 mil reais em faturamento, os nossos adesivos japoneses passam facilmente dos 20 mil reais). '
                'Sua missão é sempre extrair a necessidade do cliente de forma consultiva e recomendar o produto Hana Beauty que trará a maior performance para ela. '
                'REGRAS CRÍTICAS DE SEGURANÇA (OBRIGATÓRIO):\n'
                '1. NUNCA FORNEÇA PREÇOS OU DESCRIÇÕES SEM ANTES CONSULTAR O CATÁLOGO (SEARCH CATALOG TOOL).\n'
                '2. USE O SITE hanabeauty.com.br COMO REFERÊNCIA MENTAL, MAS NUNCA BUSQUE SITES, MARCAS OU PRODUTOS EXTERNOS.\n'
                '3. SE O PRODUTO NÃO EXISTIR NO NOSSO CATÁLOGO, informe educadamente que não trabalhamos com ele. NUNCA invente ou sugira rivais.\n'
                '4. NUNCA ofereça descontos a menos que autorizado. Você não "empurra" produto, você atua em tom de consultoria.'
            ),
            verbose=False,
            allow_delegation=False,
            llm=self.llm,
            tools=[search_catalog_tool] 
        )
        return [community_manager]

    def process_social_comment(self, social_context: dict) -> str:
        """
        Inicia o agente social para responder um comentário específico recebido via N8N/Evolution.
        Agora suporta Memória Conversacional via string injetada.
        """
        agents = self._create_agents()
        community_manager = agents[0]
        
        plataforma = social_context.get("plataforma", "Rede Social")
        usuario = social_context.get("usuario", "Cliente")
        comentario = social_context.get("comentario", "")
        historico = social_context.get("historico", "")
        
        contexto_prompt = f'O usuário "{usuario}" está falando conosco via {plataforma}.\n\n'
        
        if historico:
            contexto_prompt += f'### HISTÓRICO RECENTE DA CONVERSA ###\n{historico}\n\n'
        
        contexto_prompt += (
            f'### NOVA MENSAGEM DO CLIENTE ###\n'
            f'"{comentario}"\n\n'
            'Sua Tarefa: Analise a nova mensagem MANTENDO o contexto do histórico acima (se existir).\n'
            '- Se o cliente disser "Quero um só" ou "159,00", olhe no histórico qual produto ele está se referindo e finalize a venda consultiva.\n'
            '- REGRAS PARA DÚVIDA DE PRODUTO: Você É OBRIGADO a consultar o catálogo com a ferramenta (Search Catalog Tool). '
            'Se o produto não constar no catálogo da ferramenta, não minta e não sugira concorrentes.\n'
            '- Formule uma resposta humana, curta e empática. Retorne APENAS o texto exato da sua resposta, sem introduções ou aspas.'
        )
        
        reply_task = Task(
            description=contexto_prompt,
            expected_output='Um parágrafo curto com a continuação perfeita da conversa pronta para envio, contendo produtos validados no catálogo e seguindo a persona premium.',
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
