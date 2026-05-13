from __future__ import annotations

import argparse
import os
import smtplib
from email.message import EmailMessage


class SmtpEmailSender:
    """SMTP email sender configured by environment variables."""

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
        self.host = host or _get_env("ATM_SMTP_HOST")
        self.port_raw = str(port or _get_env("ATM_SMTP_PORT", "465")).strip()
        self.port = _parse_port(self.port_raw)
        self.username = username or _get_env("ATM_SMTP_USER")
        self.password = password or _get_env("ATM_SMTP_PASSWORD")
        self.from_email = from_email or _get_env("ATM_SMTP_FROM") or self.username
        self.use_ssl = _env_bool("ATM_SMTP_SSL", True) if use_ssl is None else use_ssl
        self.timeout = timeout

    def missing_config(self):
        missing = []
        if not self.host:
            missing.append("ATM_SMTP_HOST")
        if self.port is None:
            missing.append("ATM_SMTP_PORT")
        if not self.username:
            missing.append("ATM_SMTP_USER")
        if not self.password:
            missing.append("ATM_SMTP_PASSWORD")
        if not self.from_email:
            missing.append("ATM_SMTP_FROM")
        return missing

    def is_configured(self):
        return not self.missing_config()

    def send(self, to_email, subject, content):
        if not to_email or not self.is_configured():
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


def get_smtp_config_status(sender=None):
    email_sender = sender or SmtpEmailSender()
    missing = email_sender.missing_config()
    return {
        "configured": not missing,
        "missing": missing,
        "host": email_sender.host,
        "port": email_sender.port,
        "username": email_sender.username,
        "from_email": email_sender.from_email,
        "use_ssl": email_sender.use_ssl,
    }


def send_email(to_email, subject, content, sender=None):
    """Send email by SMTP. Return False on configuration or delivery failure."""
    if not to_email:
        return False
    try:
        email_sender = sender or SmtpEmailSender()
        return bool(email_sender.send(to_email, subject, content))
    except Exception:
        return False


def send_test_email(to_email, sender=None):
    subject = "Bank ATM SMTP Test"
    content = (
        "This is a Bank ATM SMTP test email.\n"
        "If you receive this message, SMTP notification is configured correctly."
    )
    return send_email(to_email, subject, content, sender=sender)


def _parse_port(value):
    try:
        port = int(value)
    except (TypeError, ValueError):
        return None
    if port <= 0 or port > 65535:
        return None
    return port


def _env_bool(name, default):
    value = _get_env(name)
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "on"}


def _get_env(name, default=None):
    value = os.getenv(name)
    if value is not None:
        return value
    if os.name == "nt":
        try:
            import winreg

            with winreg.OpenKey(winreg.HKEY_CURRENT_USER, "Environment") as key:
                value, _ = winreg.QueryValueEx(key, name)
                return value
        except OSError:
            pass
    return default


def main(argv=None):
    parser = argparse.ArgumentParser(description="Bank ATM SMTP checker")
    parser.add_argument("--check", action="store_true", help="show SMTP config status")
    parser.add_argument("--to", help="recipient address for a real test email")
    args = parser.parse_args(argv)

    status = get_smtp_config_status()
    if args.check or not args.to:
        print("SMTP configured:", status["configured"])
        print("Missing:", ", ".join(status["missing"]) if status["missing"] else "None")
        print("Host:", status["host"])
        print("Port:", status["port"])
        print("User:", status["username"])
        print("From:", status["from_email"])
        print("SSL:", status["use_ssl"])
        if not args.to:
            return 0 if status["configured"] else 1

    ok = send_test_email(args.to)
    print("SMTP test email:", "sent" if ok else "failed")
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
