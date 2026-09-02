from django.core.exceptions import ValidationError as ErroDeValidacaoDjango
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

    def validate(self, attrs):
        # O DRF nao chama full_clean() sozinho. Sem isto, a regra do
        # capitulo valeria no admin e a API deixaria passar.
        dados = {}
        for campo in ('obra', 'capitulo_atual'):
            if self.instance is not None:
                dados[campo] = getattr(self.instance, campo)
            if campo in attrs:
                dados[campo] = attrs[campo]
        try:
            Leitura(**dados).clean()
        except ErroDeValidacaoDjango as erro:
            raise serializers.ValidationError(erro.message_dict)
        return attrs
