from flask_mail import Message
from flask import render_template, current_app
from api.extensions import mail
from api.celery_app import celery


@celery.task()
def send_mail(to='', subject='', template='', **kwargs):
    app = current_app._get_current_object()
    print(app)
    msg = Message(
        subject, sender=current_app.config['FLASKY_MAIL_SENDER'], recipients=[to])
    msg.body = render_template(template + '.txt', **kwargs)
    with app.app_context():
        mail.send(msg)
