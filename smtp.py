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

def generateSecureRandomString(stringLength = 12):
    password_characters = string.ascii_letters + string.digits + string.punctuation
    return ''.join(random.choice(password_characters) for i in range(stringLength))

#Hacer todos los casos, mejor coger el rol del usuario a crear
stage = sys.argv[2]
newuser = sys.argv[4]
user=sys.argv[6]
password=sys.argv[8]
address=sys.argv[10]


if stage == 'int':
    role_arn = role_arn = 'arn:aws:iam::624472315656:role/int-na-delegated-jenkins'
else:
    print('Stage can only be dev, int, pro or opt')
    sys.exit(1)

sts=boto3.client('sts')
response = sts.assume_role(
    RoleArn=role_arn,
    RoleSessionName='jenkins-new-user'
)

access_key_id = response['Credentials']['AccessKeyId']
secret_access_key = response['Credentials']['SecretAccessKey']
session_token = response['Credentials']['SessionToken']

iam = boto3.client(
    'iam',
    aws_access_key_id=access_key_id,
    aws_secret_access_key=secret_access_key,
    aws_session_token=session_token,
    region_name='eu-west-1'
)

# Se crea el usuario
response = iam.create_user(
    UserName=newuser
)

#Le añado a los dos grupos: 
response = iam.add_user_to_group(
    GroupName='BasicIAM',
    UserName='test.test'
)

response = iam.add_user_to_group(
    GroupName='ForceMFA',
    UserName='test.test'
)

#aqui creo la password
contrasena = generateSecureRandomString(12)

response = iam.create_login_profile(
    UserName=newuser,
    Password=contrasena,
    PasswordResetRequired=True
    )

#VOY A CREAR LAS CREDENCIALES
print("creo las credenciales")
response = iam.create_access_key(
    UserName='test.test',
)

data = response['AccessKey']
data.pop('Status')
data.pop('CreateDate')
data['Password'] = contrasena
data['ConsoleLoginLink']='https://na-int.signin.aws.amazon.com/console'
with open('credentials.csv','w') as f:
    for key in data.keys():
        f.write("%s,%s\n"%(key,data[key]))

print("el csv se ha creado")
print("me meto en las funciones")


def read_template(filename):
    with open(filename,'r', encoding='ISO-8859-1') as template_file:
        template_file_content = template_file.read()
    return Template(template_file_content)

#PONER EN COPIA A NA CUANDO ESTE TODO OK
def send_email1(user,password,address):
    msg = MIMEMultipart('alternative')
    sender = 'no-reply@na.telefonicadev.com'
    sender_name = 'na-engineering'
    smtp_host='email-smtp.eu-west-1.amazonaws.com'
    smtp_port=587
    msg['Subject'] = 'Acceso a AWS Network Analytics entorno de ....'
    msg['From'] = email.utils.formataddr((sender_name, sender))
    msg['To'] =address
    message_template = read_template('mensaje1.txt')
    #poner opciones dependiendo de la cuenta donde se ha creado al usuario
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

def send_email2(user,password,address):
    msg = MIMEMultipart('alternative')
    sender = 'no-reply@na.telefonicadev.com'
    sender_name = 'na-engineering'
    smtp_host='email-smtp.eu-west-1.amazonaws.com'
    smtp_port=587
    msg['Subject'] = 'Credenciales AWS Network Analytics entorno ....'
    msg['From'] = email.utils.formataddr((sender_name, sender))
    msg['To'] =address
    #Necesito el mensaje en html?
    message_template = read_template('mensaje2.txt')
    #poner opciones dependiendo de la cuenta donde se ha creado al usuario
    message = message_template.safe_substitute(name='Nombre', entorno='int', loginurl='na-int', user_name='nombre.usuario')
    #if cc is not None:
        #msg['CC'] = ','.join(cc)
        #recipients = to + cc
    #else:
        #recipients = to
    msg.attach(MIMEText(message, 'plain'))
    #msg.attach(MIMEText(body_html, 'html', 'UTF-8'))

    #adjunto las credenciales
    #mail_file = file('crd.csv').read()
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
        print('Mail enviado satisfactoriamente')
    except Exception as e:
        print("Error: ", e)


print("ahora se manda el primer correo")
send_email1(user,password,address)

#De aqui para arriba lo hace bien, creo funcion para mandar el segundo correo

print("ahora mando el segundo correo con las credenciales")
send_email2(user,password,address)
print("se han mandado ambos correos")