# coding: utf-8
from flask_mail import Message
from flask import current_app, render_template
from . import mail
from manage import celery

@celery.task
def send_email(app, msg):
        mail.send(msg)

def create_email(to, subject, template, **kwargs):
    app = current_app._get_current_object()
    msg = Message(app.config['FLASKY_MAIL_SUBJECT_PREFIX'] + ' ' + subject, sender=app.config['FLASK_MAIL_SENDER'], recipients=[to])
    msg.body = render_template(template + '.txt', **kwargs)
    msg.html = render_template(template + '.html', **kwargs)
    return msg