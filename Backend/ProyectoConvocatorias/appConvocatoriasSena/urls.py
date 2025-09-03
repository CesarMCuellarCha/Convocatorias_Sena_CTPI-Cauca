from django.contrib import admin
from django.urls import path
from . import viewsLider, views, viewsAprendiz

urlpatterns = [
    path('', views.home),
    path('addConvocatoria/', viewsLider.addConvocatoria),
    path('addFuncionario/', viewsLider.addFuncionario),    
    path('addAprendiz/', viewsAprendiz.addAprendiz),
    path('postulacion/', viewsAprendiz.postulacion),
    path('login/', views.login),    
]

