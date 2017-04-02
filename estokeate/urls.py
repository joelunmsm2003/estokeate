from django.conf.urls import include, url
from django.contrib import admin

urlpatterns = [

    url(r'^admin/', admin.site.urls),
    url(r'^$', 'app.views.home'),
    url(r'^autentificacion/$', 'app.views.autentificacion'),
    url(r'^productos/$', 'app.views.productos'),
    url(r'^ingresar/$', 'app.views.ingresar'),
    url(r'^registra/$', 'app.views.registra'),
    url(r'^salir/$', 'app.views.salir'),
    url(r'^perfil/$', 'app.views.perfil'),
    url(r'^vender/$', 'app.views.vender'),
    url(r'^productos/(\d+)$', 'app.views.productos'),
    url(r'^producto/(\d+)$', 'app.views.producto'),
    url(r'^productojson/(\d+)$', 'app.views.productojson'),
    url(r'^usuario/(\d+)$', 'app.views.usuario'),
    url(r'^editarproducto/(\d+)$', 'app.views.editarproducto'),
    url(r'^chat/$', 'app.views.chat'),
    url(r'^chatin/(\d+)$', 'app.views.chatin'),
    url(r'^enviamensaje/$', 'app.views.enviamensaje'),
    url(r'^listamensajes/(\d+)$', 'app.views.listamensajes'),

]