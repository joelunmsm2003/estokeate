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


from datetime import datetime,timedelta

from django.contrib.auth import authenticate

def home(request):


	productos= Producto.objects.all()


	return render(request, 'home.html',{'productos':productos})


def autentificacion(request):


	return render(request, 'login.html')


def productos(request):


	return render(request, 'productos.html')

def perfil(request):

	user = request.user.id

	productos= Producto.objects.filter(user_id=user)

	usuario= AuthUser.objects.get(id=user)

	return render(request, 'productosuser.html',{'productos':productos,'usuario':usuario})


	return render(request, 'perfil.html')


@login_required(login_url="/autentificacion/")

def productos(request,id):

	user = request.user.id

	productos= Producto.objects.filter(user_id=user)

	usuario= AuthUser.objects.get(id=user)

	return render(request, 'productosuser.html',{'productos':productos,'usuario':usuario})

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

def vender(request):

	user = request.user.id

	usuario= AuthUser.objects.get(id=user)

	if request.method == 'POST':

		print request.POST

		user = request.user.id

		categoria = request.POST['categoria']
		
		titulo = request.POST['titulo']

		descripcion = request.POST['descripcion']

		Producto(user_id=user,categoria_id=categoria,descripcion=descripcion).save()

		return HttpResponseRedirect('/productos/'+str(user))

		

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