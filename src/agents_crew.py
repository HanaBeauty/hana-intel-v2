import os
import logging
from langchain_openai import ChatOpenAI
from crewai import Agent, Task, Crew, Process
from .rag.tools import SearchCatalogTool

logger = logging.getLogger(__name__)

class ContentLabCrew:
    """
    CrewAI: Esquadrão responsável por criar os e-mails e criativos.
    Esse é o Nível 2 na Hierarquia do Hana Intel 2.0.
    """
    
    def __init__(self):
        self.api_key = os.getenv("OPENAI_API_KEY")
        if self.api_key:
            # Modelo criativo (O-mini ou GPT-4o) para redação final
            self.llm = ChatOpenAI(model="gpt-4o-mini", api_key=self.api_key, temperature=0.7)
        else:
            self.llm = None

    def _create_agents(self):
        # O Agente Especialista em Copywriting recebe a ferramenta de busca
        search_tool = SearchCatalogTool()
        
        copywriter = Agent(
            role='Senior Copywriter Hana Beauty',
            goal='Escrever e-mails de alta conversão, persuasivos e com tom de voz premium para clientes reais.',
            backstory='Você é especialista na indústria de beleza e cosméticos, conhecendo a fundo os produtos da Hana Beauty (pincéis, alongamento de unhas). Seu foco é gerar vendas mantendo a postura de luxo e autoridade técnica. Use a ferramenta de Busca no Catálogo SEMPRE que precisar mencionar produtos reais.',
            verbose=False,
            allow_delegation=False,
            llm=self.llm,
            tools=[search_tool]
        )
        return [copywriter]

    def process_campaign(self, strategy_directive: str) -> str:
        """
        Gera conteúdo baseado em uma diretiva enviada pela Hana AI Core (Manager).
        """
        if not self.llm:
            return "Demostração: Conteúdo gerado baseado em: " + strategy_directive

        logger.info(f"🎨 [CrewAI] Iniciando redação para diretiva: {strategy_directive[:50]}...")
        
        agents = self.create_agents()
        
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

crew_content_lab = ContentLabCrew()
