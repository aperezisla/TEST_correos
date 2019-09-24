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
import argparse

#rol_user = sys.argv[2]
#Hacer todos los casos, mejor coger el rol del usuario a crear
#stage = sys.argv[4]
#caso_de_uso = sys.argv[4]
#cuenta_pro=sys.argv[6]
#new_user = sys.argv[8]
#user=sys.argv[9]
#password=sys.argv[10]
#address=sys.argv[12]

casos_de_uso=[
	'PLEXT',
	'PLEXT TOA',
	'PLEXT ASSIA',
	'PLEXT HADA',
	'ASTRO',
	'VIDEO Y PLATAFORMAS'
]

entornos = {
	'int' : 
		['integración','arn:aws:iam::624472315656:role/int-na-delegated-jenkins','na-int'],
	'pro' : 
		['producción','arn:aws:iam::486960344036:role/pro-na-delegated-jenkins','na-pro'],
	'dev' : 
		['desarrollo','arn:aws:iam::363896548138:role/dev-na-delegated-jenkins','na-dev'],
	'opt' : 
		['operaciones','arn:aws:iam::416481324865:role/pro-opt-delegated-jenkins','na-opt']
}

roles = {
	'Desarrollador global':['dev'],
	'Desarrollador':['dev'],
	'Desarrollador avanzado de Tableau':['dev'],
	#al responsable se le añade solo a pro si lo necesita
	'Responsable de area usuaria':[''],
	'Engineering':['pro','int','dev','opt'],
	'Engineering Manager':['pro','int','dev','opt']
}

#print(casos_de_uso)


#ARGUMENTOS: 
parser = argparse.ArgumentParser()
parser.add_argument('--rol', choices=roles,required=True,help=roles)
parser.add_argument('--casodeuso1',choices=casos_de_uso,help=casos_de_uso)
parser.add_argument('--casodeuso2',choices=casos_de_uso,help=casos_de_uso)
parser.add_argument('--casodeuso3',choices=casos_de_uso,help=casos_de_uso)
parser.add_argument('--pro',action='store_true', default = False)
parser.add_argument('--newuser',required=True,help ='Formato nombre.apellido')
parser.add_argument('user',help ='Usuario necesario para los correos')
parser.add_argument('password',help ='Contraseña necesaria para los correos')
parser.add_argument('--address',required=True,help ='Dirección de correo a enviar las credenciales')
args = parser.parse_args()
if args.pro == True:
	if 'pro' not in roles[args.rol]:
		roles[args.rol].append('pro')
mis_casos=[]
if args.casodeuso1 != None:
	mis_casos.append(args.casodeuso1)
if args.casodeuso2 != None:
	mis_casos.append(args.casodeuso2)
if args.casodeuso3 != None:
	mis_casos.append(args.casodeuso3)
#accounts=functions.coger_role(rol_user,cuenta_pro,caso_de_uso)
#if accounts == (0,0,0,0):
	#print('[INFO] No es necesario crear ninguna cuenta.')
	#sys.exit(1)
accounts = roles[args.rol]
functions.assign_role_arn(accounts,args.user,args.password,args.address,args.newuser,args.rol,mis_casos,entornos) 
print('[INFO] Finalizado con éxito.')
