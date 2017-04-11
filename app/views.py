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

from datetime import datetime,timedelta

from django.contrib.auth import authenticate

def ValuesQuerySetToDict(vqs):

    return [item for item in vqs]

def home(request):

	user = request.user.id

	usuario = None

	productos= Producto.objects.all()

	for p in productos:

		if Photoproducto.objects.filter(producto_id=p.id).values('id','photo__photo').count()>0:

			p.photo = Photoproducto.objects.filter(producto_id=p.id).values('id','photo__photo')[0]

	if user:

		usuario= AuthUser.objects.get(id=user)

	return render(request, 'home.html',{'productos':productos,'usuario':usuario})


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


	return render(request, 'perfil.html',{'productos':productos,'usuario':usuario,'miperfil':'active'})


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





        return render(request, 'perfil.html',{'productos':productos,'usuario':usuario,'miperfil':'active'})

        




@login_required(login_url="/autentificacion")
def chat(request):

	user = request.user.id

	productos= Producto.objects.filter(user_id=user)

	print productos



	usuario= AuthUser.objects.get(id=user)


	return render(request, 'chat.html',{'productos':productos,'usuario':usuario,'mimensaje':'active'})

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

	return render(request, 'productosuser.html',{'productos':productos,'usuario':usuario,'mianuncio':'active'})

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

	usuario = None

	if user:

		usuario =AuthUser.objects.get(id=user)

	producto= Producto.objects.get(id=id)


	return render(request, 'productodetalle.html',{'producto':producto,'usuario':usuario})



def busqueda(request,dato):

	user = request.user.id

	usuario = None

	if user:

		usuario =AuthUser.objects.get(id=user)

	categoria = Categoria.objects.all()

		
	productos = Producto.objects.filter(descripcion__contains=dato)

		
	return render(request, 'busqueda.html',{'categoria':categoria,'productos':productos,'usuario':usuario,'dato':dato})


def productojson(request,id):

	user = request.user.id

	usuario = None

	if user:

		usuario =AuthUser.objects.get(id=user)

	
	photos = Photoproducto.objects.filter(producto_id=id).values('id','photo__photo')

	for p in range(len(photos)):

		photos[p]['detalle'] = str(Photoproducto.objects.get(id=photos[p]['id']).photo.photo).split('.jpg')[0]+'_thumbail.jpg'


	photos = ValuesQuerySetToDict(photos)

	photos = simplejson.dumps(photos)
	

	return HttpResponse(photos, content_type="application/json")

@login_required(login_url="/autentificacion/")

def usuario(request,id):

	user = request.user.id

	usuario= AuthUser.objects.get(id=user)

	return render(request, 'usuario.html',{'usuario':usuario})



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

		mensaje = data['mensaje1']

		receptor = data['user']

		Chat(user_id=user,destino_id=receptor,mensaje=mensaje,producto_id=producto,fecha=fecha).save()

		data = simplejson.dumps(data)

	return HttpResponse(data, content_type="application/json")




@login_required(login_url="/autentificacion/")

def editarproducto(request,id):


	if request.method == 'GET':

		producto = Producto.objects.get(id=id)

		return render(request, 'editarproducto.html',{'producto':producto})

	if request.method == 'POST':

		categoria = request.POST['categoria']

		titulo = request.POST['titulo']

		descripcion = request.POST['descripcion']

		p = Producto.objects.get(id=id)

		p.categoria_id = categoria
		p.titulo = titulo
		p.descripcion = descripcion
		p.save()


		return render(request, 'editarproducto.html',{'producto':p})






def vender(request):

	user = request.user.id

	usuario= None

	if user:

		usuario= AuthUser.objects.get(id=user)

	if request.method == 'POST':


		print 'ooooooo',request.FILES

		categoria = request.POST['categoria']
		
		titulo = request.POST['titulo']

		descripcion = request.POST['descripcion']

		precio = request.POST['precio']

		Producto(user_id=user,titulo=titulo,categoria_id=categoria,descripcion=descripcion,precio=precio).save()

		id_producto = Producto.objects.all().values('id').order_by('-id')[0]['id']

		y = 600

		for p in request.FILES:

			if p == 'picture':

				photo =  request.FILES['picture']

				#Photo

				Photo(photo=photo).save()

				id_photo = Photo.objects.all().values('id').order_by('-id')[0]['id']

				Photoproducto(photo_id=id_photo,producto_id=id_producto).save()

				caption = '/var/www/html/'+str(Photo.objects.get(id=id_photo).photo)

				# Para la galeria

				

				caption_galeria = caption.split('.jpg')[0]+'_thumbail.jpg'

				fd_img = open(caption, 'r')

				img = Image.open(fd_img)

				

				img = resizeimage.resize_cover(img, [500, 600])

				img.save(caption_galeria, img.format)
				
				fd_img.close()

				# Para el Home

				fd_img = open(caption, 'r')

				img = Image.open(fd_img)

				img = resizeimage.resize_cover(img, [250, 300])

				img.save(caption, img.format)
				
				fd_img.close()


			if p == 'picture1':

				# Photo

				picture1 =  request.FILES['picture1']

				Photo(photo=picture1).save()

				id_photo = Photo.objects.all().values('id').order_by('-id')[0]['id']

				Photoproducto(photo_id=id_photo,producto_id=id_producto).save()

				caption = '/var/www/html/'+str(Photo.objects.get(id=id_photo).photo)

				# Para la galeria

				caption_galeria = caption.split('.jpg')[0]+'_thumbail.jpg'

				fd_img = open(caption, 'r')

				img = Image.open(fd_img)

				img = resizeimage.resize_cover(img, [500, y])

				img.save(caption_galeria, img.format)
				
				fd_img.close()

				#Para el home

				fd_img = open(caption, 'r')

				img = Image.open(fd_img)

				img = resizeimage.resize_cover(img, [250, 300])

				img.save(caption, img.format)
				
				fd_img.close()

			if p=='picture2':

						# Photo

				picture2 =  request.FILES['picture2']

				Photo(photo=picture2).save()

				id_photo = Photo.objects.all().values('id').order_by('-id')[0]['id']

				Photoproducto(photo_id=id_photo,producto_id=id_producto).save()

				caption = '/var/www/html/'+str(Photo.objects.get(id=id_photo).photo)

				# Para el galeria

		 		caption_galeria = caption.split('.jpg')[0]+'_thumbail.jpg'

				fd_img = open(caption, 'r')

				img = Image.open(fd_img)

				img = resizeimage.resize_cover(img, [500, y])

				img.save(caption_galeria, img.format)
				
				fd_img.close()

				#Para el home

				fd_img = open(caption, 'r')

				img = Image.open(fd_img)

				img = resizeimage.resize_cover(img, [250, 300])

				img.save(caption, img.format)
				
				fd_img.close()


			if p=='picture3':

						# Photo

				picture3 =  request.FILES['picture3']

				Photo(photo=picture3).save()

				id_photo = Photo.objects.all().values('id').order_by('-id')[0]['id']

				Photoproducto(photo_id=id_photo,producto_id=id_producto).save()

				caption = '/var/www/html/'+str(Photo.objects.get(id=id_photo).photo)

								# Para la galeria

				caption_galeria = caption.split('.jpg')[0]+'_thumbail.jpg'

				fd_img = open(caption, 'r')

				img = Image.open(fd_img)

				img = resizeimage.resize_cover(img, [500, y])

				img.save(caption_galeria, img.format)
				
				fd_img.close()

				#para el home

				fd_img = open(caption, 'r')

				img = Image.open(fd_img)

				img = resizeimage.resize_cover(img, [250, 300])

				img.save(caption, img.format)
				
				fd_img.close()


	return render(request, 'vender.html',{'usuario':usuario})



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

			return render(request, 'login.html',{})