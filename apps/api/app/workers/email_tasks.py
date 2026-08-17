"""Email delivery Celery tasks."""
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

import structlog
from celery import shared_task

from app.config import settings

logger = structlog.get_logger()


@shared_task(bind=True, max_retries=3, default_retry_delay=60)
def send_email(self, to: str, subject: str, html_body: str) -> bool:
    try:
        msg = MIMEMultipart("alternative")
        msg["Subject"] = subject
        msg["From"] = settings.SMTP_FROM
        msg["To"] = to
        msg.attach(MIMEText(html_body, "html"))

        with smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT) as server:
            if settings.SMTP_TLS:
                server.starttls()
            if settings.SMTP_USER:
                server.login(settings.SMTP_USER, settings.SMTP_PASSWORD)
            server.sendmail(settings.SMTP_FROM, to, msg.as_string())

        logger.info("email_sent", to=to, subject=subject)
        return True
    except Exception as exc:
        logger.error("email_failed", to=to, error=str(exc))
        raise self.retry(exc=exc)


@shared_task
def send_invitation_email(to: str, inviter_name: str, org_name: str, invite_url: str) -> None:
    html = f"""
    <h2>You've been invited to {org_name}</h2>
    <p>{inviter_name} has invited you to join {org_name} on SaaS Platform.</p>
    <a href="{invite_url}" style="background:#6d28d9;color:white;padding:12px 24px;
       border-radius:6px;text-decoration:none;">Accept Invitation</a>
    """
    send_email.delay(to, f"Join {org_name} on SaaS Platform", html)
