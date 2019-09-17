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
import emails_smtp


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
		print('Entorno: Stage can only be dev, int, pro or opt')
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
		print('Login Stage can only be dev, int, pro or opt')
		sys.exit(1)


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
		print('role: Stage can only be dev, int, pro or opt')
		sys.exit(1)


def generateSecureRandomString(stringLength = 12):
	special_characters="!@#$%^&*()_+-=[]{}|'"
	password_characters = string.ascii_letters + string.digits + special_characters
	return ''.join(random.sample(password_characters,stringLength))


def read_template(filename):
	with open(filename,'r', encoding='ISO-8859-1') as template_file:
		template_file_content = template_file.read()
	return Template(template_file_content)


def aws_connection(role_arn):
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

	return iam

def create_credentials(new_user,iam):
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


def coger_role(rol_user):
	if rol_user == '1':
		#Desarrollador global
		#Se crea cuenta en pro y dev
		return (1,0,1,0)
	if rol_user == '2':
		#Desarrollador (caso de uso)
		#Se crea cuenta en dev
		return (0,0,1,0)
	if rol_user == '3':
		#Desarrollador avanzado de Tableau (caso de uso)
		#Se crea cuenta en pro y dev
		return (1,0,1,0)
	if rol_user == '4':
		#Responsable de area usuaria (area)
		#Se crea cuenta en pro
		return (1,0,0,0)
	if rol_user == '5':
		#Engineering
		#Se crea cuenta en pro,int,dev y opt
		return (1,1,1,1)
	if rol_user == '6':
		#Engineering Manager
		#Se crea cuenta en pro,int,dev y opt
		return (1,1,1,1)

def assign_basicforce(iam,new_user):
	#Le añado a los dos grupos: 
	response = iam.add_user_to_group(
		GroupName='BasicIAM',
		UserName=new_user
	)

	response = iam.add_user_to_group(
		GroupName='ForceMFA',
		UserName=new_user
	)

def assign_groups(iam,stage,rol_user,new_user,caso_de_uso):
	#if rol_user == '1':
	#if rol_user == '2':
	#if rol_user == '3':
	#if rol_user == '4':
	if rol_user == '5':
			assign_basicforce(iam,new_user)
	#if rol_user == '6':

def assign_role_arn(accounts,user,password,address,new_user,rol_user,caso_de_uso):
	#if accounts[0] == 1:
		#Se crea cuenta en pro
		#pass
	if accounts[1] == 1:
		stage = 'int'
		print(stage)
		#Se crea cuenta en int
		role_arn = 'arn:aws:iam::624472315656:role/int-na-delegated-jenkins'
		iam=aws_connection(role_arn)

		# Se crea el usuario
		response = iam.create_user(
			UserName=new_user
		)

		assign_groups(iam,stage,rol_user,new_user,caso_de_uso)
		create_credentials(new_user,iam)

		print("el csv se ha creado")
		print("me meto en las funciones")

		print("ahora se manda el primer correo")
		emails_smtp.send_email1(user,password,address,new_user,stage)

		print("ahora mando el segundo correo con las credenciales")
		emails_smtp.send_email2(user,password,address,new_user,stage)
		print("se han mandado ambos correos")
		
	if accounts[2] == 1:
		#Se crea cuenta en dev
		pass
	if accounts[3] == 1:
		#Se crea cuenta en opt
		pass