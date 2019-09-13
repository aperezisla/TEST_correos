import boto3
import smtplib
import email.utils
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from string import Template
import jinja2
import os
import sys

def read_template(filename):
    with open(filename,'r', encoding='ISO-8859-1') as template_file:
        template_file_content = template_file.read()
    return Template(template_file_content)

#PONER EN COPIA A NA CUANDO ESTE TODO OK
def send_email(user,password,address):
    msg = MIMEMultipart('alternative')
    sender = 'no-reply@na.telefonicadev.com'
    sender_name = 'na-engineering'
    smtp_host='email-smtp.eu-west-1.amazonaws.com'
    smtp_port=587
    msg['Subject'] = 'Acceso a AWS Network Analytics entorno de ....'

    msg['From'] = email.utils.formataddr((sender_name, sender))

    msg['To'] =address

    message_template = read_template('mensaje1.txt')
    message = message_template.safe_substitute(name='Nombre', entorno='int', loginurl='na-int', user_name='nombre.usuario')
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

        print('Mail enviado satisfactoriamente')

    except Exception as e:

        print("Error: ", e)

    #Una vez mandado el primer correo, se manda el segundo con los credenciales


user=sys.argv[2]
password=sys.argv[4]
address=sys.argv[6]

iam = boto3.client('iam')
response = iam.create_user(
    UserName='test.test'
)

#print(response)

#Le añado a los dos grupos: 
response = iam.add_user_to_group(
    GroupName='BasicIAM',
    UserName='test.test'
)
#print(response)

response = iam.add_user_to_group(
    GroupName='ForceMFA',
    UserName='test.test'
)
#print(response)
print("se ha añadido al usuario a los dos grupos")
print("ahora se manda el primer correo")
send_email(user,password,address)

#De aqui para arriba lo hace bien, creo funcion para mandar el segundo correo

print("creo la contraseña")
response = iam.create_access_key(
    UserName='test.test',
)

print(response)