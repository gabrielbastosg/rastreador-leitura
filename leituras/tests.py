from django.test import TestCase
from .models import Obra,Leitura
from django.core.exceptions import ValidationError
# Create your tests here.

class ObraModelTestCase(TestCase):
        def test_grupo_de_manhwa_e_quadrinhos(self):
            obra = Obra.objects.create(tipo='Manhwa', titulo='Teste', autor='Autor', plataforma='Plataforma')
            self.assertEqual(obra.grupo,'Quadrinhos')

        def test_grupo_de_tipos_desconhecidos_e_outros(self):
            obra = Obra.objects.create(tipo='Podcast',titulo='Teste', autor='Autor', plataforma='Plataforma')
            self.assertEqual(obra.grupo,'Outros')


class LeituraModelTestCase(TestCase):
    def test_capitulo_acima_total_e_recusado(self):
        obra = Obra.objects.create(tipo='Manga',titulo='Numero1',autor='autor',plataforma='Plataforma',total_capitulos=10)
        leitura = Leitura(obra=obra, capitulo_atual=15, status='Lendo')
        with self.assertRaises(ValidationError) as cm:
            leitura.full_clean()
        self.assertIn('capitulo_atual', cm.exception.message_dict)

    def test_obra_sem_total_aceita_qualquer_capitulo(self):
        obra = Obra.objects.create(tipo='Manga',titulo='Numero1',autor='autor',plataforma='Plataforma')
        leitura = Leitura(obra=obra, capitulo_atual=999, status='Lendo')
        leitura.full_clean()  # não deve levantar exceção

    def test_capitulo_igual_ao_total_aceito(self):
        obra = Obra.objects.create(tipo='Manga',titulo='Numero1',autor='autor',plataforma='Plataforma',total_capitulos=10)
        leitura = Leitura(obra=obra, capitulo_atual=10, status='Lendo')
        leitura.full_clean()  # não deve levantar exceção