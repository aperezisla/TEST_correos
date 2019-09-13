import boto3
import smtplib
import email.utils
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import jinja2
import os
#Cojo los credenciales
#Hacer funcion para coger esos parámetros
import sys
user=sys.argv[2]
password=sys.argv[4]
address=sys.argv[6]
#cc=sys.argv[8]
#print("user",user)
#print("pass",password)
#print(sys.argv[5])

print("Antes de la funcion")

def mandarcorreonormal(user,password,address,cc):
	print("Al principio de la funcion")
	recipients = None
	#Cambiar valores por los mios propios
	#server = smtplib.SMTP(host='host_address', port=your_port)
	#Cambiar el sender cuando me salgan las pruebas a no reply
	sender_email='no-reply@na.telefonicadev.com'
	sender_name='NA-Pruebas'
	#user es el usuario para poder usar smtp
	user=user
	password=password

	msg = MIMEMultipart()

	message = "mensaje de prueba"

	#Parametros
	password = password
	msg['From'] = "no-reply@na.telefonicadev.com"
	#msg['From'] = email.utils.formataddr((sender_name,sender_email))
	msg['To'] = "andrea.perezisla.practicas@telefonica.com"
	#msg['To'] = ','.join(address)
	msg['Subject'] = "Acceso a AWS Network Analytics entorno de ....."

	if cc is not None:
		msg['cc']=','.join(cc)
		recipients = address + cc
	else:
		recipients = address

	msg.attach(MIMEText(message,'plain','UTF-8'))
	#msg.attach(MIMEText(message,'html','UTF-8'))

	try:
		smtp_host = "email-smtp.eu-west-1.amazonaws.com"
		smtp_port = 587
		server = smtplib.SMTP_SSL("email-smtp.eu-west-1.amazonaws.com")
		server.set_debuglevel(1)
		#server.ehlo()
		#server.starttls()
		#server.ehlo()
		server.login(user,password)
		server.sendmail(msg['From'],msg['To'],msg.as_string())
		#server.close()
		server.quit()
		print('Email Sent!')
	except Exception as e:
		print("Error: ",e)

mandarcorreonormal(user,password,address,'copi')