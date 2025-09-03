from django.shortcuts import render
from appConvocatoriasSena.models import Convocatoria, TipoConvocatoria
from django.db import Error, transaction
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
# para correo
from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.template.loader import get_template
from smtplib import SMTPException

#para autenticarse al iniciar la sesión
from django.contrib.auth import authenticate
from django.contrib import auth

#librerias para generar password
import string
import random

# Create your views here.
def home(request):
    return  "Bienvenidos"


def enviarCorreo(asunto=None, mensaje=None, destinatario=None, archivo=None):
    remitente = settings.EMAIL_HOST_USER
    template = get_template('enviarCorreo.html')
    contenido = template.render({
        'mensaje': mensaje,
    })
    try:
        correo = EmailMultiAlternatives(
            asunto, mensaje, remitente, destinatario)
        correo.attach_alternative(contenido, 'text/html')
        if archivo != None:
            correo.attach_file(archivo)
        correo.send(fail_silently=True)
    except SMTPException as error:
        print(error)
        
def generar_password(longitud=12):
    caracteres = string.ascii_letters + string.digits + string.punctuation
    return ''.join(random.choice(caracteres) for _ in range(longitud))

@csrf_exempt
def login(request):    
    if(request.method=='POST'):
        try:
            username = request.POST["txtUser"]
            password = request.POST["txtPassword"]
            user = authenticate(username=username, password=password)
            if user is not None:
                # registrar la variable de sesión user
                auth.login(request, user)
                if user.usuRol=="Lider":
                    mensaje=f"Usuario {user.username} con rol de Líder ha iniciado la sesión"                  
                elif(user.usuRol=="Funcionario"):
                    mensaje=f"Usuario {user.username} con rol de Funcionario ha iniciado la sesión"    
                else:
                    mensaje=f"Usuario {user.username} con rol de Aprendiz ha iniciado la sesión"      
            else:
                mensaje = "Usuario o Contraseña Incorrectas"
        except Exception as error:
                mensaje = str(error)
               
        retorno = {"mensaje":mensaje}
    
        return JsonResponse(retorno)
    

def salir(request):
    auth.logout(request)
    return render(request, "frmIniciarSesion.html",
                  {"mensaje": "Ha cerrado la sesión"})