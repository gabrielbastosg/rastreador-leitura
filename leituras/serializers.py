from django.core.exceptions import ValidationError as ErroDeValidacaoDjango
from rest_framework import serializers
from .models import Obra, Leitura

class ObraSerializer(serializers.ModelSerializer):
    dono = serializers.HiddenField(default=serializers.CurrentUserDefault())
    class Meta:
        model = Obra
        fields = '__all__'

class LeituraSerializer(serializers.ModelSerializer):
    obra_titulo = serializers.CharField(source='obra.titulo', read_only=True)
    class Meta:
        model = Leitura
        fields = ['id', 'obra', 'obra_titulo', 'capitulo_atual', 'status',
                  'nota', 'criado_em', 'atualizado_em', 'encerrado_em']

    def get_fields(self):
        # O menu da API navegavel desenha o queryset do campo. Sem filtrar
        # aqui, ele lista o titulo de todo mundo mesmo sem deixar gravar.
        campos = super().get_fields()
        request = self.context.get('request')
        if request is not None:
            campos['obra'].queryset = Obra.objects.filter(dono=request.user)
        return campos

    def validate_obra(self, obra):
        if obra.dono != self.context['request'].user:
            raise serializers.ValidationError('Essa obra não é sua.')
        return obra
        
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
