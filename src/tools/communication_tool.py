from pydantic import BaseModel, Field
from crewai.tools import BaseTool
from typing import Type
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import requests
import logging
import os

logger = logging.getLogger(__name__)

# --- Inputs ---

class SendWhatsAppInput(BaseModel):
    phone_number: str = Field(..., description="Número de telefone no formato internacional (Ex: 5511999999999)")
    message: str = Field(..., description="Mensagem de texto a ser enviada pelo WhatsApp. Suporta formatação *negrito* e _itálico_.")
    instance_name: str = Field(default="HanaBot", description="Nome da instância na Evolution API. Ex: HanaBot")

class SendEmailInput(BaseModel):
    to_email: str = Field(..., description="Endereço de e-mail do destinatário. Ex: cliente@email.com")
    subject: str = Field(..., description="Assunto do E-mail persuasivo criado.")
    body_html: str = Field(..., description="Corpo do e-mail em formato HTML.")

# --- Ferramentas (Tools) ---

class SendWhatsAppTool(BaseTool):
    name: str = "Enviar Mensagem pelo WhatsApp (Evolution API)"
    description: str = (
        "Utilize esta ferramenta para enviar uma mensagem ativa pelo WhatsApp (Hana Intel) "
        "para uma cliente. Útil para recuperar carrinhos ou enviar códigos de desconto VIP."
    )
    args_schema: Type[BaseModel] = SendWhatsAppInput

    def _run(self, phone_number: str, message: str, instance_name: str = "HanaBot") -> str:
        api_url = os.getenv("EVOLUTION_API_URL")
        api_token = os.getenv("EVOLUTION_API_TOKEN")
        
        if not api_url or not api_token:
            logger.warning("Faltam credenciais da Evolution API. Mocking WhatsApp Send.")
            return f"Mock: Mensagem de WhatsApp enviada com sucesso para o número {phone_number}."

        endpoint = f"{api_url}/message/sendText/{instance_name}"
        headers = {
            "Content-Type": "application/json",
            "apikey": api_token
        }
        payload = {
            "number": phone_number,
            "options": {
                "delay": 1200,
                "presence": "composing"
            },
            "textMessage": {
                "text": message
            }
        }
        
        try:
            response = requests.post(endpoint, headers=headers, json=payload)
            response.raise_for_status()
            logger.info(f"✅ WhatsApp enviado para {phone_number} com sucesso.")
            return f"Mensagem enviada com sucesso para {phone_number} via Módulo Evolution API."
        except Exception as e:
            logger.error(f"Erro ao disparar WhatsApp: {str(e)}")
            return f"Falha ao enviar mensagem de WhatsApp. Erro: {str(e)}"

class SendEmailTool(BaseTool):
    name: str = "Módulo de Disparo de E-mail (SMTP)"
    description: str = (
        "Ferramenta responsável por enviar o prospecto final de um e-mail escrito pelo Agente "
        "diretamente para a caixa de entrada da cliente final."
    )
    args_schema: Type[BaseModel] = SendEmailInput

    def _run(self, to_email: str, subject: str, body_html: str) -> str:
        smtp_host = os.getenv("SMTP_HOST")
        smtp_port = os.getenv("SMTP_PORT")
        smtp_user = os.getenv("SMTP_USER")
        smtp_pass = os.getenv("SMTP_PASS")
        
        if not all([smtp_host, smtp_port, smtp_user, smtp_pass]):
            logger.warning("Credenciais de SMTP ausentes. Mocking Email Send.")
            return f"Mock: E-mail com o assunto '{subject}' enviado para {to_email} simulado com sucesso."

        try:
            msg = MIMEMultipart("alternative")
            msg['Subject'] = subject
            msg['From'] = f"Hana Beauty <{smtp_user}>"
            msg['To'] = to_email

            # Anexando o corpo em modo HTML
            html_part = MIMEText(body_html, 'html')
            msg.attach(html_part)

            with smtplib.SMTP(smtp_host, int(smtp_port)) as server:
                server.starttls()
                server.login(smtp_user, smtp_pass)
                server.sendmail(smtp_user, to_email, msg.as_string())
                
            logger.info(f"📧 E-mail {subject} enviado com sucesso para {to_email}.")
            return f"E-mail disparado para {to_email} via SMTP Mestre."

        except Exception as e:
            logger.error(f"Falha de SMTP ao enviar e-mail: {str(e)}")
            return f"Ocorreu um erro no servidor de SMTP ao enviar o e-mail: {str(e)}"
