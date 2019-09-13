import boto3
import smtplib
import email.utils
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import jinja2
import os

import sys
user=sys.argv[2]
password=sys.argv[4]
address=sys.argv[6]


'''

    Envía un email

'''

def send_email(user,password,address):
    address="<andrea.perezisla.practicas@telefonica.com>"
    msg = MIMEMultipart('alternative')
    sender = 'no-reply@na.telefonicadev.com'
    sender_name = 'na-engineering'
    smtp_host='email-smtp.eu-west-1.amazonaws.com'
    smtp_port=587
    msg['Subject'] = "correo de prueba"

    msg['From'] = email.utils.formataddr((sender_name, sender))

    msg['To'] = ','.join(address)

    message="mensaje de prueba"

    #if cc is not None:

        #msg['CC'] = ','.join(cc)

        #recipients = to + cc

    #else:

        #recipients = to



    msg.attach(MIMEText(message, 'plain', 'UTF-8'))

    #msg.attach(MIMEText(body_html, 'html', 'UTF-8'))



    try:

        server = smtplib.SMTP(smtp_host,smtp_port)

        server.ehlo()

        server.starttls()

        server.ehlo()

        server.login(user, password)

        server.sendmail(sender, msg['To'], message)

        server.close()

        print('[INFO] Sent email.')

    except Exception as e:

        print("Error: ", e)

send_email(user,password,address)