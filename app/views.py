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


	return render(request, 'home.html')


def autentificacion(request):


	return render(request, 'login.html')


def productos(request):


	return render(request, 'productos.html')

def perfil(request):


	return render(request, 'perfil.html')



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

	if request.method == 'POST':

		print request.POST

		categoria = request.POST['categoria']
		
		titulo = request.POST['titulo']

		descripcion = request.POST['descripcion']

		Producto(user_id=user,categoria_id=categoria,descripcion=descripcion).save()

		

	return render(request, 'vender.html')


def ingresar(request):

	if request.user.is_authenticated():

		return HttpResponseRedirect("/productos")

	else:

		if request.method == 'POST':

			print request.POST

			user = request.POST['username']
			
			psw = request.POST['password']

			user = authenticate(username=user, password=psw)

		
			if user is not None:

				if user.is_active:

					login(request, user)

					return HttpResponseRedirect("/home")

			else:
				return HttpResponseRedirect("/ingresar")
		
		else:

			return render(request, 'login.html',{})