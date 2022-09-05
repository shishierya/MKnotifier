import json
import log as logger
import os
import smtplib
from email.mime.text import MIMEText
from email.header import Header


def send_qq_email(message):
    email_json = load_json("email.json")
    from_addr = email_json["from_addr"]
    password = email_json["password"]
    to_addr = email_json["to_addr"]
    smtp_server = "smtp.qq.com"

    msg = MIMEText(message, "plain", "utf8")
    msg['From'] = Header('云服务器')
    msg['to'] = Header('通知号')
    subject = "MK官网心仪包包到货通知"
    msg['Subject'] = Header(subject, 'utf8')
    try:
        smtp_obj = smtplib.SMTP_SSL(smtp_server)
        smtp_obj.connect(smtp_server, 465)
        smtp_obj.login(from_addr, password)
        smtp_obj.sendmail(from_addr, to_addr, msg.as_string())
        logger.info("Send email Success.")
    except smtplib.SMTPException as e:
        logger.info("Email could not be sent:" + str(e))
    finally:
        smtp_obj.quit()


def load_json(json_path_msg):
    json_path = os.path.join(os.path.dirname(__file__), json_path_msg)
    with open(json_path, mode='r', encoding='utf8') as f:
        content = json.load(f)
        return content


