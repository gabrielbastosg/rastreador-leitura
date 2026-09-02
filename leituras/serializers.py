from rest_framework import serializers
from .models import Obra, Leitura

class ObraSerializer(serializers.ModelSerializer):
    class Meta:
        model = Obra
        fields = '__all__'

class LeituraSerializer(serializers.ModelSerializer):
    obra_titulo = serializers.CharField(source='obra.titulo', read_only=True)
    class Meta:
        model = Leitura
        fields = ['id', 'obra', 'obra_titulo', 'capitulo_atual', 'status',
                  'nota', 'criado_em', 'atualizado_em', 'encerrado_em']