from django.test import TestCase
from .models import Obra,Leitura
from django.core.exceptions import ValidationError
from django.urls import reverse
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

    def test_estrelas_sem_nota_e_vazio(self):
        leitura = Leitura(nota=None)
        self.assertEqual(leitura.estrelas, '')
              
    def test_estrelas_com_nota_tres_estrelas(self):
        leitura = Leitura(nota=3)
        self.assertEqual(leitura.estrelas, '★★★☆☆')
    
    def test_estrelas_com_nota_cinco_estrelas(self):
        leitura = Leitura(nota=5)
        self.assertEqual(leitura.estrelas, '★★★★★')


class MoverCapituloTestCase(TestCase):
    def test_passo_1_avanca_capitulo(self):
        obra= Obra.objects.create(tipo='Manga',titulo='Numero1',autor='autor',plataforma='Plataforma',total_capitulos=10)
        leitura = Leitura.objects.create(obra=obra, capitulo_atual=3, status='Lendo')
        self.client.post(reverse('mover-capitulo', args=[leitura.pk]), {'passo': '1'})
        leitura.refresh_from_db()
        self.assertEqual(leitura.capitulo_atual, 4)

    
    def test_chegar_no_total_finaliza_a_leitura(self):
        obra = Obra.objects.create(tipo='Manga',titulo='Numero1',autor='autor',plataforma='Plataforma',total_capitulos=10)
        leitura = Leitura.objects.create(obra=obra, capitulo_atual=9, status='Lendo')
        self.client.post(reverse('mover-capitulo', args=[leitura.pk]), {'passo': '1'})
        leitura.refresh_from_db()
        self.assertEqual(leitura.capitulo_atual, 10)
        self.assertEqual(leitura.status, 'Finalizado')
        self.assertIsNotNone(leitura.encerrado_em)

    def test_nao_passar_do_total(self):
        obra = Obra.objects.create(tipo='Manga',titulo='Numero1',autor='autor',plataforma='Plataforma',total_capitulos=10)
        leitura = Leitura.objects.create(obra=obra, capitulo_atual=10, status='Lendo')
        self.client.post(reverse('mover-capitulo', args=[leitura.pk]), {'passo': '1'})
        leitura.refresh_from_db()
        self.assertEqual(leitura.capitulo_atual, 10)  # não mudou

    
    def test_nao_desce_abaixo_de_zero(self):
        obra = Obra.objects.create(tipo='Manga',titulo='Numero1',autor='autor',plataforma='Plataforma',total_capitulos=10)
        leitura = Leitura.objects.create(obra=obra, capitulo_atual=0, status='Lendo')
        self.client.post(reverse('mover-capitulo', args=[leitura.pk]), {'passo': '-1'})
        leitura.refresh_from_db()
        self.assertEqual(leitura.capitulo_atual, 0)  # não mudou

    
    def test_get_devolve_405(self):
        obra = Obra.objects.create(tipo='Manga',titulo='Numero1',autor='autor',plataforma='Plataforma',total_capitulos=10)
        leitura = Leitura.objects.create(obra=obra, capitulo_atual=5, status='Lendo')
        resposta = self.client.get(reverse('mover-capitulo', args=[leitura.pk]))
        self.assertEqual(resposta.status_code, 405)  # Method Not Allowed



class NovaObraTestCase(TestCase):
    def test_post_valido_cria_obra_e_leitura(self):
        resposta = self.client.post(reverse('nova-obra'), {
            'tipo': 'Manga',
            'titulo': 'Nova Obra',
            'autor': 'Autor',
            'plataforma': 'Plataforma',
            'total_capitulos': 10,
            'capitulo_atual': 1,
            'status': 'Lendo',
        })
        self.assertEqual(Obra.objects.count(), 1)
        self.assertEqual(Leitura.objects.count(), 1)
        leitura = Leitura.objects.get()
        self.assertEqual(leitura.obra.titulo, 'Nova Obra')
        self.assertRedirects(resposta, reverse('lista-leituras'))  # redireciona para a lista de leituras

            
    def test_erro_nos_dois_formularios_volta_com_os_dois_erros(self):
        resposta = self.client.post(reverse('nova-obra'),{
            'tipo': 'Manga',
            'titulo': '',
            'autor': 'Autor',
            'plataforma': 'Plataforma',
            'nota': 9,
            'total_capitulos': 10,
            'capitulo_atual': 1,
            'status': 'Lendo',
        })
        self.assertEqual(Obra.objects.count(), 0)
        self.assertEqual(Leitura.objects.count(), 0)
        self.assertEqual(resposta.status_code, 200)
        self.assertIn('titulo', resposta.context['form_obra'].errors) 
        self.assertIn('nota', resposta.context['form_leitura'].errors)

    
    def test_capitulo_acima_do_total_nao_cria_nem_a_obra(self):
        resposta = self.client.post(reverse('nova-obra'), {
            'tipo': 'Manga',
            'titulo': 'Nova Obra',
            'autor': 'Autor',
            'plataforma': 'Plataforma',
            'total_capitulos': 10,
            'capitulo_atual': 15,
            'status': 'Lendo',
        })

        self.assertEqual(Obra.objects.count(), 0)
        self.assertEqual(Leitura.objects.count(), 0)
        self.assertEqual(resposta.status_code, 200)
        self.assertIn('capitulo_atual', resposta.context['form_leitura'].errors)

class EditarLeituraTestCase(TestCase):
    def test_muda_total_e_capitulo_no_mesmo_post(self):
        obra = Obra.objects.create(tipo='Manga',titulo='Numero1',autor='autor',plataforma='plataforma', total_capitulos=10)
        leitura = Leitura.objects.create(obra=obra,status='Lendo',capitulo_atual=5)
        resposta = self.client.post(reverse('editar-leitura', args=[leitura.pk]), {
            'tipo': 'Manga',
            'titulo': 'Numero1',
            'autor': 'autor',
            'plataforma': 'plataforma',
            'total_capitulos': 30,
            'capitulo_atual': 25,
            'status': 'Lendo',
        })
        obra.refresh_from_db()
        leitura.refresh_from_db()
        self.assertEqual(obra.total_capitulos, 30)
        self.assertEqual(leitura.capitulo_atual, 25)
        self.assertRedirects(resposta, reverse('lista-leituras'))