# \ <section:top>
from django.http import HttpResponse, HttpResponseRedirect
from django.template import loader
import time
from .forms import *
from .models import *
# / <section:top>
# \ <section:mid>
def index(request):
    if not request.user.is_authenticated:
        return HttpResponseRedirect(f'/admin/login/?next={request.path}')
    template = loader.get_template('index.html')
    form = bullyForm()
    context = {
        'form':form,
        # \ <section:context>
        'date':time.strftime('%d.%m.%y'),
        'time':time.strftime('%H:%M'),
        # / <section:context>
    }
    return HttpResponse(template.render(context, request))
# / <section:mid>
