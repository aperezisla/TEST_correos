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
new_user = sys.argv[6]
user=sys.argv[7]
password=sys.argv[8]
address=sys.argv[10]

accounts=functions.coger_role(rol_user)
functions.assign_role_arn(accounts,user,password,address,new_user,rol_user,caso_de_uso) 
print('final, se han creado los usuarios correspondientes')
