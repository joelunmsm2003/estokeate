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
from django.db import transaction
from django.contrib.auth.hashers import *
from django.core.mail import send_mail
from django.db import connection
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

	print productos



	usuario= AuthUser.objects.get(id=user)


	return render(request, 'perfil.html',{'productos':productos,'usuario':usuario})


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

	return render(request, 'productosuser.html',{'productos':productos,'usuario':usuario})




def producto(request,id):

	user = request.user.id

	usuario = None

	if user:

		usuario =AuthUser.objects.get(id=user)

	producto= Producto.objects.get(id=id)


	return render(request, 'productodetalle.html',{'producto':producto,'usuario':usuario})


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



def vender(request):

	user = request.user.id

	usuario= None

	if user:

		usuario= AuthUser.objects.get(id=user)

	if request.method == 'POST':

		print 'Archivos...',request.FILES

		photo =  request.FILES['picture']

		picture1 =  request.FILES['picture1']

		picture2 =  request.FILES['picture2']

		picture3 =  request.FILES['picture3']

		user = request.user.id

		categoria = request.POST['categoria']
		
		titulo = request.POST['titulo']

		descripcion = request.POST['descripcion']

		Producto(user_id=user,categoria_id=categoria,descripcion=descripcion).save()

		id_producto = Producto.objects.all().values('id').order_by('-id')[0]['id']

		#Photo

		Photo(photo=photo).save()

		id_photo = Photo.objects.all().values('id').order_by('-id')[0]['id']

		Photoproducto(photo_id=id_photo,producto_id=id_producto).save()

		caption = '/var/www/html/'+str(Photo.objects.get(id=id_photo).photo)

		# Para la galeria

		y = 600

		caption_galeria = caption.split('.jpg')[0]+'_thumbail.jpg'

		fd_img = open(caption, 'r')

		img = Image.open(fd_img)

		img = resizeimage.resize_cover(img, [500, y])

		img.save(caption_galeria, img.format)
		
		fd_img.close()

		# Para el Home

		fd_img = open(caption, 'r')

		img = Image.open(fd_img)

		img = resizeimage.resize_cover(img, [250, 300])

		img.save(caption, img.format)
		
		fd_img.close()



		# Photo

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



		# Photo

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




		# Photo

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