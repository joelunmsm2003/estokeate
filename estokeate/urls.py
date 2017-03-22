from django.conf.urls import include, url
from django.contrib import admin

urlpatterns = [

    url(r'^admin/', admin.site.urls),
    url(r'^$', 'app.views.home'),
    url(r'^autentificacion/$', 'app.views.autentificacion'),
    url(r'^productos/$', 'app.views.productos'),
    url(r'^ingresar/$', 'app.views.ingresar'),
    url(r'^registra/$', 'app.views.registra'),
    url(r'^perfil/$', 'app.views.perfil')
]