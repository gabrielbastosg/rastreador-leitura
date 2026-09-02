from django.shortcuts import render,redirect, get_object_or_404
from django.views.decorators.http import require_POST
from rest_framework import viewsets
from .models import Obra, Leitura
from .serializers import ObraSerializer, LeituraSerializer
from django.utils import timezone
# Create your views here.

class ObraViewSet(viewsets.ModelViewSet):
    queryset = Obra.objects.all()
    serializer_class = ObraSerializer

class LeituraViewSet(viewsets.ModelViewSet):
    queryset = Leitura.objects.all()
    serializer_class = LeituraSerializer

def lista_leituras(request):
    leituras = Leitura.objects.select_related('obra').order_by('-atualizado_em')
    return render(request, 'leituras/lista.html', {'leituras': leituras})

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