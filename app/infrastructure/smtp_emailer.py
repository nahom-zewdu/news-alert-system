# app/infrastructure/smtp_emailer.py
"""
SMTP emailer implementation.

Synchronous, simple wrapper using smtplib to send plain-text emails. Intended for demo.
"""

import smtplib
from email.message import EmailMessage
import logging
from typing import Optional

from app.domain.interfaces import EmailerInterface

logger = logging.getLogger(__name__)


class SMTPEmailer(EmailerInterface):
    """
    SMTP-based email sender.
    Uses TLS and login authentication.
    """

    def __init__(self, host: str, port: int, user: str, password: str, default_from: Optional[str] = None):
        self.host = host
        self.port = port
        self.user = user
        self.password = password
        self.default_from = default_from

    def send(self, to: str, subject: str, body: str) -> None:
        """
        Send a plain-text email. Raises smtplib.SMTPException on failure.
        """
        msg = EmailMessage()
        msg["Subject"] = subject
        msg["From"] = self.default_from or self.user
        msg["To"] = to
        msg.set_content(body)

        logger.info("SMTPEmailer sending to=%s via %s:%s", to, self.host, self.port)
        with smtplib.SMTP(self.host, self.port, timeout=20) as server:
            server.ehlo()
            server.starttls()
            server.ehlo()
            server.login(self.user, self.password)
            server.send_message(msg)
        logger.info("Email sent to %s", to)
