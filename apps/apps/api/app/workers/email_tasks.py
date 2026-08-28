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
        msg["From"] = settings.FROM_EMAIL
        msg["To"] = to
        msg.attach(MIMEText(html_body, "html"))

        with smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT) as server:
            if settings.SMTP_USE_TLS:
                server.starttls()
            if settings.SMTP_USERNAME:
                server.login(settings.SMTP_USERNAME, settings.SMTP_PASSWORD)
            server.sendmail(settings.FROM_EMAIL, to, msg.as_string())

        logger.info("email_sent", to=to, subject=subject)
        return True
    except Exception as exc:
        logger.error("email_failed", to=to, error=str(exc))
        raise self.retry(exc=exc) from exc


@shared_task
def send_invitation_email(to: str, inviter_name: str, org_name: str, invite_url: str) -> None:
    html = f"""
    <h2>You've been invited to {org_name}</h2>
    <p>{inviter_name} has invited you to join {org_name} on SaaS Platform.</p>
    <a href="{invite_url}" style="background:#6d28d9;color:white;padding:12px 24px;
       border-radius:6px;text-decoration:none;">Accept Invitation</a>
    """
    send_email.delay(to, f"Join {org_name} on SaaS Platform", html)


@shared_task
def send_password_reset_email(to: str, reset_url: str) -> None:
    html = f"""
    <h2>Reset your password</h2>
    <p>Click the link below to choose a new password. This link expires in 1 hour.</p>
    <a href="{reset_url}" style="background:#6d28d9;color:white;padding:12px 24px;
       border-radius:6px;text-decoration:none;">Reset Password</a>
    <p>If you didn't request this, you can safely ignore this email.</p>
    """
    send_email.delay(to, "Reset your password", html)
