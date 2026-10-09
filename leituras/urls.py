from django.urls import path

from . import views

urlpatterns = [
    path('', views.lista_leituras, name='lista-leituras'),
    path('leituras/<int:pk>/mover/', views.mover_capitulo, name='mover-capitulo'),
    path('obras/nova/', views.nova_obra, name='nova-obra'),
    path('leituras/<int:pk>/editar/', views.editar_leitura, name='editar-leitura'),
    path('leituras/<int:pk>/excluir/', views.excluir_leitura, name='excluir-leitura'),
    path('leituras/<int:pk>/status/',views.mudar_status, name='mudar-status'),  
]