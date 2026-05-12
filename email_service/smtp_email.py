import os
import smtplib
from email.message import EmailMessage


class SmtpEmailSender:
    """SMTP 邮件发送器，配置从环境变量读取。"""

    def __init__(
        self,
        host=None,
        port=None,
        username=None,
        password=None,
        from_email=None,
        use_ssl=None,
        timeout=10,
    ):
        self.host = host or os.getenv("ATM_SMTP_HOST")
        self.port = int(port or os.getenv("ATM_SMTP_PORT", "465"))
        self.username = username or os.getenv("ATM_SMTP_USER")
        self.password = password or os.getenv("ATM_SMTP_PASSWORD")
        self.from_email = from_email or os.getenv("ATM_SMTP_FROM") or self.username
        self.use_ssl = _env_bool("ATM_SMTP_SSL", True) if use_ssl is None else use_ssl
        self.timeout = timeout

    def send(self, to_email, subject, content):
        if not all([self.host, self.port, self.username, self.password, self.from_email]):
            return False

        message = EmailMessage()
        message["From"] = self.from_email
        message["To"] = to_email
        message["Subject"] = subject
        message.set_content(content)

        if self.use_ssl:
            with smtplib.SMTP_SSL(self.host, self.port, timeout=self.timeout) as smtp:
                smtp.login(self.username, self.password)
                smtp.send_message(message)
        else:
            with smtplib.SMTP(self.host, self.port, timeout=self.timeout) as smtp:
                smtp.starttls()
                smtp.login(self.username, self.password)
                smtp.send_message(message)
        return True


def send_email(to_email, subject, content, sender=None):
    """发送邮件；发送失败返回 False，不影响存取款主流程。"""
    if not to_email:
        return False
    email_sender = sender or SmtpEmailSender()
    try:
        return bool(email_sender.send(to_email, subject, content))
    except (OSError, smtplib.SMTPException):
        return False


def _env_bool(name, default):
    value = os.getenv(name)
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "on"}
