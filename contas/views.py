from django.shortcuts import render,redirect
from django.contrib.auth import login

from .forms import CadastroForm
# Create your views here.

def cadastro(request):
    if request.method == 'POST':
        form = CadastroForm(request.POST)
        if form.is_valid():
            usuario = form.save()
            login(request, usuario)
            return redirect('lista-leituras')
    else:
        form = CadastroForm()

    return render(request, 'contas/cadastro.html', {'form': form})