import smtplib
import excalibur
log = excalibur.logger.getlogger()


email_server_ssl_configs = {
    "yahoo": {
        "url": "smtp.mail.yahoo.com",
        "port": 465,
    }
}


def send_email(username, password, subject, date, message_text, to, email_server_provider="yahoo"):
    fromMy = username  # email from would be the same as uername
    msg = "From: %s\nTo: %s\nSubject: %s\nDate: %s\n\n%s" % (fromMy, to, subject, date, message_text)
    try:
        # server = smtplib.SMTP("smtp.mail.yahoo.com",587)
        config = email_server_ssl_configs[email_server_provider]
        url = config["url"]
        port = config["port"]
        server = smtplib.SMTP_SSL(url, port)

        server.login(username, password)
        server.sendmail(fromMy, to, msg)
        server.quit()
        log.info('Email has sent from {fr} to {to} with subject:{subject}'.format(fr=fromMy, to=to, subject=subject))
    except Exception as e:
        log.error('Failed to send email from {fr} to {to} with subject:{subject}, error:{er}'.format(fr=fromMy, to=to, subject=subject, er=str(e)))
