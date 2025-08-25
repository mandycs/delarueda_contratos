import asyncio
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email.mime.application import MIMEApplication
from email import encoders
import aiosmtplib
from jinja2 import Environment, BaseLoader
import os
from typing import Optional, List
import logging

from ..config import settings

logger = logging.getLogger(__name__)

class TemplateLoader(BaseLoader):
    """Custom template loader for Jinja2"""
    
    def __init__(self, templates_dir: str):
        self.templates_dir = templates_dir
    
    def get_source(self, environment, template):
        path = os.path.join(self.templates_dir, template)
        if not os.path.exists(path):
            raise FileNotFoundError(f"Template {template} not found")
        
        with open(path, 'r', encoding='utf-8') as f:
            source = f.read()
        
        return source, path, lambda: True

# Initialize Jinja2 environment
templates_dir = os.path.join(os.path.dirname(__file__), '..', 'templates')
jinja_env = Environment(loader=TemplateLoader(templates_dir))

class EmailService:
    def __init__(self):
        self.smtp_server = settings.SMTP_SERVER
        self.smtp_port = settings.SMTP_PORT
        self.username = settings.SMTP_USERNAME
        self.password = settings.SMTP_PASSWORD
        self.use_tls = getattr(settings, 'SMTP_USE_TLS', True)
        self.use_ssl = getattr(settings, 'SMTP_USE_SSL', False)
        self.from_email = settings.SMTP_FROM_EMAIL
        self.from_name = settings.SMTP_FROM_NAME

    async def send_email(
        self,
        to_email: str,
        subject: str,
        html_content: str,
        text_content: Optional[str] = None,
        attachments: Optional[List[dict]] = None
    ) -> bool:
        """
        Send an email with HTML content and optional attachments
        
        Args:
            to_email: Recipient email address
            subject: Email subject
            html_content: HTML content of the email
            text_content: Plain text content (optional)
            attachments: List of attachments [{'path': str, 'filename': str}]
        
        Returns:
            bool: True if email was sent successfully
        """
        try:
            # Create message - use mixed for attachments, not alternative
            if attachments:
                message = MIMEMultipart("mixed")
                # Create alternative part for text/html content
                content_part = MIMEMultipart("alternative")
            else:
                message = MIMEMultipart("alternative")
            message["Subject"] = subject
            message["From"] = f"{self.from_name} <{self.from_email}>"
            message["To"] = to_email

            # Add text content if provided
            if text_content:
                text_part = MIMEText(text_content, "plain", "utf-8")
                if attachments:
                    content_part.attach(text_part)
                else:
                    message.attach(text_part)

            # Add HTML content
            html_part = MIMEText(html_content, "html", "utf-8")
            if attachments:
                content_part.attach(html_part)
                message.attach(content_part)
            else:
                message.attach(html_part)

            # Add attachments if provided
            if attachments:
                logger.info(f"Processing {len(attachments)} attachments")
                for i, attachment in enumerate(attachments):
                    logger.info(f"Attachment {i+1}: {attachment['path']} -> {attachment['filename']}")
                    if os.path.exists(attachment['path']):
                        file_size = os.path.getsize(attachment['path'])
                        logger.info(f"Attachment {i+1} exists, size: {file_size} bytes")
                        with open(attachment['path'], "rb") as f:
                            # Use MIMEApplication for better PDF handling
                            part = MIMEApplication(
                                f.read(),
                                _subtype='pdf',
                                name=attachment["filename"]
                            )
                            part.add_header(
                                'Content-Disposition',
                                f'attachment; filename="{attachment["filename"]}"'
                            )
                            message.attach(part)
                        logger.info(f"Attachment {i+1} added to email successfully")
                    else:
                        logger.error(f"Attachment file not found: {attachment['path']}")

            # Send email using aiosmtplib
            if self.use_ssl:
                await aiosmtplib.send(
                    message,
                    hostname=self.smtp_server,
                    port=self.smtp_port,
                    use_tls=True,   # For SSL on port 465, use_tls=True works
                    username=self.username,
                    password=self.password,
                )
            else:
                await aiosmtplib.send(
                    message,
                    hostname=self.smtp_server,
                    port=self.smtp_port,
                    start_tls=self.use_tls,
                    username=self.username,
                    password=self.password,
                )
            
            logger.info(f"Email sent successfully to {to_email}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to send email to {to_email}: {str(e)}")
            return False

    def render_template(self, template_name: str, **kwargs) -> str:
        """
        Render a Jinja2 template with the provided context
        
        Args:
            template_name: Name of the template file
            **kwargs: Template context variables
        
        Returns:
            str: Rendered template content
        """
        try:
            template = jinja_env.get_template(template_name)
            return template.render(**kwargs)
        except Exception as e:
            logger.error(f"Failed to render template {template_name}: {str(e)}")
            raise

    async def send_contract_invitation(
        self, 
        to_email: str, 
        client_name: str, 
        contract_id: int,
        titulo_diseno: Optional[str] = None
    ) -> bool:
        """
        Send contract signing invitation email
        
        Args:
            to_email: Client email address
            client_name: Client name
            contract_id: Contract ID
            titulo_diseno: Design title (optional)
        
        Returns:
            bool: True if email was sent successfully
        """
        try:
            signing_url = f"{settings.FRONTEND_URL}/sign/{contract_id}"
            
            html_content = self.render_template(
                'contract_invitation.html',
                client_name=client_name,
                contract_id=contract_id,
                titulo_diseno=titulo_diseno or f"Contrato #{contract_id}",
                signing_url=signing_url,
                company_name="De La Rueda"
            )
            
            subject = f"Contrato de Diseño para Firmar - {titulo_diseno or f'#{contract_id}'}"
            
            # Enviar email al cliente
            client_success = await self.send_email(
                to_email=to_email,
                subject=subject,
                html_content=html_content
            )
            
            # Enviar notificación al administrador
            if client_success:
                await self.send_admin_notification(
                    action="invitation_sent",
                    client_email=to_email,
                    client_name=client_name,
                    contract_id=contract_id,
                    titulo_diseno=titulo_diseno
                )
            
            return client_success
            
        except Exception as e:
            logger.error(f"Failed to send contract invitation to {to_email}: {str(e)}")
            return False

    async def send_contract_signed_confirmation(
        self,
        to_email: str,
        client_name: str,
        contract_id: int,
        signed_pdf_path: Optional[str] = None,
        titulo_diseno: Optional[str] = None
    ) -> bool:
        """
        Send contract signed confirmation email with PDF attachment
        
        Args:
            to_email: Client email address
            client_name: Client name
            contract_id: Contract ID
            signed_pdf_path: Path to signed PDF file
            titulo_diseno: Design title (optional)
        
        Returns:
            bool: True if email was sent successfully
        """
        try:
            html_content = self.render_template(
                'contract_signed.html',
                client_name=client_name,
                contract_id=contract_id,
                titulo_diseno=titulo_diseno or f"Contrato #{contract_id}",
                company_name="De La Rueda"
            )
            
            subject = f"Contrato Firmado - {titulo_diseno or f'#{contract_id}'}"
            
            attachments = []
            if signed_pdf_path:
                logger.info(f"Original signed_pdf_path: {signed_pdf_path}")
                logger.info(f"Current working directory: {os.getcwd()}")
                
                # Convert to absolute path if relative
                if not os.path.isabs(signed_pdf_path):
                    full_path = os.path.abspath(signed_pdf_path)
                    logger.info(f"Converted relative to absolute: {signed_pdf_path} -> {full_path}")
                else:
                    full_path = signed_pdf_path
                    logger.info(f"Path already absolute: {full_path}")
                    
                logger.info(f"Checking PDF file for attachment: {full_path}")
                
                if os.path.exists(full_path):
                    file_size = os.path.getsize(full_path)
                    logger.info(f"PDF file found, size: {file_size} bytes")
                    attachments.append({
                        'path': full_path,
                        'filename': f'contrato_{contract_id}_firmado.pdf'
                    })
                else:
                    logger.error(f"PDF file not found for attachment: {full_path}")
            else:
                logger.warning(f"No signed_pdf_path provided for contract {contract_id}")
            
            # Enviar confirmación al cliente
            logger.info(f"Sending email to client with {len(attachments)} attachments")
            client_success = await self.send_email(
                to_email=to_email,
                subject=subject,
                html_content=html_content,
                attachments=attachments if attachments else None
            )
            
            # Enviar notificación al administrador
            if client_success:
                await self.send_admin_notification(
                    action="contract_signed",
                    client_email=to_email,
                    client_name=client_name,
                    contract_id=contract_id,
                    titulo_diseno=titulo_diseno,
                    signed_pdf_path=signed_pdf_path
                )
            
            return client_success
            
        except Exception as e:
            logger.error(f"Failed to send contract signed confirmation to {to_email}: {str(e)}")
            return False

    async def send_admin_notification(
        self,
        action: str,
        client_email: str,
        client_name: str,
        contract_id: int,
        titulo_diseno: Optional[str] = None,
        signed_pdf_path: Optional[str] = None
    ) -> bool:
        """
        Send notification to administrator about contract actions
        
        Args:
            action: Type of action ("invitation_sent" or "contract_signed")
            client_email: Client email address
            client_name: Client name
            contract_id: Contract ID
            titulo_diseno: Design title (optional)
            signed_pdf_path: Path to signed PDF (for contract_signed action)
        
        Returns:
            bool: True if notification was sent successfully
        """
        try:
            admin_email = settings.ADMIN_EMAIL  # Email del administrador desde variables de entorno
            
            if action == "invitation_sent":
                subject = f"[Sistema] Invitación enviada - Contrato #{contract_id}"
                template_name = "admin_invitation_sent.html"
            elif action == "contract_signed":
                subject = f"[Sistema] Contrato firmado - #{contract_id}"
                template_name = "admin_contract_signed.html"
            else:
                logger.warning(f"Unknown admin notification action: {action}")
                return False
            
            html_content = self.render_template(
                template_name,
                client_name=client_name,
                client_email=client_email,
                contract_id=contract_id,
                titulo_diseno=titulo_diseno or f"Contrato #{contract_id}",
                company_name="De La Rueda"
            )
            
            # Para contratos firmados, adjuntar el PDF
            attachments = []
            if action == "contract_signed" and signed_pdf_path:
                # Convert to absolute path if relative
                if not os.path.isabs(signed_pdf_path):
                    full_path = os.path.abspath(signed_pdf_path)
                else:
                    full_path = signed_pdf_path
                    
                logger.info(f"Admin notification: Original path: {signed_pdf_path}")
                logger.info(f"Admin notification: checking PDF file {full_path}")
                
                if os.path.exists(full_path):
                    file_size = os.path.getsize(full_path)
                    logger.info(f"Admin notification: PDF found, size {file_size} bytes")
                    attachments.append({
                        'path': full_path,
                        'filename': f'contrato_{contract_id}_firmado.pdf'
                    })
                else:
                    logger.error(f"PDF file not found for admin notification: {full_path}")
            
            logger.info(f"Sending admin notification with {len(attachments)} attachments")
            return await self.send_email(
                to_email=admin_email,
                subject=subject,
                html_content=html_content,
                attachments=attachments if attachments else None
            )
            
        except Exception as e:
            logger.error(f"Failed to send admin notification for {action}: {str(e)}")
            return False

# Global email service instance
email_service = EmailService()