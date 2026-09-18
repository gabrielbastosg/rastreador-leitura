from django.test import TestCase
from .models import Obra,Leitura
from django.core.exceptions import ValidationError
from django.urls import reverse
from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase
# Create your tests here.

class ObraModelTestCase(TestCase):
    def setUp(self):
        self.usuario = get_user_model().objects.create_user(
            username='leitor', password='senha123'
        )

    def test_grupo_de_manhwa_e_quadrinhos(self):
        obra = Obra.objects.create(dono=self.usuario, tipo='Manhwa', titulo='Teste', autor='Autor', plataforma='Plataforma')
        self.assertEqual(obra.grupo,'Quadrinhos')

    def test_grupo_de_tipos_desconhecidos_e_outros(self):
        obra = Obra.objects.create(dono=self.usuario, tipo='Podcast',titulo='Teste', autor='Autor', plataforma='Plataforma')
        self.assertEqual(obra.grupo,'Outros')


class LeituraModelTestCase(TestCase):
    def setUp(self):
        self.usuario = get_user_model().objects.create_user(
            username='leitor', password='senha123'
            )

    def test_capitulo_acima_total_e_recusado(self):
        obra = Obra.objects.create(dono=self.usuario, tipo='Manga',titulo='Numero1',autor='autor',plataforma='Plataforma',total_capitulos=10)
        leitura = Leitura(obra=obra, capitulo_atual=15, status='Lendo')
        with self.assertRaises(ValidationError) as cm:
            leitura.full_clean()
        self.assertIn('capitulo_atual', cm.exception.message_dict)

    def test_obra_sem_total_aceita_qualquer_capitulo(self):
        obra = Obra.objects.create(dono=self.usuario,tipo='Manga',titulo='Numero1',autor='autor',plataforma='Plataforma')
        leitura = Leitura(obra=obra, capitulo_atual=999, status='Lendo')
        leitura.full_clean()  # não deve levantar exceção

    def test_capitulo_igual_ao_total_aceito(self):
        obra = Obra.objects.create(dono=self.usuario,tipo='Manga',titulo='Numero1',autor='autor',plataforma='Plataforma',total_capitulos=10)
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
    def setUp(self):
        self.usuario = get_user_model().objects.create_user(
            username='leitor', password='senha123'
        )
        self.client.force_login(self.usuario)

    def test_passo_1_avanca_capitulo(self):
        obra= Obra.objects.create(dono=self.usuario, tipo='Manga',titulo='Numero1',autor='autor',plataforma='Plataforma',total_capitulos=10)
        leitura = Leitura.objects.create(obra=obra, capitulo_atual=3, status='Lendo')
        self.client.post(reverse('mover-capitulo', args=[leitura.pk]), {'passo': '1'})
        leitura.refresh_from_db()
        self.assertEqual(leitura.capitulo_atual, 4)

    
    def test_chegar_no_total_finaliza_a_leitura(self):
        obra = Obra.objects.create(dono=self.usuario,tipo='Manga',titulo='Numero1',autor='autor',plataforma='Plataforma',total_capitulos=10)
        leitura = Leitura.objects.create(obra=obra, capitulo_atual=9, status='Lendo')
        self.client.post(reverse('mover-capitulo', args=[leitura.pk]), {'passo': '1'})
        leitura.refresh_from_db()
        self.assertEqual(leitura.capitulo_atual, 10)
        self.assertEqual(leitura.status, 'Finalizado')
        self.assertIsNotNone(leitura.encerrado_em)

    def test_nao_passar_do_total(self):
        obra = Obra.objects.create(dono=self.usuario,tipo='Manga',titulo='Numero1',autor='autor',plataforma='Plataforma',total_capitulos=10)
        leitura = Leitura.objects.create(obra=obra, capitulo_atual=10, status='Lendo')
        self.client.post(reverse('mover-capitulo', args=[leitura.pk]), {'passo': '1'})
        leitura.refresh_from_db()
        self.assertEqual(leitura.capitulo_atual, 10)  # não mudou

    
    def test_nao_desce_abaixo_de_zero(self):
        obra = Obra.objects.create(dono=self.usuario,tipo='Manga',titulo='Numero1',autor='autor',plataforma='Plataforma',total_capitulos=10)
        leitura = Leitura.objects.create(obra=obra, capitulo_atual=0, status='Lendo')
        self.client.post(reverse('mover-capitulo', args=[leitura.pk]), {'passo': '-1'})
        leitura.refresh_from_db()
        self.assertEqual(leitura.capitulo_atual, 0)  # não mudou

    
    def test_get_devolve_405(self):
        obra = Obra.objects.create(dono=self.usuario,tipo='Manga',titulo='Numero1',autor='autor',plataforma='Plataforma',total_capitulos=10)
        leitura = Leitura.objects.create(obra=obra, capitulo_atual=5, status='Lendo')
        resposta = self.client.get(reverse('mover-capitulo', args=[leitura.pk]))
        self.assertEqual(resposta.status_code, 405)  # Method Not Allowed



class NovaObraTestCase(TestCase):
    def setUp(self):
        self.usuario = get_user_model().objects.create_user(
            username='leitor', password='senha123'
        )
        self.client.force_login(self.usuario)

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

    def test_link_repetido_nao_quebra_e_volta_com_erro(self):
        Obra.objects.create(
            dono=self.usuario, tipo='Fanfic', titulo='Primeira',
            autor='a', plataforma='Wattpad', link='https://exemplo.com/1',
        )
        resposta = self.client.post(reverse('nova-obra'), {
            'titulo': 'Segunda', 'autor': 'b', 'tipo': 'Fanfic',
            'plataforma': 'Wattpad', 'link': 'https://exemplo.com/1',
            'total_capitulos': '', 'capitulo_atual': '0',
            'status': 'Lendo', 'nota': '',
        })
        self.assertEqual(resposta.status_code, 200)
        self.assertEqual(Obra.objects.count(), 1)

class EditarLeituraTestCase(TestCase):
    def setUp(self):
        self.usuario = get_user_model().objects.create_user(
            username='leitor', password='senha123'
        )
        self.client.force_login(self.usuario)

    def test_muda_total_e_capitulo_no_mesmo_post(self):
        obra = Obra.objects.create(dono=self.usuario,tipo='Manga',titulo='Numero1',autor='autor',plataforma='plataforma', total_capitulos=10)
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

class IsolamentoTestCase(TestCase):
    def setUp(self):
        self.dono = get_user_model().objects.create_user(
            username='dono', password='senha123'
        )
        self.invasor = get_user_model().objects.create_user(
            username='invasor', password='senha123'
        )
        obra = Obra.objects.create(
            dono=self.dono, tipo='Manga', titulo='Numero1',
            autor='autor', plataforma='Plataforma', total_capitulos=10
        )
        self.leitura = Leitura.objects.create(
            obra=obra, capitulo_atual=5, status='Lendo'
        )
        self.client.force_login(self.invasor)

    def test_invasao_nao_edita_leitura_de_outro(self):
        resposta = self.client.post(
            reverse('editar-leitura', args=[self.leitura.pk]), {}
        )
        self.assertEqual(resposta.status_code, 404)

class ApiIsolamentoTestCase(APITestCase):
    def setUp(self):
        self.dono = get_user_model().objects.create_user(
            username='dono', password='senha123'
        )
        self.invasor = get_user_model().objects.create_user(
            username='invasor', password='senha123'
        )
        self.obra_do_dono = Obra.objects.create(
            dono=self.dono, tipo='Manga', titulo='Numero1',
            autor='autor', plataforma='Plataforma', total_capitulos=10
        )
        self.leitura_do_dono = Leitura.objects.create(
            obra=self.obra_do_dono, capitulo_atual=5, status='Lendo'
        )

    def test_sem_login_nao_lista_obra(self):
        resposta = self.client.get(reverse('obra-list'))
        self.assertEqual(resposta.status_code,403)

    def test_lista_traz_so_as_obras_do_dono(self):
        obra_do_invasor = Obra.objects.create(dono=self.invasor, tipo='Manga', titulo='Minha', autor='autor', plataforma='Plataforma')
        self.client.force_login(self.invasor)
        resposta = self.client.get(reverse('obra-list'))
        self.assertEqual(len(resposta.data), 1)
        self.assertEqual(resposta.data[0]['titulo'], 'Minha')
    
    def test_invasor_nao_apaga_obra_de_outro(self):
        self.client.force_login(self.invasor)
        resposta = self.client.delete(reverse('obra-detail',args=[self.obra_do_dono.pk]))
        self.assertEqual(resposta.status_code,404)
        self.assertTrue(Obra.objects.filter(pk=self.obra_do_dono.pk).exists())
    
    def test_dono_do_payload_e_ignorado(self):
        self.client.force_login(self.invasor)
        resposta = self.client.post(reverse('obra-list'), {
            'dono': self.dono.pk,
            'tipo': 'Manga',
            'titulo': 'No nome do outro',
            'autor': 'autor',
            'plataforma': 'Plataforma',
        })
        self.assertEqual(resposta.status_code, 201)
        obra = Obra.objects.get(titulo='No nome do outro')
        self.assertEqual(obra.dono, self.invasor)

    
    def test_nao_cria_leitura_na_obra_de_outro(self):
        self.client.force_login(self.invasor)
        resposta = self.client.post(reverse('leitura-list'), {
            'obra': self.obra_do_dono.pk,
            'capitulo_atual': 1,
            'status': 'Lendo',
        })
        self.assertEqual(resposta.status_code, 400)
        self.assertEqual(Leitura.objects.count(), 1)


    def test_menu_de_obras_nao_mostra_titulo_alheio(self):
        self.client.force_login(self.invasor)
        resposta = self.client.get(reverse('leitura-list'),HTTP_ACCEPT='text/html')
        self.assertNotContains(resposta, self.obra_do_dono.titulo)