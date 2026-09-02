from django.contrib import admin
from .models import Obra, Leitura
# Register your models here.

@admin.register(Obra)
class ObraAdmin(admin.ModelAdmin):
    list_display = ['titulo','tipo', 'autor', 'plataforma','total_capitulos']
    search_fields = ['titulo', 'autor']
    list_filter = ['tipo', 'plataforma']

@admin.register(Leitura)
class LeituraAdmin(admin.ModelAdmin):
    list_display = ['obra', 'capitulo_atual', 'status', 'nota', 'atualizado_em']
    list_filter = ['status','obra__tipo','obra__plataforma']