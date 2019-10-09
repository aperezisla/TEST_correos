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
from envio_smtp import Mensaje

def get_name(newuser):
	real=''
	for i in newuser:
		if(i == '.'):
			break
		else:
			real += i
	real=real[0].upper() + real[1:]
	return(real)

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
	#El responsable de area no incluye acceso a la consola, solo se crea el par de access key
	if rol_str != 'Responsable_De_Area_Usuaria': 
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

	response = iam.create_access_key(
		UserName=newuser,
	)

	data = response['AccessKey']
	data.pop('Status')
	data.pop('CreateDate')

	if rol_str != 'Responsable_De_Area_Usuaria':
		data['Password'] = contrasena
	data['ConsoleLoginLink']='https://'+consoleLogin+'.signin.aws.amazon.com/console'
	with open('credentials.csv','w') as f:
		f.write("%s,%s\n"%('UserName',data['UserName']))
		if rol_str != 'Responsable_De_Area_Usuaria':
			f.write("%s,%s\n"%('Password',data['Password']))
		f.write("%s,%s\n"%('AccessKeyId',data['AccessKeyId']))
		f.write("%s,%s\n"%('SecretAccessKey',data['SecretAccessKey']))
		f.write("%s,%s\n"%('ConsoleLoginLink',data['ConsoleLoginLink']))


def assign_basicforce(iam,newuser):
	response = iam.add_user_to_group(
		GroupName='BasicIAM',
		UserName=newuser
	)

	response = iam.add_user_to_group(
		GroupName='ForceMFA',
		UserName=newuser
	)

def assign_specific_group(group,iam,newuser):
	response=iam.add_user_to_group(
		GroupName=group,
		UserName=newuser
	)

def assign_specific_policy(policy,iam,newuser):
	response=iam.attach_user_policy(
		UserName=newuser,
		PolicyArn=policy
	)


def assign_groups(iam,cuenta,rol_str,newuser,mis_casos):
	if rol_str == 'Desarrollador_Global':
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
				if caso == 'PLEXT_TOA':
					assign_specific_group('NaDevPlantaExternaTOA',iam,newuser)
					print('[INFO] Asignado el grupo NaDevPlantaExternaTOA en su usuario dev')
				if caso == 'PLEXT_ASSIA':
					assign_specific_group('NaDevPlantaExternaAssia',iam,newuser)
					print('[INFO] Asignado el grupo NaDevPlantaExternaAssia en su usuario dev')
				if caso == 'PLEXT_HADA':
					assign_specific_group('NaDevPlantaExternaHada',iam,newuser)
					print('[INFO] Asignado el grupo NaDevPlantaExternaHada en su usuario dev')
			if cuenta == 'pro':
				if caso == 'PLEXT':
					assign_specific_group('NaDevPlantaExternaAssia',iam,newuser)
					assign_specific_group('NaDevPlantaExternaHada',iam,newuser)
					assign_specific_group('NaDevPlantaExternaTOA',iam,newuser)
					print('[INFO] Asignados los grupos NaDevPlantaExternaAssia, Hada y TOA en su usuario pro')
	if rol_str == 'Desarrollador_Avanzado_De_Tableau':
		assign_basicforce(iam,newuser)
		print('[INFO] Asignados los grupos BasicIAM y ForceMFA')
		for caso in mis_casos:
			if cuenta == 'dev':
				if caso == 'PLEXT_TOA':
					assign_specific_group('NaDevTableauPlantaExternaTOA',iam,newuser)
					print('[INFO] Asignado el grupo NaDevTableauPlantaExternaTOA en su usuario dev')
				if caso == 'PLEXT_ASSIA':
					assign_specific_group('NaDevTableauPlantaExternaASSIA',iam,newuser)
					print('[INFO] Asignado el grupo NaDevTableauPlantaExternaASSIA en su usuario dev')
				if caso == 'PLEXT_HADA':
					assign_specific_group('NaDevTableauPlantaExternaHADA',iam,newuser)
					print('[INFO] Asignado el grupo NaDevTableauPlantaExternaHADA en su usuario dev')
				if caso == 'ASTRO':
					assign_specific_group('NaDevTableauPlantaInternaASTRO',iam,newuser)
					print('[INFO] Asignado el grupo NaDevTableauPlantaInternaASTRO en su usuario dev')
				if caso == 'VIDEO_Y_PLATAFORMAS':
					assign_specific_group('NaDevTableauOpsPlatGlob',iam,newuser)
					print('[INFO] Asignado el grupo NaDevTableauOpsPlatGlob en su usuario dev')
			if cuenta == 'pro':
				if caso == 'PLEXT_TOA':
					assign_specific_group('NaDevTableauPlantaExternaTOA',iam,newuser)
					print('[INFO] Asignado el grupo NaDevTableauPlantaExternaTOA en su usuario pro')
				if caso == 'PLEXT_ASSIA':
					assign_specific_group('NaDevTableauPlantaExternaASSIA',iam,newuser)
					print('[INFO] Asignado el grupo NaDevTableauPlantaExternaASSIA en su usuario pro')
				if caso == 'PLEXT_HADA':
					assign_specific_group('NaDevTableauPlantaExternaHADA',iam,newuser)
					print('[INFO] Asignado el grupo NaDevTableauPlantaExternaHADA en su usuario pro')
				if caso == 'ASTRO':
					assign_specific_group('NaDevTableauPlantaInternaASTRO',iam,newuser)
					print('[INFO] Asignado el grupo NaDevTableauPlantaInternaASTRO en su usuario pro')
				if caso == 'VIDEO_Y_PLATAFORMAS':
					assign_specific_group('NaDevTableauOpsPlatGlob',iam,newuser)
					print('[INFO] Asignado el grupo NaDevTableauOpsPlatGlob en su usuario pro')
	if rol_str == 'Responsable_De_Area_Usuaria':
		assign_basicforce(iam,newuser)
		print('[INFO] Asignados los grupos BasicIAM y ForceMFA')
	if rol_str == 'Engineering':
		assign_basicforce(iam,newuser)
		print('[INFO] Asignados los grupos BasicIAM y ForceMFA')
	if rol_str == 'Engineering_Manager':
		assign_basicforce(iam,newuser)
		print('[INFO] Asignados los grupos BasicIAM y ForceMFA')

def assign_role_arn(accounts,user,password,address,newuser,rol_str,mis_casos,entornos):
	for cuenta in accounts:
		print(accounts)
		nombre_entorno=entornos[cuenta][0]
		role_arn=entornos[cuenta][1]
		consoleLogin=entornos[cuenta][2]

		iam=aws_connection(role_arn)

		try:
			response=iam.create_user(
				UserName=newuser
			)
		except ClientError as e:
			if e.response['Error']['Code'] == 'EntityAlreadyExists':
				print('[ERROR] El usuario ya existe')
				print('[INFO] Compruebo que el usuario esté en los grupos correspondientes')
				assign_groups(iam,cuenta,rol_str,newuser,mis_casos)
				print('[INFO] Se ha asignado los grupos a los que no estaba anteriormente')
				print('[INFO] No se envía email al ya tener usuario')
				#Si es la ultima cuenta, salir del programa, sino pasar al siguiente paso
				if (len(accounts) == 1):
					print('[INFO] Finalizado con éxito')
					sys.exit()
				else:
					accounts.remove(cuenta)
					print('BORRO Y PASO A LA SIGUIENTE CUENTA')
					continue
			else:
				print('[ERROR] Error inesperado: %s' % e)

		print('[INFO]Usuario creado correctamente en '+cuenta+':')
		assign_groups(iam,cuenta,rol_str,newuser,mis_casos)
		create_credentials(newuser,iam,rol_str,consoleLogin)

		x=Mensaje(user,password,address,newuser,cuenta,nombre_entorno,consoleLogin)
		msg1 = x.mail1()
		x.envio(msg1)
		print('[INFO] El primer mail se ha mandado correctamente')
		msg2 = x.mail2()
		x.envio(msg2)
		print('[INFO] El mail con las credenciales se ha mandado correctamente')
		#Elimino la cuenta en la que se ha creado el usuario
		accounts.remove(cuenta)
		print('elimino la cuenta'+cuenta)
		print(accounts)