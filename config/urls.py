"""
URL configuration for config project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from leituras.views import ObraViewSet, LeituraViewSet, lista_leituras, mover_capitulo,nova_obra,editar_leitura


router = DefaultRouter()
router.register('obras', ObraViewSet)
router.register('leituras', LeituraViewSet)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include(router.urls)),
    path('', lista_leituras, name='lista-leituras'),
    path('leituras/<int:pk>/mover/', mover_capitulo, name='mover-capitulo'),
    path('obras/nova/', nova_obra, name='nova-obra'),
    path('leituras/<int:pk>/editar/', editar_leitura, name='editar-leitura'),
]