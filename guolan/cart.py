# -*- coding: utf-8 -*-
from django.shortcuts import *
from models import *
import json

class Cart:
	pass
	
def get_cart(request):
	menu = json.loads(request.session.get("menu", "[]"))

	cart = Cart()
	cart.min_total = cart.max_total = cart.delivery_fee = 0
	cart.fruits = []
	for f in menu:
		try:
			fruit = Fruit.objects.get(id = f["id"])
			fruit.count = f["count"]
			cart.fruits.append(fruit)
			cart.min_total += fruit.min_price() * fruit.count
			cart.max_total += fruit.max_price() * fruit.count
		except:
			pass
	
	cart.types = len(cart.fruits)
	try:
		cart.coupons = request.user.get_profile().coupon_set.all()
	except:
		cart.coupons = []
		
	flag = True
	try:		
		coupon = Coupon.objects.get(id = request.session["coupon_id"])
		if cart.min_total < coupon.type.least_consumption:
			flag = False
		if (coupon.userprofile != request.user.get_profile()):
			flag = False
	except:
		flag = False
		
	if flag:
		cart.coupon = coupon
		cart.discount = coupon.type.price
	else:
		cart.coupon = None
		cart.discount = 0 
	
	if cart.min_total < 10:
		cart.delivery_fee = 1
	cart.min_pay = cart.min_total + cart.delivery_fee - cart.discount
	cart.max_pay = cart.max_total + cart.delivery_fee - cart.discount
	return cart

def add(request):
	try:
		fruit_id = request.GET["fruit_id"]
		try:
			render_to = request.GET["render_to"]
		except:
			render_to = "cart.html"
			
		fruit = Fruit.objects.get(id = fruit_id)
		menu = json.loads(request.session.get("menu", "[]"))

		exist = False
		for f in menu:
			if f["id"] == fruit.id:
				f["count"] += 1
				exist = True
				break
				
		if not exist:
			menu.append({"id":fruit.id, "count":fruit.least})
		
		request.session["menu"] = json.dumps(menu)
		cart = get_cart(request)
		return render_to_response(render_to, {"cart":cart})
	except:
		return HttpResponse("出错了，请刷新页面")
	
def delete(request):
	try:
		fruit_id = request.GET["fruit_id"]
		try:
			render_to = request.GET["render_to"]
		except:
			render_to = "cart.html"

		fruit = Fruit.objects.get(id = fruit_id)
		menu = json.loads(request.session.get("menu", "[]"))
		for f in menu:
			if f["id"] == fruit.id:
				f["count"] -= 1
				if f["count"] < fruit.least:
					f["count"] = fruit.least
				break
		request.session["menu"] = json.dumps(menu)
		cart = get_cart(request)
		return render_to_response(render_to, {"cart":cart})
	except:
		return HttpResponse("出错了，请刷新页面")

def remove(request):
	try:
		fruit_id = request.GET["fruit_id"]
		try:
			render_to = request.GET["render_to"]
		except:
			render_to = "cart.html"
			
		fruit = Fruit.objects.get(id = fruit_id)
		menu = json.loads(request.session.get("menu", "[]"))
		for f in menu:
			if f["id"] == fruit.id:
				menu.remove(f)
				break
		request.session["menu"] = json.dumps(menu)
		cart = get_cart(request)
		return render_to_response(render_to, {"cart":cart})
	except:
		return HttpResponse("出错了，请刷新页面")

def update(request):
	try:
		fruit_id = request.GET["fruit_id"]
		try:
			count = int(request.GET["count"])
		except:
			count = 0
		try:
			render_to = request.GET["render_to"]
		except:
			render_to = "cart.html"
		fruit = Fruit.objects.get(id = fruit_id)
		menu = json.loads(request.session.get("menu", "[]"))
		for f in menu:
			if f["id"] == fruit.id:
				f["count"] = count
				if count <= fruit.least:
					f["count"] = fruit.least
				break
		request.session["menu"] = json.dumps(menu)
		cart = get_cart(request)
		return render_to_response(render_to, {"cart":cart})
	except:
		return HttpResponse("出错了，请刷新页面")
	
def clear(request):
	try:
		render_to = request.GET["render_to"]
	except:
		render_to = "cart.html"
	request.session["menu"] = "[]"
	cart = get_cart(request)
	return render_to_response(render_to, {"cart":cart})

def show(request):
	#menu = json.loads(request.session.get("menu", "[]"))
	cart = get_cart(request)
	return render_to_response("cart.html", {"cart":cart})

def coupon(request):
	#menu = json.loads(request.session.get("menu", "[]"))
	try:
		render_to = request.GET["render_to"]
	except:
		render_to = "cart.html"
	try:		
		coupon = Coupon.objects.get(id = request.GET["coupon_id"])
		if (coupon.userprofile == request.user.get_profile()):
			request.session["coupon_id"] = coupon.id
	except:
		request.session["coupon_id"] = 0

	cart = get_cart(request)
	return render_to_response(render_to, {"cart":cart})
