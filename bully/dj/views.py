# \ <section:top>
from django.http import HttpResponse, HttpResponseRedirect
from django.template import loader
# / <section:top>
# \ <section:mid>
def index(request):
    if not request.user.is_authenticated:
        return HttpResponseRedirect(f'/admin/login/?next={request.path}')
    template = loader.get_template('index.html')
    context = {
        
    }
    return HttpResponse(template.render(context, request))
# / <section:mid>
