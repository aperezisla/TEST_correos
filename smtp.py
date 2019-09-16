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

def get_name(new_user):
    real=''
    for i in new_user:
        if(i == '.'):
            break
        else:
            real += i
        real=real[0].upper() + real[1:]
        return(real)

def get_entorno(stage):
    if stage == 'int':
        return 'integración'
    elif stage == 'dev':
        return 'desarrollo'
    elif stage == 'opt':
        return 'operaciones'
    elif stage == 'pro':
        return 'producción'
    else:
        print('Stage can only be dev, int, pro or opt')
        sys.exit(1)

def get_loginurl(stage):
    if stage == 'int':
        return 'na-int'
    elif stage == 'dev':
        return 'na-dev'
    elif stage == 'opt':
        return 'na-opt'
    elif stage == 'pro':
        return 'na-pro'
    else:
        print('Stage can only be dev, int, pro or opt')
        sys.exit(1)

def generateSecureRandomString(stringLength = 12):
    password_characters = string.ascii_letters + string.digits + string.punctuation
    return ''.join(random.sample(password_characters,stringLength))

def get_role(stage):
    if stage == 'int':
        return 'arn:aws:iam::624472315656:role/int-na-delegated-jenkins'
    elif stage == 'dev':
        return 'arn:aws:iam::363896548138:role/dev-na-delegated-jenkins'
    elif stage == 'opt':
        return 'arn:aws:iam::416481324865:role/pro-opt-delegated-jenkins'
    elif stage == 'pro':
        return 'arn:aws:iam::486960344036:role/pro-na-delegated-jenkins'
    else:
        print('Stage can only be dev, int, pro or opt')
        sys.exit(1)

#Hacer todos los casos, mejor coger el rol del usuario a crear
stage = sys.argv[2]
new_user = sys.argv[4]
user=sys.argv[6]
password=sys.argv[8]
address=sys.argv[10]

role_arn=get_role(stage)

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
    UserName=new_user
)

#Le añado a los dos grupos: 
response = iam.add_user_to_group(
    GroupName='BasicIAM',
    UserName=new_user
)

response = iam.add_user_to_group(
    GroupName='ForceMFA',
    UserName=new_user
)

#aqui creo la password
contrasena = generateSecureRandomString(12)

response = iam.create_login_profile(
    UserName=new_user,
    Password=contrasena,
    PasswordResetRequired=True
    )

#VOY A CREAR LAS CREDENCIALES
print("creo las credenciales")
response = iam.create_access_key(
    UserName=new_user,
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
def send_email1(user,password,address,new_user,stage):
    msg = MIMEMultipart('alternative')
    sender = 'no-reply@na.telefonicadev.com'
    sender_name = 'na-engineering'
    smtp_host='email-smtp.eu-west-1.amazonaws.com'
    smtp_port=587
    entorno=get_entorno(stage)
    loginurl=get_loginurl(stage)
    nombre=get_name(new_user)
    msg['Subject'] = 'Acceso a AWS Network Analytics entorno de '+ entorno
    msg['From'] = email.utils.formataddr((sender_name, sender))
    msg['To'] =address
    message_template = read_template('mensaje1.txt')
    message = message_template.safe_substitute(name=nombre, entorno=stage, loginurl=loginurl, user_name=new_user)
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

def send_email2(user,password,address,new_user,stage):
    msg = MIMEMultipart('alternative')
    sender = 'no-reply@na.telefonicadev.com'
    sender_name = 'na-engineering'
    smtp_host='email-smtp.eu-west-1.amazonaws.com'
    smtp_port=587
    nombre=get_name(new_user)
    msg['Subject'] = 'Credenciales AWS Network Analytics entorno '+ stage
    msg['From'] = email.utils.formataddr((sender_name, sender))
    msg['To'] =address
    #Necesito el mensaje en html?
    message_template = read_template('mensaje2.txt')
    #poner opciones dependiendo de la cuenta donde se ha creado al usuario
    message = message_template.safe_substitute(name=nombre)
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
send_email1(user,password,address,new_user,stage)

#De aqui para arriba lo hace bien, creo funcion para mandar el segundo correo

print("ahora mando el segundo correo con las credenciales")
send_email2(user,password,address,new_user,stage)
print("se han mandado ambos correos")