"""Email sending. Without SMTP settings, emails are logged (and the UI says email is not configured)."""
import logging
import smtplib
from email.message import EmailMessage

from flask import current_app

log = logging.getLogger("formsaathi.mail")


def is_configured() -> bool:
    return bool(current_app.config.get("SMTP_HOST"))


def send(to: str, subject: str, text: str) -> bool:
    cfg = current_app.config
    if not is_configured():
        log.info("[email not configured] would send %r to recipient #%s", subject, hash(to) % 10_000)
        if current_app.debug:
            log.info("Email body:\n%s", text)
        return False
    msg = EmailMessage()
    msg["From"], msg["To"], msg["Subject"] = cfg["MAIL_FROM"], to, subject
    msg.set_content(text + "\n\n— FormSaathi\nYou can change email preferences in Settings.")
    try:
        with smtplib.SMTP(cfg["SMTP_HOST"], cfg["SMTP_PORT"], timeout=15) as smtp:
            if cfg["SMTP_USE_TLS"]:
                smtp.starttls()
            if cfg["SMTP_USERNAME"]:
                smtp.login(cfg["SMTP_USERNAME"], cfg["SMTP_PASSWORD"])
            smtp.send_message(msg)
        return True
    except (smtplib.SMTPException, OSError) as e:
        log.error("Email send failed: %s", e)
        return False
