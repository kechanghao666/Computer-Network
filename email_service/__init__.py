"""Email service package."""

__all__ = [
    "SmtpEmailSender",
    "get_smtp_config_status",
    "send_email",
    "send_test_email",
]


def __getattr__(name):
    if name in __all__:
        from . import smtp_email

        return getattr(smtp_email, name)
    raise AttributeError(name)
