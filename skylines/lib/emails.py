from threading import Thread
from flask import current_app, copy_current_request_context
from flask_mail import Message


def send_async(msg):
    @copy_current_request_context
    def send_message(message):
        try:
            current_app.mail.send(message)
        except Exception, e:
            current_app.logger.error('Send mail async error: %s' % e.message)

    sender = Thread(name='mail_sender', target=send_message, args=(msg,))
    sender.start()


def send_mail(subject, sender, recipients, text_body=None, html_body=None,
              async=True, info_log_str=None):
    msg = Message(
        subject=subject,
        sender=sender,
        recipients=recipients,
        body=text_body,
        html=html_body,
        charset='utf-8',
    )

    if info_log_str is not None:
        current_app.logger.info('Send mail: %s' % info_log_str)

    if async:
        send_async(msg)
    else:
        current_app.mail.send(msg)