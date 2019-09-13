import boto3
import smtplib
import email.utils
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from string import Template
import jinja2
import os
import sys
user=sys.argv[2]
password=sys.argv[4]
address=sys.argv[6]


def read_template(filename):
    with open(filename,'r', encoding='ISO-8859-1') as template_file:
        template_file_content = template_file.read()
    return Template(template_file_content)

'''

    Envía un email

'''

def send_email(user,password,address):
    msg = MIMEMultipart('alternative')
    sender = 'no-reply@na.telefonicadev.com'
    sender_name = 'na-engineering'
    smtp_host='email-smtp.eu-west-1.amazonaws.com'
    smtp_port=587
    msg['Subject'] = 'Acceso a AWS Network Analytics entorno de ....'

    msg['From'] = email.utils.formataddr((sender_name, sender))

    msg['To'] =address

    #message=(" Hola ......,\r\n")
    message_template = read_template('mensaje1.txt')
    message = message_template.substitute(name='Nombre', entorno='int', loginurl='na-int', user_name='nombre.usuario')
    #if cc is not None:

        #msg['CC'] = ','.join(cc)

        #recipients = to + cc

    #else:

        #recipients = to



    msg.attach(MIMEText(message, 'plain'))

    #msg.attach(MIMEText(body_html, 'html', 'UTF-8'))



    try:

        server = smtplib.SMTP(smtp_host,smtp_port)

        server.ehlo()

        server.starttls()

        server.ehlo()

        server.login(user, password)

        server.sendmail(sender, msg['To'], msg.as_string())

        server.close()

        print('[INFO] Sent email.')

    except Exception as e:

        print("Error: ", e)

send_email(user,password,address)