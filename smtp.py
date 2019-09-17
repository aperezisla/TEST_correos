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
stage = sys.argv[4]
new_user = sys.argv[6]
user=sys.argv[7]
password=sys.argv[8]
address=sys.argv[10]

#print(rolecito)

accounts=functions.coger_role(rol_user)
functions.assign_role_arn(accounts,user,password,address,new_user) 
#role_arn=functions.get_role(stage)
# iam=functions.aws_connection(role_arn)

# # Se crea el usuario
# response = iam.create_user(
#     UserName=new_user
# )

# #Le añado a los dos grupos: 
# response = iam.add_user_to_group(
#     GroupName='BasicIAM',
#     UserName=new_user
# )

# response = iam.add_user_to_group(
#     GroupName='ForceMFA',
#     UserName=new_user
# )

# functions.create_credentials(new_user,iam)

# print("el csv se ha creado")
# print("me meto en las funciones")

# print("ahora se manda el primer correo")
# emails_smtp.send_email1(user,password,address,new_user,stage)

# print("ahora mando el segundo correo con las credenciales")
# emails_smtp.send_email2(user,password,address,new_user,stage)
# print("se han mandado ambos correos")