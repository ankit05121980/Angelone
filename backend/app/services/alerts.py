import smtplib
from email.message import EmailMessage

import httpx
from loguru import logger

from app.config.settings import Settings


class AlertService:
    def __init__(self, settings: Settings):
        self.settings = settings

    async def trade_alert(self, message: str) -> None:
        await self._telegram(message)
        self._email("Trade alert", message)

    async def daily_report(self, message: str) -> None:
        await self._telegram(message)
        self._email("Daily PnL report", message)

    async def _telegram(self, message: str) -> None:
        if not self.settings.telegram_bot_token or not self.settings.telegram_chat_id:
            return
        url = f"https://api.telegram.org/bot{self.settings.telegram_bot_token.get_secret_value()}/sendMessage"
        try:
            async with httpx.AsyncClient(timeout=10) as client:
                await client.post(url, json={"chat_id": self.settings.telegram_chat_id, "text": message})
        except Exception as exc:
            logger.warning("Telegram alert failed: {}", exc)

    def _email(self, subject: str, body: str) -> None:
        if not all([self.settings.smtp_host, self.settings.smtp_username, self.settings.smtp_password, self.settings.alert_from_email, self.settings.alert_to_email]):
            return
        email = EmailMessage()
        email["Subject"] = subject
        email["From"] = self.settings.alert_from_email
        email["To"] = self.settings.alert_to_email
        email.set_content(body)
        try:
            with smtplib.SMTP(self.settings.smtp_host, self.settings.smtp_port) as smtp:
                smtp.starttls()
                smtp.login(self.settings.smtp_username, self.settings.smtp_password.get_secret_value())
                smtp.send_message(email)
        except Exception as exc:
            logger.warning("Email alert failed: {}", exc)
