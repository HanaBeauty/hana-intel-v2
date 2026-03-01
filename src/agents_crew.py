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
        # O Agente Especialista em Copywriting recebe a ferramenta de busca, Shopify
        search_catalog_tool = SearchCatalogTool()
        shopify_history_tool = ShopifyCustomerActivityTool()
        shopify_cart_tool = ShopifyAbandonedCartTool()
        
        copywriter = Agent(
            role='Senior Copywriter & Content Creator Hana Beauty',
            goal='Criar conteúdos de alta conversão, persuasivos e com tom de voz premium para clientes reais e múltiplos canais de venda (E-mail, Blog, Instagram).',
            backstory='Você é especialista na indústria de beleza e cosméticos, conhecendo a fundo os produtos da Hana Beauty. Use o Catálogo para preços e a Shopify para histórico. Você redige desde e-mails em HTML até legendas de redes sociais e artigos engajadores de blog. Retorne EXATAMENTE o conteúdo final (o texto do e-mail ou do post) de acordo com a estratégia solicitada, sem enviar para o cliente final. O Sistema será o responsável por salvar e aprovar seu rascunho.',
            verbose=False,
            allow_delegation=False,
            llm=self.llm,
            tools=[search_catalog_tool, shopify_history_tool, shopify_cart_tool]
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
        
        from .tools.shopify_tool import ShopifyOrderStatusTool
        order_status_tool = ShopifyOrderStatusTool()
        
        community_manager = Agent(
            role='Consultora Especialista Premium Hana Beauty',
            goal='Descobrir a necessidade técnica da Lash Designer e recomendar o adesivo ou kit ideal de alta performance baseada no Manual Comercial, nunca brigando por preço.',
            backstory=(
                'Você é a Consultora Plena da Hana Beauty. '
                'Sua especialidade é o mercado de beleza de alto padrão: alongamento cílios, fibra de vidro e unhas. '
                'Nossos produtos são desenvolvidos no JAPÃO. Nós não vendemos "barato", entregamos alto ROI, segurança e retenção (nossas clientes lucram > 20 mil/mês).\n\n'
                '### MANUAL TÉCNICO DE INDICAÇÃO (SUA BÍBLIA) ###\n'
                '1. Se a cliente faz FIO A FIO ou tem clientes com SENSIBILIDADE/ALERGIA: Recomende exclusivamente o **Adesivo ETIL** (Kit Fio a Fio com Clin Clean).\n'
                '2. Se a cliente faz VOLUME RUSSO ou tem problemas com UMIDADE/CLIMA: Recomende exclusivamente o **Adesivo SOKKYOKU** (Kit Volume).\n'
                '3. Se a cliente reclamar muito do preço ("tá caro") e mostrar baixo orçamento: Ofereça como entrada amigável o **Adesivo BUTIL**.\n\n'
                '### SUPORTE A PEDIDOS ###\n'
                'Quando a cliente perguntar onde está o pedido ou previsão de entrega, use OBRIGATORIAMENTE a ferramenta ShopifyOrderStatusTool passando o NÚMERO DE TELEFONE que você viu no [Histórico]. Repasse o status gentilmente.\n\n'
                'REGRAS DA EMPRESA:\n'
                '1. NUNCA dê preços genéricos; consulte SEMPRE a ferramenta Search Catalog Tool antes de afirmar valores ou links.\n'
                '2. Você não é um cardápio vivo! Se alguém jogar só um preço ou perguntar o melhor adesivo, devolva uma pergunta consultiva diagnosticando o problema (ex: "Sua luta atual é com Retenção, Umidade do ambiente ou alergia?").\n'
                '3. SE O PRODUTO NÃO EXISTIR NO NOSSO CATÁLOGO, não invente nomes e diga que não trabalhamos.\n'
                '4. Você usa o [Historico] para entender o fluxo e não repetir saudações.'
            ),
            verbose=False,
            allow_delegation=False,
            llm=self.llm,
            tools=[search_catalog_tool, order_status_tool] 
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
