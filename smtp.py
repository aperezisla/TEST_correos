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
import emails_smtp

rol_user = sys.argv[2]
#Hacer todos los casos, mejor coger el rol del usuario a crear
#stage = sys.argv[4]
caso_de_uso = sys.argv[4]
cuenta_pro=sys.argv[6]
new_user = sys.argv[8]
user=sys.argv[9]
password=sys.argv[10]
address=sys.argv[12]

accounts=functions.coger_role(rol_user,cuenta_pro)
if accounts == (0,0,0,0):
	print('[INFO] No es necesario crear ninguna cuenta')
	sys.exit(1)
functions.assign_role_arn(accounts,user,password,address,new_user,rol_user,caso_de_uso) 
print('[INFO] Finalizado con éxito la creación del usuario')
