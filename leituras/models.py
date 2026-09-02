from django.db import models
from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator, MaxValueValidator

# Create your models here.
class Obra(models.Model):
    TIPOS=[
        ('Fanfic','Fanfic'),
        ('Manga','Manga'),
        ('Manhwa','Manhwa'),
        ('Webtoon','Webtoon')
    ]
    tipo = models.CharField(max_length=20, choices=TIPOS,default='Fanfic')
    titulo = models.CharField(max_length=200)
    autor = models.CharField(max_length=200)
    plataforma = models.CharField(max_length=200)
    link = models.URLField(unique=True)
    total_capitulos = models.PositiveIntegerField(null=True, blank=True)

    def __str__(self):
        return self.titulo
    
class Leitura(models.Model):
    obra = models.ForeignKey(Obra, on_delete=models.CASCADE)
    capitulo_atual = models.PositiveIntegerField()
    status = models.CharField(max_length=20, choices=[('Lendo', 'Lendo'), ('Pausado', 'Pausado'), ('Finalizado', 'Finalizado'), ('Abandonado', 'Abandonado')])
    criado_em = models.DateTimeField(auto_now_add=True)
    encerrado_em = models.DateField(null=True, blank=True)
    atualizado_em = models.DateTimeField(auto_now=True)
    nota = models.PositiveSmallIntegerField(
        null=True, blank=True,
        validators=[MinValueValidator(1), MaxValueValidator(5)],
    )

    def clean(self):
        # obra_id em vez de obra: se a FK ainda nao foi preenchida, ler
        # self.obra estoura RelatedObjectDoesNotExist em vez de dar None.
        if not self.obra_id or self.capitulo_atual is None:
            return
        total = self.obra.total_capitulos
        if total is not None and self.capitulo_atual > total:
            raise ValidationError({
                'capitulo_atual': f'"{self.obra.titulo}" tem {total} capítulos — '
                                  f'não dá pra estar no {self.capitulo_atual}.'
            })

    @property
    def estrelas(self):
        if self.nota is None:
            return ''
        return '★' * self.nota + '☆' * (5 - self.nota)


    def __str__(self):
        return f"{self.obra.titulo} - Capítulo {self.capitulo_atual} - Status: {self.status}"
