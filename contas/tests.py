from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model

# Create your tests here.


class CadastroTestCase(TestCase):
    def test_cadastro_cria_usuario_ja_loga(self):
        resposta = self.client.post(reverse('cadastro'),{
            'username':'novato',
            'password1':"senhaboa123",
            'password2':'senhaboa123',

        })
        self.assertRedirects(resposta,reverse('lista-leituras'))
        self.assertTrue(get_user_model().objects.filter(username='novato').exists())
        self.assertIn('_auth_user_id',self.client.session)

    def test_cadastro_com_senhas_diferentes_nao_cria_usuario(self):
        resposta = self.client.post(reverse( 'cadastro'),{
        'username' : 'novato',
        'password1':'senhaboa245',
        'password2':'senhaboa345',
        })

        self.assertEqual(resposta.status_code,200)
        self.assertFalse(get_user_model().objects.filter(username='novato').exists())


    def test_logout_derruba_a_sessao(self):
        usuario = get_user_model().objects.create_user(username='soldado', password='novato23')
        self.client.force_login(usuario)
        self.client.post(reverse('logout'))
        self.assertNotIn('_auth_user_id', self.client.session)


class AcessoSemLoginTestCase(TestCase):
    def test_estante_sem_login_manda_pro_login(self):
        resposta = self.client.get(reverse('lista-leituras'))
        self.assertRedirects(resposta,'/contas/login/?next=/')
    
    def test_nova_obra_sem_login_manda_pro_login(self):
        resposta = self.client.get(reverse('nova-obra'))
        self.assertRedirects(resposta, '/contas/login/?next=/obras/nova/')

    def test_editar_sem_login_manda_pro_login(self):
        resposta = self.client.get(reverse('editar-leitura',args=[1]))
        self.assertRedirects(resposta, '/contas/login/?next=/leituras/1/editar/')


    def test_mover_sem_login_manda_pro_login(self):
        resposta = self.client.post(reverse('mover-capitulo', args=[1]))
        self.assertRedirects(resposta, '/contas/login/?next=/leituras/1/mover/')