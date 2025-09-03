from django.shortcuts import render
from appConvocatoriasSena.models import Convocatoria, TipoConvocatoria, Usuario, Funcionario
from django.db import Error, transaction
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from datetime import datetime
#para envío de correo y generar el password
from appConvocatoriasSena.views import generar_password, enviarCorreo
import threading #para crear hilos


#formato para fecha y hora
formato_fecha = '%Y/%m/%d %H:%M:%S'
# Create your views here.
@csrf_exempt
def addConvocatoria(request):
    try:
        nombre = request.POST['txtNombre']
        idTipo = request.POST["cbTipoConvocatoria"]
        tipo = TipoConvocatoria.objects.get(pk=idTipo)
        cantidadBeneficiarios = request.POST['txtCantidadBeneficiarios']     
        fechaInicio = request.POST['txtFechaInicio']
        fecha_inicio = datetime.strptime(fechaInicio, formato_fecha)
        fechaFinal = request.POST['txtFechaFinal']
        fecha_final = datetime.strptime(fechaFinal, formato_fecha)
        documento = request.FILES['fileDocumento']
        
        convocatoria = Convocatoria(conNombre = nombre,
                                    conTipo=tipo,
                                    conCantidadBeneficiarios=cantidadBeneficiarios,
                                    conFechaInicio=fecha_inicio,
                                    conFechaFinal=fecha_final,
                                    conDocumento=documento)
        convocatoria.save()
        mensaje="Convocatoria Agregada Correctamente"
    except Error as error:
        mensaje=str(error)
        
    retorno = {"mensaje":mensaje}
    
    return JsonResponse(retorno)


@csrf_exempt
def addFuncionario(request):
    try:
        if request.method=='POST':
            identificacion = request.POST['txtIdentificacion']
            nombres = request.POST['txtNombres']
            apellidos = request.POST['txtApellidos']
            correo = request.POST['txtCorreo']
            cargo = request.POST['txtCargo']
            
            with transaction.atomic():
                usuario = Usuario(usuIdentificacion=identificacion,
                                first_name=nombres, last_name=apellidos,
                                email=correo, usuRol="Funcionario",
                                username=correo)
                usuario.save()
                usuario.is_active=True
              
                passwordGenerado=generar_password()
                usuario.set_password(passwordGenerado)
                usuario.save()
                #ahora creamos el objeto funcionario
                funcionario = Funcionario(funCargo=cargo,
                                        funUsuario=usuario)
                funcionario.save()
                #enviar correo con datos de ingreso al funcionario 
                asunto="Registro de Usuario en el Sistema" 
                mensajeCorreo=f"Cordial saludo <b>{nombres} {apellidos}</b>, usted ha sido registrado \
                    en el Sistema De Gestión de Convocatorias para aprendices del CTPI-SENA-CAUCA.\
                   <br>Nos permitimos enviar las credenciales de ingreso al sistema: <br><br>\
                    <b>Username:</b> {correo}<br>\
                    <b>Password:</b> {passwordGenerado}<br><br>\
                    La url del sistema es : http://127.0.0.1:8000"   
                # crear el hilo para el envío del correo
                thread = threading.Thread(
                    target=enviarCorreo, args=(asunto, mensajeCorreo, [correo], None))
                # ejecutar el hilo
                thread.start()
            mensaje="Funcionario Agregado Correctamente..."
        else:
            mensaje="No permitido"       
        
    except Error as error:
        transaction.rollback()
        mensaje = error
        
    retorno = {"mensaje":mensaje, "username": correo, "password": passwordGenerado}
    
    return JsonResponse(retorno)
    
    
