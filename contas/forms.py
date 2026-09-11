from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm


class CadastroForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = get_user_model()
        fields = ['username']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].help_text = ''
        self.fields['password1'].help_text = 'Mínimo de 8 caracteres, e não pode ser só números.'
        self.fields['password2'].help_text = ''

