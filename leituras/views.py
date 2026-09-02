from rest_framework import viewsets
from .models import Obra, Leitura
from .serializers import ObraSerializer, LeituraSerializer
# Create your views here.

class ObraViewSet(viewsets.ModelViewSet):
    queryset = Obra.objects.all()
    serializer_class = ObraSerializer

class LeituraViewSet(viewsets.ModelViewSet):
    queryset = Leitura.objects.all()
    serializer_class = LeituraSerializer