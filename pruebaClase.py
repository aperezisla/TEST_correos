
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


class Mensaje:
	def __init__(self,user,password,address,newuser,cuenta,nombre_entorno,consoleLogin):
		self.user=user
		self.password=password
		self.address=address
		self.newuser=newuser
		self.cuenta=cuenta
		self.nombre_entorno=nombre_entorno
		self.consoleLogin=consoleLogin
		self.msg1 = MIMEMultipart('alternative')
		self.msg2 = MIMEMultipart('alternative')
		self.sender='no-reply@na.telefonicadev.com'
		self.sender_name='na-engineering'
		self.smtp_host='email-smtp.eu-west-1.amazonaws.com'
		self.smtp_port=587
		self.nombre=functions.get_name(newuser)
		#COMPROBAR QUE ESTO ESTA BIEN
		self.msg1['From'] = email.utils.formataddr((self.sender_name,self.sender))
		self.msg2['From'] = self.msg1['From']

	def envio(self,msg):
		try:
			server = smtplib.SMTP(self.smtp_host,self.smtp_port)
			server.ehlo()
			server.starttls()
			server.ehlo()
			server.login(self.user,self.password)
			server.sendmail(self.sender,self.emails,self.msg.as_string())
			self.msg['Subject']=None
			server.close()
		except Exception as e:
			print("Error: ", e)

	def mail1(self):
		#meter aqui el subject
		self.msg1['Subject']='Acceso a AWS Network Analytics entorno de '+self.nombre_entorno
		#CAMBIAR ESTO! Lleva copia a na
		self.cc=['andreap.isla97@gmail.com']
		self.emails=[self.address] + self.cc
		#self.msg['To']=self.address
		self.message_template = functions.read_template('mensaje1.txt')
		self.message = self.message_template.safe_substitute(name=self.nombre,entorno=self.cuenta, loginurl=self.consoleLogin,user_name=self.newuser)
		self.msg1.attach(MIMEText(self.message,'plain'))
		return self.msg1



	def mail2(self):
		#meter aqui el subject
		self.msg2['Subject']='Credenciales AWS Network Analytics entorno '+self.cuenta
		self.emails=[self.address]
		self.message_template = functions.read_template('mensaje2.txt')
		self.message=self.message_template.safe_substitute(name=self.nombre)
		self.msg2.attach(MIMEText(self.message,'plain'))

		self.mail_file=MIMEBase('application','csv')
		self.mail_file.set_payload(open('credentials.csv','r').read())
		self.mail_file.add_header('Content-Disposition','attachment',filename='credentials.csv')
		encoders.encode_base64(self.mail_file)
		self.msg2.attach(self.mail_file)
		return self.msg2

	


