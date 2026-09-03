from django import forms
from .models import Leitura, Obra

class ObraForm(forms.ModelForm):
    class Meta:
        model = Obra
        fields = ['titulo', 'autor', 'tipo', 'plataforma', 'link', 'total_capitulos']
        labels = {
            'total_capitulos': 'Total de capítulos',
        }
        help_texts = {
            'total_capitulos': 'Deixe vazio se ainda está em andamento.',
        }
        widgets = {
            'titulo': forms.TextInput(attrs={'placeholder': 'The Primal Hero // Shield Hero x Male! Reader'}),
            'autor': forms.TextInput(attrs={'placeholder': 'souleater26'}),
            'plataforma': forms.TextInput(attrs={'placeholder': 'Wattpad'}),
            'link': forms.URLInput(attrs={'placeholder': 'https://www.wattpad.com/story/...'}),
        }

class LeituraForm(forms.ModelForm):
    class Meta:
        model = Leitura
        fields = ['capitulo_atual', 'status', 'nota']
        labels = {
            'capitulo_atual': 'Capítulo atual',
        }
        help_texts = {
            'nota': 'De 1 a 5. Pode deixar vazio e dar depois.',
        }