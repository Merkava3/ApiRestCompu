"""
Servicio de envío de correos electrónicos.
Implementa el patrón Service para desacoplar la lógica de envío de los controladores.
"""
import smtplib
import os
import logging
from email.message import EmailMessage
from typing import Optional

logger = logging.getLogger(__name__)

class MailerService:
    """
    Servicio encargado de la comunicación con el servidor SMTP.
    """

    def __init__(self):
        self.smtp_server = "smtp.mail.yahoo.com"
        self.smtp_port = 587
        self.email_user = os.getenv('YAHOO_EMAIL')
        self.email_pass = os.getenv('YAHOO_PASSWORD')

    def send_email(self, subject: str, body: str, to: str) -> bool:
        """
        Envía un correo electrónico de forma síncrona.
        
        Returns:
            bool: True si el envío fue exitoso, False en caso contrario.
        """
        if not self.email_user or not self.email_pass:
            logger.error("Credenciales de correo no configuradas en el entorno.")
            return False

        msg = EmailMessage()
        msg.set_content(body)
        msg['Subject'] = subject
        msg['From'] = self.email_user
        msg['To'] = to

        try:
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                server.login(self.email_user, self.email_pass)
                server.send_message(msg)
                logger.info(f"Correo enviado exitosamente a {to}")
                return True
        except smtplib.SMTPException as e:
            logger.error(f"Error SMTP al enviar correo a {to}: {str(e)}")
            return False
        except Exception as e:
            logger.error(f"Error inesperado al enviar correo: {str(e)}")
            return False

# Instancia global para ser utilizada en la aplicación
mailer = MailerService()