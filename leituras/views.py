from django.shortcuts import render,redirect, get_object_or_404
from django.views.decorators.http import require_POST
from rest_framework import viewsets
from .models import Obra, Leitura
from .serializers import ObraSerializer, LeituraSerializer
from django.utils import timezone
from .forms import ObraForm, LeituraForm
from django.core.exceptions import ValidationError
from django.db import transaction
# Create your views here.

class ObraViewSet(viewsets.ModelViewSet):
    queryset = Obra.objects.all()
    serializer_class = ObraSerializer

class LeituraViewSet(viewsets.ModelViewSet):
    queryset = Leitura.objects.all()
    serializer_class = LeituraSerializer

def lista_leituras(request):
    leituras = Leitura.objects.select_related('obra').order_by('-atualizado_em')
    grupos = {}
    for leitura in leituras:
        grupos.setdefault(leitura.obra.grupo, []).append(leitura)
    # a ordem das secoes segue a ordem do GRUPOS no modelo, e so entra
    # secao que tem leitura -- por isso o "if nome in grupos"  
    ordem = list(dict.fromkeys(Obra.GRUPOS.values())) + ['Outros']
    secoes = [(nome, grupos[nome]) for nome in ordem if nome in grupos]

    return render(request, 'leituras/lista.html', {
        'leituras': leituras,
        'secoes': secoes,
    })

@require_POST
def mover_capitulo(request, pk):
    leitura = get_object_or_404(Leitura, pk=pk)
    passo = 1 if request.POST.get('passo') == '1' else -1
    novo = leitura.capitulo_atual + passo
    total = leitura.obra.total_capitulos

    if novo < 0 or (total is not None and novo > total):
        return redirect('lista-leituras')

    leitura.capitulo_atual = novo

    if total is not None:
        if novo == total:
            leitura.status = 'Finalizado'
            leitura.encerrado_em = timezone.localdate()
        elif leitura.status == 'Finalizado':
            leitura.status = 'Lendo'
            leitura.encerrado_em = None

    leitura.save()
    return redirect('lista-leituras')


def nova_obra(request):
    if request.method == 'POST':
        form_obra = ObraForm(request.POST)
        form_leitura = LeituraForm(request.POST)

        # os dois is_valid() rodam antes do if: com "a and b", um erro no
        # primeiro faria o segundo nem ser validado, e a tela voltaria
        # escondendo metade dos erros.
        obra_ok = form_obra.is_valid()
        leitura_ok = form_leitura.is_valid()

        if obra_ok and leitura_ok:
            try:
                with transaction.atomic():
                    obra = form_obra.save()
                    leitura = form_leitura.save(commit=False)
                    leitura.obra = obra
                    leitura.full_clean(exclude=['obra'])
                    leitura.save()
            except ValidationError as erro:
                form_leitura.add_error(None, erro)
            else:
                return redirect('lista-leituras')
    else:
        form_obra = ObraForm()
        form_leitura = LeituraForm(initial={'status': 'Lendo', 'capitulo_atual': 0})

    return render(request, 'leituras/form_obra.html', {
        'form_obra': form_obra,
        'form_leitura': form_leitura,
    })