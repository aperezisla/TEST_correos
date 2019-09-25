
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
		self.msg = MIMEMultipart('alternative')
		self.sender='no-reply@na.telefonicadev.com'
		self.sender_name='na-engineering'
		self.smtp_host='email-smtp.eu-west-1.amazonaws.com'
		self.smtp_port=587
		self.nombre=functions.get_name(newuser)
		#COMPROBAR QUE ESTO ESTA BIEN
		self.msg['From'] = email.utils.formataddr((sender_name,sender))

	def mail1(self):
		#meter aqui el subject
		self.msg['Subject']='Acceso a AWS Network Analytics entorno de '+self.nombre_entorno
		#CAMBIAR ESTO! Lleva copia a na
		self.cc=['andreap.isla97@gmail.com']
		self.emails=[self.address] + self.cc
		#self.msg['To']=self.address
		self.message_template = functions.read_template('mensaje1.txt')
		self.message = self.message_template.safe_substitute(name=nombre,entorno=cuenta, loginurl=consoleLogin,user_name=newuser)
		self.msg.attach(MIMEText(message,'plain'))



	def mail2(self):
		#meter aqui el subject
		self.msg['Subject']='Credenciales AWS Network Analytics entorno '+self.cuenta
		self.emails=[self.address]
		self.message_template = functions.read_template('mensaje2.txt')
		self.message=self.message_template.safe_substitute(name=nombre)
		self.msg.attach(MIMEText(message,'plain'))

		self.mail_file=MIMEBase('application','csv')
		self.mail_file.set_payload(open('credentials.csv','r').read())
		self.mail_file.add_header('Content-Disposition','attachment',filename='credentials.csv')
		encoders.encode_base64(self.mail_file)
		self.msg.attach(self.mail_file)


	def envio(self):
		try:
			server = smtplib.SMTP(self.smtp_host,self.smtp_port)
			server.ehlo()
			server.starttls()
			server.ehlo()
			server.login(self.user,self.password)
			server.sendmail(self.sender,self.emails,self.msg.as_string())
			server.close()
		except Exception as e:
			print("Error: ", e)



