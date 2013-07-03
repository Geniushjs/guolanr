# -*- coding: utf-8 -*-
from django.shortcuts import *
from django.contrib import auth
from django.contrib.auth.decorators import *
from guolan.models import *

def user_is_superuser(user):
	return user.is_superuser

@user_passes_test(user_is_superuser, login_url="/admin")
def index(request):
	order_count = Order.objects.filter(valid = True).count()
	evaluation_count = Evaluation.objects.all().count()
	orders = Order.objects.all().order_by("-id")[:40]
	evaluations = Evaluation.objects.all().order_by("-datetime")[:40]
	
	for eval in evaluations:
		try:
			eval.remark2 = eval.remark.decode("utf-8")
		except:
			try:
				eval.remark2 = eval.remark.decode("gbk")
			except:
				try:
					eval.remark2 = eval.remark.encode("utf-8")
				except:
					eval.remark2 = "sorry"
		 
	return render_to_response("myadmin/index.html", locals())	
	
@user_passes_test(user_is_superuser, login_url="/admin")
def fruit(request):
	fruits = Fruit.objects.all().order_by("order")
	return render_to_response("myadmin/fruit.html", locals())	
	

@user_passes_test(user_is_superuser, login_url="/admin")
def sold_out(request):
	try:
		fruit = Fruit.objects.get(id = request.GET["id"])
		if fruit.sold_out():
			fruit.sold_out_datetime = datetime.datetime.now()
			fruit.save()
			return HttpResponse("<font color=green>已上架</font>")
		else:
			fruit.sold_out_datetime = datetime.datetime.now() + datetime.timedelta(hours = 12)
			fruit.save()
			return HttpResponse("<font color=green>已下架</font>")
	except:
		return HttpResponse("<font color=red>出错了</font>")

@user_passes_test(user_is_superuser, login_url="/admin")
def top(request):
	try:
		top_fruit = Fruit.objects.get(id = request.GET["id"])
		fruits = Fruit.objects.all().order_by("order")
		counter = 0
		for fruit in fruits:
			if top_fruit != fruit:
				counter += 1
				fruit.order = counter
				fruit.save()
		top_fruit.order = 0
		top_fruit.save()
		return HttpResponse("<font color=green>已置顶</font>")
	except:
		return HttpResponse("<font color=red>出错了</font>")
