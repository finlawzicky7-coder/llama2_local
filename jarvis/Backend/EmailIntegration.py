"""EmailIntegration — IMAP + SMTP helper used by Main.py.

The original zip referenced Backend.EmailIntegration but did not ship it.
This module restores the interface Main.py expects (check_emails,
summarize_emails, send_email) using nothing but the Python standard library.

Configuration is loaded from the project's .env. Required keys:

    EmailAddress=<imap/smtp username, usually your email>
    EmailPassword=<app password>
    ImapHost=imap.gmail.com
    ImapPort=993
    SmtpHost=smtp.gmail.com
    SmtpPort=587

Any missing key produces a friendly error string instead of a crash, which
keeps the rest of the assistant responsive.
"""
from __future__ import annotations

import email
import imaplib
import os
import smtplib
import ssl
from email.header import decode_header
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from typing import List, Dict, Union

from dotenv import dotenv_values


def _env() -> Dict[str, str]:
    here = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    return {k: (v or '') for k, v in dotenv_values(os.path.join(here, '.env')).items()}


def _decode(value) -> str:
    if value is None:
        return ''
    if isinstance(value, bytes):
        try:
            return value.decode('utf-8', errors='replace')
        except Exception:
            return value.decode('latin-1', errors='replace')
    parts = decode_header(value)
    out = []
    for text, charset in parts:
        if isinstance(text, bytes):
            out.append(text.decode(charset or 'utf-8', errors='replace'))
        else:
            out.append(text)
    return ''.join(out)


class EmailClient:
    """Stateless wrapper for IMAP read + SMTP send.

    All public methods either return a string (the answer that Jarvis will
    speak/show) or, in the case of check_emails, a list of message dicts.
    Configuration problems return a single human-readable string so the
    assistant can read them out loud without crashing.
    """

    def __init__(self) -> None:
        env = _env()
        self.email_address = env.get('EmailAddress', '')
        self.email_password = env.get('EmailPassword', '')
        self.imap_host = env.get('ImapHost', 'imap.gmail.com')
        self.imap_port = int(env.get('ImapPort') or '993')
        self.smtp_host = env.get('SmtpHost', 'smtp.gmail.com')
        self.smtp_port = int(env.get('SmtpPort') or '587')

    def _missing_creds(self) -> Union[str, None]:
        if not self.email_address or not self.email_password:
            return (
                'Email is not configured. Add EmailAddress and EmailPassword '
                '(an app password, not your account password) to your .env file '
                'to enable email features.'
            )
        return None

    # ------------------------------------------------------------------
    # IMAP
    # ------------------------------------------------------------------
    def check_emails(self, limit: int = 5) -> Union[List[Dict[str, str]], str]:
        err = self._missing_creds()
        if err:
            return err
        try:
            with imaplib.IMAP4_SSL(self.imap_host, self.imap_port) as imap:
                imap.login(self.email_address, self.email_password)
                imap.select('INBOX')
                typ, data = imap.search(None, 'ALL')
                if typ != 'OK' or not data or not data[0]:
                    return []
                ids = data[0].split()[-limit:][::-1]
                results: List[Dict[str, str]] = []
                for msg_id in ids:
                    typ, msg_data = imap.fetch(msg_id, '(RFC822)')
                    if typ != 'OK' or not msg_data or not msg_data[0]:
                        continue
                    raw = msg_data[0][1]
                    msg = email.message_from_bytes(raw)
                    results.append({
                        'sender': _decode(msg.get('From')),
                        'subject': _decode(msg.get('Subject')) or '(no subject)',
                        'date': _decode(msg.get('Date')),
                    })
                return results
        except imaplib.IMAP4.error as exc:
            return f'IMAP login failed: {exc}'
        except Exception as exc:
            return f'Could not check emails: {exc}'

    def summarize_emails(self, limit: int = 10) -> str:
        result = self.check_emails(limit=limit)
        if isinstance(result, str):
            return result
        if not result:
            return 'Your inbox is empty.'
        lines = [f'You have {len(result)} recent emails:']
        for i, msg in enumerate(result, 1):
            lines.append(f"{i}. {msg['subject']} — from {msg['sender']}")
        return '\n'.join(lines)

    # ------------------------------------------------------------------
    # SMTP
    # ------------------------------------------------------------------
    def send_email(self, recipient: str, subject: str, message: str) -> str:
        err = self._missing_creds()
        if err:
            return err
        if not recipient or '@' not in recipient:
            return f'Refusing to send: "{recipient}" does not look like an email address.'
        try:
            mime = MIMEMultipart()
            mime['From'] = self.email_address
            mime['To'] = recipient
            mime['Subject'] = subject
            mime.attach(MIMEText(message, 'plain'))
            context = ssl.create_default_context()
            with smtplib.SMTP(self.smtp_host, self.smtp_port) as smtp:
                smtp.starttls(context=context)
                smtp.login(self.email_address, self.email_password)
                smtp.sendmail(self.email_address, [recipient], mime.as_string())
            return f'Email sent to {recipient}.'
        except smtplib.SMTPAuthenticationError as exc:
            return f'SMTP login failed: {exc}'
        except Exception as exc:
            return f'Could not send email: {exc}'
