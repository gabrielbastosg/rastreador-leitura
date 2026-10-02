from django.core.exceptions import ValidationError



class ExigeLetraValidator:
    def validate(self, password, user=None):
        if not any(caractere.isalpha() for caractere in password):
            raise ValidationError(
                "A senha deve conter pelo menos uma letra.",
                code='senha_sem_letra',
            )
        
    def get_help_text(self):
        return "A senha deve conter pelo menos uma letra."
