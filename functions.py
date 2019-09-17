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

def create_credentials(new_user):
	#aqui creo la password
	contrasena = functions.generateSecureRandomString(12)

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
