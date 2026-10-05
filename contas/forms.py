from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm


class CadastroForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = get_user_model()
        fields = ['username']


    def validate_password_for_user(self, user, **kwargs):
        super().validate_password_for_user(user, password_field_name='password1',**kwargs)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].help_text = ''
        self.fields['password1'].help_text = 'Mínimo de 8 caracteres, e deve conter pelo menos uma letra.'
        self.fields['password2'].help_text = ''

