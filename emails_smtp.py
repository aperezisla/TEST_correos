import boto3
import smtplib
import email.utils
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
from string import Template
import jinja2
import os
import sys
import string
import random
import functions

#PONER EN COPIA A NA CUANDO ESTE TODO OK
def send_email1(user,password,address,new_user,stage):
    msg = MIMEMultipart('alternative')
    sender = 'no-reply@na.telefonicadev.com'
    sender_name = 'na-engineering'
    cc=['andreap.isla97@gmail.com']
    mailto=['andrea.perezisla.practicas@telefonica.com']
    emails=mailto + cc
    smtp_host='email-smtp.eu-west-1.amazonaws.com'
    smtp_port=587
    entorno=functions.get_entorno(stage)
    loginurl=functions.get_loginurl(stage)
    nombre=functions.get_name(new_user)
    msg['Subject'] = 'Acceso a AWS Network Analytics entorno de '+ entorno
    msg['From'] = email.utils.formataddr((sender_name, sender))
    msg['To'] =address
    message_template = functions.read_template('mensaje1.txt')
    message = message_template.safe_substitute(name=nombre, entorno=stage, loginurl=loginurl, user_name=new_user)

    msg.attach(MIMEText(message, 'plain'))
    #msg.attach(MIMEText(body_html, 'html', 'UTF-8'))
    try:
        server = smtplib.SMTP(smtp_host,smtp_port)
        server.ehlo()
        server.starttls()
        server.ehlo()
        server.login(user, password)
        server.sendmail(sender, emails, msg.as_string())
        server.close()
        print('Mail enviado satisfactoriamente')
    except Exception as e:
        print("Error: ", e)
    #Una vez mandado el primer correo, se manda el segundo con los credenciales

def send_email2(user,password,address,new_user,stage):
    msg = MIMEMultipart('alternative')
    sender = 'no-reply@na.telefonicadev.com'
    sender_name = 'na-engineering'
    smtp_host='email-smtp.eu-west-1.amazonaws.com'
    smtp_port=587
    nombre=functions.get_name(new_user)
    msg['Subject'] = 'Credenciales AWS Network Analytics entorno '+ stage
    msg['From'] = email.utils.formataddr((sender_name, sender))
    msg['To'] =address

    message_template = functions.read_template('mensaje2.txt')

    message = message_template.safe_substitute(name=nombre)

    msg.attach(MIMEText(message, 'plain'))

    mail_file=MIMEBase('application','csv')
    mail_file.set_payload(open('credentials.csv','r').read())
    mail_file.add_header('Content-Disposition','attachment',filename='credentials.csv')
    encoders.encode_base64(mail_file)
    msg.attach(mail_file)

    try:
        server = smtplib.SMTP(smtp_host,smtp_port)
        server.ehlo()
        server.starttls()
        server.ehlo()
        server.login(user, password)
        server.sendmail(sender, msg['To'], msg.as_string())
        server.close()
        print('Mail de credenciales enviado satisfactoriamente')
    except Exception as e:
        print("Error: ", e)
