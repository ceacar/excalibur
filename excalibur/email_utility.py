import smtplib
import excalibur
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.header import Header


log = excalibur.logger.getlogger()


email_server_ssl_configs = {
    "yahoo": {
        "url": "smtp.mail.yahoo.com",
        "port": 465,
    }
}


def send_email(username, password, subject, date, message_text, to, email_server_provider="yahoo"):
    fromMy = username  # email from would be the same as uername
    msg_to_send = "%s" % (message_text)
    # use below code to avoid encoding error when sending an email
    msg = MIMEMultipart('alternative')
    msg.set_charset('utf16')
    msg['Subject'] = Header(
        subject.encode('utf-16'),
        'UTF-16'
    ).encode()
    msg_to_attach = MIMEText(msg_to_send.encode('utf-16'), 'html', 'UTF-16')
    msg.attach(msg_to_attach)
    try:
        # server = smtplib.SMTP("smtp.mail.yahoo.com",587)
        config = email_server_ssl_configs[email_server_provider]
        url = config["url"]
        port = config["port"]
        server = smtplib.SMTP_SSL(url, port)

        server.login(username, password)
        server.sendmail(fromMy, to, msg.as_string())
        server.quit()
        log.info('Email has sent from {fr} to {to} with subject:{subject}'.format(fr=fromMy, to=to, subject=subject))
    except Exception as e:
        log.error('Failed to send email from {fr} to {to} with subject:{subject}, error:{er}'.format(fr=fromMy, to=to, subject=subject, er=str(e)))
