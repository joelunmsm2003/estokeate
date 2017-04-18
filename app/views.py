from django.shortcuts import *
from django.template import RequestContext
from django.contrib.auth import *
from django.contrib.auth.models import Group, User
from django.core import serializers
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.db.models import Max,Count
from django.core.mail import send_mail
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from app.models import *
from estokeate import settings
from django.db import transaction
from django.contrib.auth.hashers import *
from django.core.mail import send_mail

from django.utils.six.moves import range
from django.http import StreamingHttpResponse
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import permission_required
from django.views.decorators.csrf import csrf_exempt
import time
import collections
import xlrd
import json 
import csv
import simplejson
import xlwt
import requests
import os
from PIL import Image
from resizeimage import resizeimage
from estokeate.settings import *
from datetime import datetime,timedelta
from django.contrib.auth import authenticate

from django.contrib.sites.shortcuts import get_current_site


def ValuesQuerySetToDict(vqs):

	return [item for item in vqs]

def home(request):

	user = request.user.id

	current_site = get_current_site(request)

	print current_site

	usuario = None

	productos= Producto.objects.all()

	for p in productos:

		if Photoproducto.objects.filter(producto_id=p.id).values('id','photo__photo').count()>0:

			p.photo = Photoproducto.objects.filter(producto_id=p.id).values('id','photo__photo')[0]

	if user:

		usuario= AuthUser.objects.get(id=user)

	return render(request, 'home.html',{'productos':productos,'usuario':usuario,'host':host})


def autentificacion(request):


	return render(request, 'login.html')



@login_required(login_url="/autentificacion")

def salir(request):

	logout(request)
	
	return HttpResponseRedirect("/")


def productos(request):


	return render(request, 'productos.html')


@login_required(login_url="/autentificacion")
def perfil(request):

	user = request.user.id

	productos= Producto.objects.filter(user_id=user)

	usuario= AuthUser.objects.get(id=user)


	return render(request, 'perfil.html',{'productos':productos,'usuario':usuario,'miperfil':'active','host':host})


@login_required(login_url="/autentificacion")

def actualizaperfil(request):


	if request.method == 'POST':

		user = request.user.id

		productos= Producto.objects.filter(user_id=user)

		usuario= AuthUser.objects.get(id=user)

		username = request.POST['username']
		
		direccion = request.POST['direccion']

		email = request.POST['email']

		telefono = request.POST['telefono']

		for p in request.FILES:

			if p == 'photo':

				photo =  request.FILES['photo']

				u = AuthUser.objects.get(id=user)

				u.photo=photo

				u.save()


		u = AuthUser.objects.get(id=user)

		u.direccion = direccion

		u.email=email

		u.telefono=telefono

		u.save()


		for p in request.FILES:

			if p == 'photo':

				caption = '/var/www/html/'+str(u.photo)

				fd_img = open(caption, 'r')

				img = Image.open(fd_img)

				img = resizeimage.resize_cover(img, [500, 500])

				img.save(caption, img.format)

				fd_img.close()


		return HttpResponseRedirect("/perfil/")

def filtrarcategoria(request,dato,categoria):


	dato = dato.replace('-',' ')

	user = request.user.id

	productos= Producto.objects.filter(descripcion__contains=dato,categoria_id=categoria)
 

	subcat = Subcategoria.objects.filter(categoria_id=categoria)

	cat = Categoria.objects.get(id=categoria)


	resultados= Producto.objects.filter(descripcion__contains=dato).values('subcategoria','subcategoria__nombre').annotate(total=Count('subcategoria'))



	usuario = None

	if user:

		usuario =AuthUser.objects.get(id=user)

	for p in productos:

		if Photoproducto.objects.filter(producto_id=p.id).values('id','photo__photo').count()>0:

			p.photo = Photoproducto.objects.filter(producto_id=p.id).values('id','photo__photo')[0]



	return render(request, 'filtrasubcategoria.html',{'host':host,'productos':productos,'dato':dato,'subcat':subcat,'categoria':cat.nombre,'resultados':resultados,'totalcat':productos.count()})

def filtrarsubcategoria(request,dato,subcategoria):


	dato = dato.replace('-',' ')

	user = request.user.id



	productos= Producto.objects.filter(descripcion__contains=dato,subcategoria_id=subcategoria)
 

	subcat = Subcategoria.objects.get(id=subcategoria)

	cat = Categoria.objects.get(id=subcategoria)

	totalcat = Producto.objects.filter(descripcion__contains=dato,categoria_id=cat.id).count()
 

	resultados= Producto.objects.filter(descripcion__contains=dato).values('subcategoria','subcategoria__nombre').annotate(total=Count('subcategoria'))



	usuario = None

	if user:

		usuario =AuthUser.objects.get(id=user)

	for p in productos:

		if Photoproducto.objects.filter(producto_id=p.id).values('id','photo__photo').count()>0:

			p.photo = Photoproducto.objects.filter(producto_id=p.id).values('id','photo__photo')[0]



	return render(request, 'resultadosubcategoria.html',{'host':host,'productos':productos,'dato':dato,'subcat':subcat,'categoria':cat,'resultados':resultados,'totalsubcat':productos.count(),'totalcat':totalcat})



@login_required(login_url="/autentificacion")
def chat(request):

	user = request.user.id

	productos= Producto.objects.filter(user_id=user)

	print productos



	usuario= AuthUser.objects.get(id=user)


	return render(request, 'chat.html',{'host':host,'productos':productos,'usuario':usuario,'mimensaje':'active'})

# Prductos de un usuario

@login_required(login_url="/autentificacion/")

def productos(request,id):

	user = request.user.id

	usuario = None

	if user:

		usuario =AuthUser.objects.get(id=user)

	productos= Producto.objects.filter(user_id=user)

	for p in productos:

		if Photoproducto.objects.filter(producto_id=p.id).values('id','photo__photo').count()>0:

			p.photo = Photoproducto.objects.filter(producto_id=p.id).values('id','photo__photo')[0]


	usuario= AuthUser.objects.get(id=user)

	return render(request, 'productosuser.html',{'host':host,'productos':productos,'usuario':usuario,'mianuncio':'active'})

# Compradores de un usuario

@login_required(login_url="/autentificacion/")

def chatin(request,id):

	user = request.user.id

	compradores = Chat.objects.filter(destino_id=user).values('user','user__username','user__photo','producto','producto__titulo','producto__precio','producto__titulo').annotate(count=Count('id'))

	compradores = ValuesQuerySetToDict(compradores)

	compradores = simplejson.dumps(compradores)

	return HttpResponse(compradores, content_type="application/json")



# MEsajes

def ordenar(data):
		 
	return data['id']


@login_required(login_url="/autentificacion/")

def listamensajes(request,user,producto):

	destino = request.user.id

	# Mensajes que le llegan al dueno del producto

	mensajes = Chat.objects.filter(destino_id=destino,user_id=user,producto_id=producto).values('id','producto','producto__precio','destino','user','destino__username','user__username','user__photo','mensaje','producto__titulo','producto__categoria')

	fmt = '%Y-%m-%d %H:%M:%S'

	for p in range(len(mensajes)):

		if Chat.objects.filter(id=mensajes[p]['id']).values('fecha')[0]['fecha']:

			mensajes[p]['fecha'] = Chat.objects.get(id=mensajes[p]['id']).fecha.strftime(fmt)
	
		mensajes[p]['photo_producto'] = str(Photoproducto.objects.filter(producto_id=mensajes[p]['producto'])[0].photo.photo)
		
	# Mensajes que envia el dueno del producto al interesado


	mensajes1 = Chat.objects.filter(destino_id=user,user_id=destino,producto_id=producto).values('id','producto','producto__precio','destino','user','destino__username','user__username','user__photo','mensaje','producto__titulo','producto__categoria')

	fmt = '%Y-%m-%d %H:%M:%S'

	for p in range(len(mensajes1)):

		if Chat.objects.filter(id=mensajes1[p]['id']).values('fecha')[0]['fecha']:

			mensajes1[p]['fecha'] = Chat.objects.get(id=mensajes1[p]['id']).fecha.strftime(fmt)
	
		mensajes1[p]['photo_producto'] = str(Photoproducto.objects.filter(producto_id=mensajes1[p]['producto'])[0].photo.photo)
		



	mensajes = ValuesQuerySetToDict(mensajes) + ValuesQuerySetToDict(mensajes1)

	mensajes = sorted(mensajes,key=ordenar)

	mensajes = simplejson.dumps(mensajes)

	return HttpResponse(mensajes, content_type="application/json")



def producto(request,id):

	user = request.user.id

	current_site = get_current_site(request)

	p = str(current_site).split('.')[0]



	print p
	
	usuario = None

	if user:

		usuario =AuthUser.objects.get(id=user)

	producto= Producto.objects.get(id=id)

	videos = None

	if Videoproducto.objects.filter(producto_id=id):

		videos = Videoproducto.objects.filter(producto_id=id)[0]

	if p=='m':	

		return render(request, 'productodetallemovil.html',{'host':host,'producto':producto,'usuario':usuario,'videos':videos})

	else:	

		return render(request, 'productodetalle.html',{'host':host,'producto':producto,'usuario':usuario,'videos':videos})
		


def busqueda(request):


	if request.method == 'POST':

		

		dato= request.POST['dato']

		dato = dato.replace(' ','-')

		user = request.user.id

		usuario = None

		if user:

			usuario =AuthUser.objects.get(id=user)

		categoria = Categoria.objects.all()

			
		productos = Producto.objects.filter(descripcion__contains=dato)

		total = productos.count()

		for p in productos:

			if Photoproducto.objects.filter(producto_id=p.id).values('id','photo__photo').count()>0:

				p.photo = Photoproducto.objects.filter(producto_id=p.id).values('id','photo__photo')[0]


		resultados= Producto.objects.filter(descripcion__contains=dato).values('categoria','categoria__nombre').annotate(total=Count('categoria'))


			
		return render(request, 'busqueda.html',{'host':host,'categoria':categoria,'productos':productos,'total':total,'dato':dato,'resultados':resultados})


def productojson(request,id):

	user = request.user.id

	usuario = None

	if user:

		usuario =AuthUser.objects.get(id=user)

	
	photos = Photoproducto.objects.filter(producto_id=id).values('id','photo__photo')

	for p in range(len(photos)):

		photos[p]['detalle'] = str(Photoproducto.objects.get(id=photos[p]['id']).photo.photo).split('.jpg')[0]+'_thumbail.jpg'


	videos = Videoproducto.objects.filter(producto_id=id).values('id','video__video')


	photos = ValuesQuerySetToDict(photos)

	photos = simplejson.dumps(photos)
	

	return HttpResponse(photos, content_type="application/json")

@login_required(login_url="/autentificacion/")

def usuario(request,id):

	user = request.user.id

	usuario= AuthUser.objects.get(id=user)

	return render(request, 'usuario.html',{'host':host,'usuario':usuario})



def registra(request):

	if request.method == 'POST':

		print request.POST

		user = request.POST['username']
		
		psw = request.POST['password']

		rpsw = request.POST['password']

		if psw == rpsw:

			User.objects.create_user(user, user, psw)

			user = authenticate(username=user, password=psw)


	return render(request, 'perfil.html')



@login_required(login_url="/autentificacion/")

def enviamensaje(request):

	if request.method == 'POST':

		user = request.user.id

		fecha = datetime.today()-timedelta(hours=5)

		producto = request.POST['producto']

		mensaje = request.POST['mensaje']

		receptor = Producto.objects.get(id=producto).user.id

		Chat(user_id=user,destino_id=receptor,mensaje=mensaje,producto_id=producto,fecha=fecha).save()



	return HttpResponseRedirect("/producto/"+producto)

@csrf_exempt
def enviamensaje_perfil(request):

	if request.method == 'POST':

		user = request.user.id

		print user

		data = json.loads(request.body)['dato']

		#{u'user__username': u'carla', u'destino__username': u'ander', u'producto': 55, u'mensaje': u'Hola Ander me interesa tu producto', u'producto__titulo': u'Iphone 7', u'photo_producto': u'static/iphone-8-hajek-2.jpg', u'destino': 3, u'user': 1, u'mensaje1': u'545', u'producto__precio': 121, u'producto__categoria': 4, u'user__photo': u'static/notachica_TZMPAOL.jpg'}

		# print 'Mesnaje.....',request.POST

		fecha = datetime.today()-timedelta(hours=5)

		producto = data['producto']

		mensaje = data['mensaje1x']

		receptor = data['user']

		Chat(user_id=user,destino_id=receptor,mensaje=mensaje,producto_id=producto,fecha=fecha).save()

		data = simplejson.dumps(data)

	return HttpResponse(data, content_type="application/json")


@csrf_exempt
def traesubcategorias(request,categoria):

	subcategorias = Subcategoria.objects.filter(categoria_id=categoria).values('id','nombre')

	subcategorias = ValuesQuerySetToDict(subcategorias) 

	subcategorias = simplejson.dumps(subcategorias)

	return HttpResponse(subcategorias, content_type="application/json")


@csrf_exempt
def uploadphoto(request):


		caption = request.FILES['file']



		Photo(photo=caption).save()

		id_photo = Photo.objects.all().values('id').order_by('-id')[0]['id']

		caption = '/var/www/html/'+str(Photo.objects.get(id=id_photo).photo)

		data_json =str(Photo.objects.get(id=id_photo).photo)

		fd_img = open(caption, 'r')

		img = Image.open(fd_img)

		width, height = img.size

		photo = Photo.objects.filter(id=id_photo).values('id','photo')

		img = resizeimage.resize_cover(img, [500, 500])

		img.save(caption, img.format)

		fd_img.close()

		# Para la galeria

		caption_galeria = caption.split('.jpg')[0]+'_thumbail.jpg'

		fd_img = open(caption, 'r')

		img = Image.open(fd_img)

		img = resizeimage.resize_cover(img, [500, 600])

		img.save(caption_galeria, img.format)

		fd_img.close()

		#para el home

		fd_img = open(caption, 'r')

		img = Image.open(fd_img)

		img = resizeimage.resize_cover(img, [250, 300])

		img.save(caption, img.format)

		fd_img.close()

		photo = ValuesQuerySetToDict(photo)

		data_json = simplejson.dumps(photo)



		return HttpResponse(data_json, content_type="application/json")


@csrf_exempt
def uploadvideo(request):

		caption = request.FILES['file']

		Video(video=caption).save()

		id_video = Video.objects.all().values('id').order_by('-id')[0]['id']

		videodata = Video.objects.filter(id=id_video).values('id','video')

		videodata = ValuesQuerySetToDict(videodata)

		data_json = simplejson.dumps(videodata)

		return HttpResponse(data_json, content_type="application/json")


@login_required(login_url="/autentificacion/")

def editarproducto(request,id):


	if request.method == 'GET':

		producto = Producto.objects.filter(id=id)

		return render(request, 'editarproducto.html',{'producto':producto[0]})

	if request.method == 'POST':

		categoria = request.POST['categoria']

		titulo = request.POST['titulo']

		descripcion = request.POST['descripcion']

		p = Producto.objects.get(id=id)

		p.categoria_id = categoria
		p.titulo = titulo
		p.descripcion = descripcion
		p.save()


		return render(request, 'editarproducto.html',{'producto':p,'host':host})





@csrf_exempt
def vender(request):

	user = request.user.id

	id_user=None

	usuario= None

	if user:

		id_user= AuthUser.objects.get(id=user).id

		usuario=AuthUser.objects.get(id=user)

	if request.method == 'POST':


		data = json.loads(request.body)['dato']

		titulo = data['titulo']
		precio=data['precio']
		descripcion=data['descripcion']
		categoria=data['categoria']
		subcategoria=data['subcategoria']

		print 'hdhdh',data


		Producto(user_id=id_user,titulo=titulo,categoria_id=categoria,subcategoria_id=subcategoria,descripcion=descripcion,precio=precio).save()

		id_producto = Producto.objects.all().values('id').order_by('-id')[0]['id']


		for d in data:


			print 'Queee...',d


			if d=='image':

				image=data['image']

				print 'Imagen...',image

				Photoproducto(photo_id=image,producto_id=id_producto).save()

			if d=='image_1':
			
				image_1 = data['image_1']

				Photoproducto(photo_id=image_1,producto_id=id_producto).save()

			if d=='image_2':

				image_2 = data['image_2']

				Photoproducto(photo_id=image_2,producto_id=id_producto).save()

			if d =='image_3':

				image_3 = data['image_3']

				Photoproducto(photo_id=image_3,producto_id=id_producto).save()


			if d =='image_4':

				image_4 = data['image_4']

				Photoproducto(photo_id=image_4,producto_id=id_producto).save()


			if d =='image_5':

				image_5 = data['image_5']

				Photoproducto(photo_id=image_5,producto_id=id_producto).save()


			if d =='image_6':

				image_6 = data['image_6']

				Photoproducto(photo_id=image_6,producto_id=id_producto).save()

			if d =='video':

				video = data['video']

				Videoproducto(video_id=video,producto_id=id_producto).save()

		id_producto = simplejson.dumps(id_producto)


		return HttpResponse(id_producto, content_type="application/json")



	categoria = Categoria.objects.all().values('id','nombre','icon')



	return render(request, 'vender.html',{'host':host,'usuario':usuario,'categoria':categoria})



def ingresar(request):

	if request.user.is_authenticated():

		return HttpResponseRedirect("/vender")

	else:

		if request.method == 'POST':

			print request.POST

			user = request.POST['username']
			
			psw = request.POST['password']

			user = authenticate(username=user, password=psw)

		
			if user is not None:

				if user.is_active:

					login(request, user)

					return HttpResponseRedirect("/vender")

			else:
				return HttpResponseRedirect("/ingresar")
		
		else:

			return render(request, 'login.html',{'host':host})