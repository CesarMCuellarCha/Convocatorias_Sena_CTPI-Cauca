from django.shortcuts import render
from appConvocatoriasSena.models import Convocatoria, Postulacion, Usuario, Aprendiz
from django.db import Error, transaction
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from datetime import datetime
from appConvocatoriasSena.views import generar_password, enviarCorreo
import threading #para crear hilos

#formato para fecha y hora
formato_fecha = '%Y/%m/%d %H:%M:%S'

@csrf_exempt
def addAprendiz(request):
    try:
        if request.method=='POST':
            identificacion = request.POST['txtIdentificacion']
            nombres = request.POST['txtNombres']
            apellidos = request.POST['txtApellidos']
            correo = request.POST['txtCorreo']
            ficha = request.POST['txtFicha']
            programa = request.POST['txtPrograma']
            
            with transaction.atomic():
                usuario = Usuario(usuIdentificacion=identificacion,
                                first_name=nombres, last_name=apellidos,
                                email=correo, usuRol="Aprendiz",
                                username=correo)
                usuario.save()
                usuario.is_active=True
                #generar el password
                passwordGenerado=generar_password()
                usuario.set_password(passwordGenerado)
                usuario.save()
                #ahora creamos el objeto funcionario
                aprendiz = Aprendiz(aprFicha=ficha,
                                    aprPrograma = programa,
                                    aprUsuario=usuario)
                aprendiz.save()
                #enviar correo al aprendiz con datos de ingreso.   
                asunto="Registro de Usuario en el Sistema" 
                mensajeCorreo=f"Cordial saludo Aprendiz <b>{nombres} {apellidos}</b>, usted ha sido registrado \
                    en el Sistema De Gestión de Convocatorias para aprendices del CTPI-SENA-CAUCA.\
                   <br><br>Nos permitimos enviar las credenciales de ingreso al sistema: <br><br>\
                    <b>Username:</b> {correo}<br>\
                    <b>Password:</b> {passwordGenerado}<br><br>\
                    La url del sistema es : http://127.0.0.1:8000"   
                # crear el hilo para el envío del correo
                thread = threading.Thread(
                    target=enviarCorreo, args=(asunto, mensajeCorreo, [correo], None))
                # ejecutar el hilo
                thread.start()
            mensaje="Aprendiz Agregado Correctamente..."
        else:
            mensaje="No permitido"        
    except Error as error:
        transaction.rollback()
        mensaje = error
        
    retorno = {"mensaje":mensaje, "username": correo, "password": passwordGenerado}    
    return JsonResponse(retorno)


@csrf_exempt
def postulacion(request):
    try:
        if request.method=='POST':
            #por ahora sumimos que es el aprendiz con id=1
            convocatoria = Convocatoria.objects.get(pk=1)
            aprendiz = Aprendiz.objects.get(pk=1)
            
            with transaction.atomic():
                postulacion = Postulacion(posAprendiz=aprendiz,
                                          posConvocatoria=convocatoria)                
                postulacion.save()             
                #enviar correo sobre la postulación al aprendiz  
                asunto="Postulación Convocatorias Bienestar Aprendices" 
                mensajeCorreo=f"Cordial saludo Aprendiz <b>{aprendiz.aprUsuario.first_name} \
                    {aprendiz.aprUsuario.last_name}</b>, nos permitimos confirmar su postulación \
                    a la convocatoria de nombre: <b>{convocatoria.conNombre.upper()}</b>.\
                   <br><br>Le recordamos estar pendiente de los resultados." 
                # crear el hilo para el envío del correo
                thread = threading.Thread(
                    target=enviarCorreo, args=(asunto, mensajeCorreo, [aprendiz.aprUsuario.email], None))
                # ejecutar el hilo
                thread.start()
            mensaje="Postulación Registrada Satisfactoriamente"
        else:
            mensaje="No permitido"       
        
    except Error as error:
        transaction.rollback()
        mensaje = error
        
    retorno = {"mensaje":mensaje}    
    return JsonResponse(retorno)
    