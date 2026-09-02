from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator

# Create your models here.
class Obra(models.Model):
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

    def __str__(self):
        return f"{self.obra.titulo} - Capítulo {self.capitulo_atual} - Status: {self.status}"