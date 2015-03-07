from threading import Thread
from flask import current_app, copy_current_request_context
from flask_mail import Message


def send_async(msg):
    @copy_current_request_context
    def send_message(message):
        current_app.mail.send(message)

    sender = Thread(name='mail_sender', target=send_message, args=(msg,))
    sender.start()


def send_mail(subject, sender, recipients, text_body=None, html_body=None):
    msg = Message(
        subject=subject,
        sender=sender,
        recipients=recipients,
        body=text_body,
        html=html_body,
        charset='utf-8',
    )
    send_async(msg)
    