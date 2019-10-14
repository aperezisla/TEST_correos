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
import argparse

casos_de_uso=[
	'PLEXT',
	'PLEXT_TOA',
	'PLEXT_ASSIA',
	'PLEXT_HADA',
	'ASTRO',
	'VIDEO_Y_PLATAFORMAS',
	'No'
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
	'Desarrollador_Global':['dev'],
	'Desarrollador':['dev'],
	'Desarrollador_Avanzado_De_Tableau':['dev'],
	#al responsable se le añade solo a pro si lo necesita
	'Responsable_De_Area_Usuaria':[''],
	'Engineering':['pro','int','dev','opt'],
	'Engineering_Manager':['pro','int','dev','opt']
}

pro_options = {
	'Si',
	'No'
}

#ARGUMENTOS: 
parser = argparse.ArgumentParser()
parser.add_argument('--rol', choices=roles,required=True,help=roles)
parser.add_argument('--casodeuso1',choices=casos_de_uso,help=casos_de_uso)
parser.add_argument('--casodeuso2',choices=casos_de_uso,help=casos_de_uso)
parser.add_argument('--casodeuso3',choices=casos_de_uso,help=casos_de_uso)
parser.add_argument('--pro',choices=pro_options, help=pro_options)
parser.add_argument('--newuser',required=True,help ='Formato nombre.apellido')
parser.add_argument('--u',help ='Usuario necesario para los correos')
parser.add_argument('--p',help ='Contraseña necesaria para los correos')
parser.add_argument('--address',required=True,help ='Dirección de correo a enviar las credenciales')
args = parser.parse_args()

if args.pro != 'No':
	if 'pro' not in roles[args.rol]:
		roles[args.rol].append('pro')
print(roles)
		
mis_casos=[]
if args.casodeuso1 != 'No':
	mis_casos.append(args.casodeuso1)
if args.casodeuso2 != 'No':
	mis_casos.append(args.casodeuso2)
if args.casodeuso3 != 'No':
	mis_casos.append(args.casodeuso3)

accounts = roles[args.rol]
functions.assign_role_arn(accounts,args.u,args.p,args.address,args.newuser,args.rol,mis_casos,entornos) 
print('[INFO] Finalizado con éxito.')
