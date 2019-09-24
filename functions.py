import boto3
import smtplib
import email.utils
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
from string import Template
from botocore.exceptions import ClientError
import jinja2
import os
import sys
import string
import random
import emails_smtp

def get_casodeuso(caso_de_uso):
	if caso_de_uso == '1':
		return 'PLEXT'
	if caso_de_uso == '2':
		return 'PLEXT TOA'
	if caso_de_uso == '3':
		return 'PLEXT ASSIA'
	if caso_de_uso == '4':
		return 'PLEXT HADA'
	if caso_de_uso == '5':
		return 'ASTRO'
	if caso_de_uso == '6':
		return 'VIDEO Y PLATAFORMAS'


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
		print('[ERROR] Entorno: Stage can only be dev, int, pro or opt.')
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
		print('[ERROR] Login: Stage can only be dev, int, pro or opt.')
		sys.exit(1)


def get_role(stage):
	if stage == 'int':
		return 'arn:aws:iam::624472315656:role/int-na-delegated-jenkins'
	elif stage == 'dev':
		return 
	elif stage == 'opt':
		return 'arn:aws:iam::416481324865:role/pro-opt-delegated-jenkins'
	elif stage == 'pro':
		return 'arn:aws:iam::486960344036:role/pro-na-delegated-jenkins'
	else:
		print('[ERROR] Role: Stage can only be dev, int, pro or opt.')
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

def create_credentials(newuser,iam,rol_str,consoleLogin):
	#aqui creo la password
	#El responsable de area no incluye acceso a la consola, solo se crea el par de access key
	if rol_str != 'Responsable de area usuaria': 
		while True:
			try:
				contrasena = generateSecureRandomString(12)
				response = iam.create_login_profile(
					UserName=newuser,
					Password=contrasena,
					PasswordResetRequired=True
				)
				print('[INFO] La contraseña de acceso se ha creado correctamente.')
				break
			except Exception:
				print('[INFO] La contraseña no es válida, se crea de nuevo.')

	#print("creo las credenciales")
	response = iam.create_access_key(
		UserName=newuser,
	)

	data = response['AccessKey']
	data.pop('Status')
	data.pop('CreateDate')
	#El responsable de area no incluye acceso a la consola, solo se crea el par de access key
	if rol_str != 'Responsable de area usuaria':
		data['Password'] = contrasena
	data['ConsoleLoginLink']='https://'+consoleLogin+'.signin.aws.amazon.com/console'
	with open('credentials.csv','w') as f:
		f.write("%s,%s\n"%('UserName',data['UserName']))
		if rol_str != 'Responsable de area usuaria':
			f.write("%s,%s\n"%('Password',data['Password']))
		f.write("%s,%s\n"%('AccessKeyId',data['AccessKeyId']))
		f.write("%s,%s\n"%('SecretAccessKey',data['SecretAccessKey']))
		f.write("%s,%s\n"%('ConsoleLoginLink',data['ConsoleLoginLink']))


def coger_role(rol_user,cuenta_pro,caso_de_uso):
	if rol_user == '1':
		#Desarrollador global
		#Se crea cuenta en dev
		print('[INFO] Desarrollador global: ')
		if cuenta_pro in ('S','s'):
			#Tambien en pro
			print('[INFO] Se crea también cuenta en pro por petición.')
			return (1,0,1,0)
		else:
			print('[INFO] Se crea cuenta únicamente en dev.')
			return (0,0,1,0)
	if rol_user == '2':
		#Desarrollador (caso de uso)
		#Se crea cuenta en dev
		print('[INFO] Desarrollador ('+get_casodeuso(caso_de_uso)+'): ')
		if cuenta_pro in ('S','s'):
			#Tambien en pro
			print('[INFO] Se crea también cuenta en pro por petición.')
			return (1,0,1,0)
		else:
			print('[INFO] Se crea cuenta únicamente en dev.')
			return (0,0,1,0)
	if rol_user == '3':
		#Desarrollador avanzado de Tableau (caso de uso)
		#Se crea cuenta en dev
		print('[INFO] Desarrollador avanzado de Tableau ('+get_casodeuso(caso_de_uso)+'): ')
		if cuenta_pro in ('S','s'):
			#Tambien en pro
			print('[INFO] Se crea también cuenta en pro por petición.')
			return (1,0,1,0)
		else:
			print('[INFO] Se crea cuenta únicamente en dev.')
			return (0,0,1,0)
	if rol_user == '4':
		#Responsable de area usuaria (area)
		#Se crea cuenta en pro
		print('[INFO] Responsable de área usuaria: ')
		if cuenta_pro in ('S','s'):
			print('[INFO] Se crea cuenta en pro por petición.')
			return (1,0,0,0)
		else:
			print('[INFO] No es necesario crear usuarios.')
			return (0,0,0,0)
	if rol_user == '5':
		#Engineering
		#Se crea cuenta en pro,int,dev y opt
		print('[INFO] Engineering: ')
		print('[INFO] Se crea cuenta en pro, int, dev y opt.')
		return (1,1,1,1)
	if rol_user == '6':
		#Engineering Manager
		#Se crea cuenta en pro,int,dev y opt
		print('[INFO] Engineering Manager: ')
		print('[INFO] Se crea cuenta en pro, int, dev y opt.')
		return (1,1,1,1)

def assign_basicforce(iam,new_user):
	#Le añado a BasicIAM y a ForceMFA: 
	response = iam.add_user_to_group(
		GroupName='BasicIAM',
		UserName=new_user
	)

	response = iam.add_user_to_group(
		GroupName='ForceMFA',
		UserName=new_user
	)

def assign_specific_group(group,iam,new_user):
	response=iam.add_user_to_group(
		GroupName=group,
		UserName=new_user
	)

def assign_specific_policy(policy,iam,new_user):
	response=iam.attach_user_policy(
		UserName=new_user,
		PolicyArn=policy
	)


def assign_groups(iam,cuenta,rol_str,newuser,mis_casos):
	if rol_str == 'Desarrollador global':
		assign_basicforce(iam,newuser)
		print('[INFO] Asignados los grupos BasicIAM y ForceMFA')
		if cuenta == 'dev':
			assign_specific_group('PowerDevelopers',iam,newuser)
			print('[INFO] Asignado el grupo PowerDevelopers en su usuario dev')
		if cuenta == 'pro':
			assign_specific_group('NaDevGlobalDevPRO',iam,newuser)
			print('[INFO] Asignado el grupo NaDevGlobalDevPRO en su usuario pro')
	if rol_str == 'Desarrollador':
		assign_basicforce(iam,newuser)
		print('[INFO] Asignados los grupos BasicIAM y ForceMFA')
		for caso in mis_casos:
			if cuenta == 'dev':
				if caso == 'PLEXT':
					assign_specific_group('NaDevPlantaExternaAssia',iam,newuser)
					assign_specific_group('NaDevPlantaExternaHada',iam,newuser)
					assign_specific_group('NaDevPlantaExternaTOA',iam,newuser)
					print('[INFO] Asignados los grupos NaDevPlantaExternaAssia, Hada y TOA en su usuario dev')
					assign_specific_policy('NaDevPlantaExternaCrossAccountPolicy',iam,newuser)
					print('[INFO] Asignada la política NaDevPlantaExternaCrossAccountPolicy en su usuario dev')
				if caso == 'PLEXT TOA':
					assign_specific_group('NaDevPlantaExternaTOA',iam,newuser)
					print('[INFO] Asignado el grupo NaDevPlantaExternaTOA en su usuario dev')
				if caso == 'PLEXT ASSIA':
					assign_specific_group('NaDevPlantaExternaAssia',iam,newuser)
					print('[INFO] Asignado el grupo NaDevPlantaExternaAssia en su usuario dev')
				if caso == 'PLEXT HADA':
					assign_specific_group('NaDevPlantaExternaHada',iam,newuser)
					print('[INFO] Asignado el grupo NaDevPlantaExternaHada en su usuario dev')
			if cuenta == 'pro':
				if caso == 'PLEXT':
					assign_specific_group('NaDevPlantaExternaAssia',iam,newuser)
					assign_specific_group('NaDevPlantaExternaHada',iam,newuser)
					assign_specific_group('NaDevPlantaExternaTOA',iam,newuser)
					print('[INFO] Asignados los grupos NaDevPlantaExternaAssia, Hada y TOA en su usuario pro')
	if rol_str == 'Desarrollador avanzado de Tableau':
		assign_basicforce(iam,newuser)
		print('[INFO] Asignados los grupos BasicIAM y ForceMFA')
		for caso in mis_casos:
			if cuenta == 'dev':
				if caso == 'PLEXT TOA':
					assign_specific_group('NaDevTableauPlantaExternaTOA',iam,newuser)
					print('[INFO] Asignado el grupo NaDevTableauPlantaExternaTOA en su usuario dev')
				if caso == 'PLEXT ASSIA':
					assign_specific_group('NaDevTableauPlantaExternaASSIA',iam,newuser)
					print('[INFO] Asignado el grupo NaDevTableauPlantaExternaASSIA en su usuario dev')
				if caso == 'PLEXT HADA':
					assign_specific_group('NaDevTableauPlantaExternaHADA',iam,newuser)
					print('[INFO] Asignado el grupo NaDevTableauPlantaExternaHADA en su usuario dev')
				if caso == 'ASTRO':
					assign_specific_group('NaDevTableauPlantaInternaASTRO',iam,newuser)
					print('[INFO] Asignado el grupo NaDevTableauPlantaInternaASTRO en su usuario dev')
				if caso == 'VIDEO Y PLATAFORMAS':
					assign_specific_group('NaDevTableauOpsPlatGlob',iam,newuser)
					print('[INFO] Asignado el grupo NaDevTableauOpsPlatGlob en su usuario dev')
			if cuenta == 'pro':
				if caso == 'PLEXT TOA':
					assign_specific_group('NaDevTableauPlantaExternaTOA',iam,newuser)
					print('[INFO] Asignado el grupo NaDevTableauPlantaExternaTOA en su usuario pro')
				if caso == 'PLEXT ASSIA':
					assign_specific_group('NaDevTableauPlantaExternaASSIA',iam,newuser)
					print('[INFO] Asignado el grupo NaDevTableauPlantaExternaASSIA en su usuario pro')
				if caso == 'PLEXT HADA':
					assign_specific_group('NaDevTableauPlantaExternaHADA',iam,newuser)
					print('[INFO] Asignado el grupo NaDevTableauPlantaExternaHADA en su usuario pro')
				if caso == 'ASTRO':
					assign_specific_group('NaDevTableauPlantaInternaASTRO',iam,newuser)
					print('[INFO] Asignado el grupo NaDevTableauPlantaInternaASTRO en su usuario pro')
				if caso == 'VIDEO Y PLATAFORMAS':
					assign_specific_group('NaDevTableauOpsPlatGlob',iam,newuser)
					print('[INFO] Asignado el grupo NaDevTableauOpsPlatGlob en su usuario pro')
	if rol_str == 'Responsable de area usuaria':
		assign_basicforce(iam,newuser)
		print('[INFO] Asignados los grupos BasicIAM y ForceMFA')
	if rol_str == 'Engineering':
		assign_basicforce(iam,newuser)
		print('[INFO] Asignados los grupos BasicIAM y ForceMFA')
	if rol_str == 'Engineering Manager':
		assign_basicforce(iam,newuser)
		print('[INFO] Asignados los grupos BasicIAM y ForceMFA')

def assign_role_arn(accounts,user,password,address,newuser,rol_str,mis_casos,entornos):
	for cuenta in accounts:
		#voy mirando donde hay que crear cuenta
		nombre_entorno=entornos[cuenta][0]
		role_arn=entornos[cuenta][1]
		consoleLogin=entornos[cuenta][2]

		iam=aws_connection(role_arn)

		#Se crea el usuario
		try:
			response=iam.create_user(
				UserName=newuser
			)
		except ClientError as e:
			if e.response['Error']['Code'] == 'EntityAlreadyExists':
				print('[ERROR] El usuario ya existe')
			else:
				print('[ERROR] Error inesperado: %s' % e)

		print('[INFO]Usuario creado correctamente en '+cuenta+':')
		assign_groups(iam,cuenta,rol_str,newuser,mis_casos)
		create_credentials(newuser,iam,rol_str,consoleLogin)

		emails_stmp.send_email1(user,password,address,newuser,cuenta,nombre_entorno,consoleLogin)
		emails_stmp.send_email2(user,password,address,newuser,cuenta,)
	# if accounts[0] == 1:
	# 	#Se crea cuenta en pro
	# 	stage = 'pro'
	# 	role_arn = 'arn:aws:iam::486960344036:role/pro-na-delegated-jenkins'
	# 	iam=aws_connection(role_arn)

	# 	# Se crea el usuario
	# 	try:
	# 		response = iam.create_user(
	# 			UserName=new_user
	# 		)
	# 	except ClientError as e:
	# 		if e.response['Error']['Code'] == 'EntityAlreadyExists':
	# 			print('[ERROR] El usuario ya existe')
	# 		else:
	# 			print('[ERROR] Error inesperado: %s' % e) 

	# 	print('[INFO]Usuario creado correctamente en '+stage+':')
	# 	assign_groups(iam,stage,rol_user,new_user,caso_de_uso)
	# 	create_credentials(new_user,iam,rol_user)

	# 	emails_smtp.send_email1(user,password,address,new_user,stage)

	# 	emails_smtp.send_email2(user,password,address,new_user,stage)
	# if accounts[1] == 1:
	# 	stage = 'int'
	# 	#Se crea cuenta en int
	# 	role_arn = 'arn:aws:iam::624472315656:role/int-na-delegated-jenkins'
	# 	iam=aws_connection(role_arn)

	# 	try:
	# 		response = iam.create_user(
	# 			UserName=new_user
	# 		)
	# 	except ClientError as e:
	# 		if e.response['Error']['Code'] == 'EntityAlreadyExists':
	# 			print('[ERROR] El usuario ya existe')
	# 		else:
	# 			print('[ERROR] Error inesperado: %s' % e) 

	# 	print('[INFO]Usuario creado correctamente en '+stage+':')
	# 	assign_groups(iam,stage,rol_user,new_user,caso_de_uso)
	# 	create_credentials(new_user,iam,rol_user)

	# 	emails_smtp.send_email1(user,password,address,new_user,stage)

	# 	emails_smtp.send_email2(user,password,address,new_user,stage)
		
	# if accounts[2] == 1:
	# 	#Se crea cuenta en dev
	# 	stage = 'dev'
	# 	role_arn = 'arn:aws:iam::363896548138:role/dev-na-delegated-jenkins'
	# 	iam=aws_connection(role_arn)

	# 	try:
	# 		response = iam.create_user(
	# 			UserName=new_user
	# 		)
	# 	except ClientError as e:
	# 		if e.response['Error']['Code'] == 'EntityAlreadyExists':
	# 			print('[ERROR] El usuario ya existe')
	# 		else:
	# 			print('[ERROR] Error inesperado: %s' % e) 

	# 	print('[INFO]Usuario creado correctamente en '+stage+':')
	# 	assign_groups(iam,stage,rol_user,new_user,caso_de_uso)
	# 	create_credentials(new_user,iam,rol_user)

	# 	emails_smtp.send_email1(user,password,address,new_user,stage)

	# 	emails_smtp.send_email2(user,password,address,new_user,stage)
	# if accounts[3] == 1:
	# 	#Se crea cuenta en opt
	# 	stage = 'opt'
	# 	role_arn = 'arn:aws:iam::416481324865:role/pro-opt-delegated-jenkins'
	# 	iam=aws_connection(role_arn)

	# 	try:
	# 		response = iam.create_user(
	# 			UserName=new_user
	# 		)
	# 	except ClientError as e:
	# 		if e.response['Error']['Code'] == 'EntityAlreadyExists':
	# 			print('[ERROR] El usuario ya existe')
	# 		else:
	# 			print('[ERROR] Error inesperado: %s' % e) 

	# 	print('[INFO]Usuario creado correctamente en '+stage+':')
	# 	assign_groups(iam,stage,rol_user,new_user,caso_de_uso)
	# 	create_credentials(new_user,iam,rol_user)

	# 	emails_smtp.send_email1(user,password,address,new_user,stage)

	# 	emails_smtp.send_email2(user,password,address,new_user,stage)
	# 	