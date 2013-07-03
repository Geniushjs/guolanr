# -*- coding: utf-8 -*-
# Create your views here.

from django.shortcuts import *

from models import *
from cart import get_cart

import datetime
import json
import sms

def index(request):
	cart = get_cart(request)
	fruits = Fruit.objects.filter(valid = True).order_by("order")
	return render_to_response("index.html", locals())

def checkout(request):
	cart = get_cart(request)
	if len(cart.fruits) == 0:
		return render_to_response("error.html", {"message":"您的果篮儿空空如也，去挑一点水果再来吧"})
	
	for fruit in cart.fruits:
		fruit.image = Fruit.objects.get(id = fruit.id).image_small
	 
	all_intervals = DeliveryTimeInterval.objects.all().order_by("start_time")
	intervals = []
	now = datetime.datetime.now()
	current_time = datetime.time(hour = now.hour, minute = now.minute)
	for interval in all_intervals:
		if interval.today == False or current_time <= interval.stop_order_time:
			intervals.append(interval) 
	schools = School.objects.all()
	address = request.COOKIES.get("address", "")
	mobile = request.COOKIES.get("mobile", "")
	phone = request.COOKIES.get("phone", "")

	return render_to_response("checkout.html", locals())

def submit(request):
	cart = get_cart(request)
	if len(cart.fruits) == 0:
		return render_to_response("error.html", {"message":"您的果篮儿空空如也，去挑一点水果再来吧"})
	
	try:
		school_id = request.POST["school_id"]
		time_id =  request.POST["time_id"]
		mobile = request.POST["mobile"]
		address = request.POST["address"]
		phone = request.POST.get("mobile", "")
		remark = request.POST.get("remark", "")
	except:
		school_id = request.session["school_id"]
		time_id =  request.session["time_id"]
		mobile = request.session["mobile"]
		address = request.session["address"]
		phone = request.session.get("mobile", "")
		remark = request.session.get("remark", "")

	try:
		userprofile = UserProfile.objects.get(mobile = mobile)
	except UserProfile.DoesNotExist:
		userprofile = UserProfile()
		userprofile.mobile = mobile
		userprofile.valid = False
	userprofile.phone = phone
	userprofile.address = address
	userprofile.save()
	
	if not userprofile.valid:
		sms.send_verify(userprofile)
		request.session["mobile"] = mobile
		request.session["phone"] = phone
		request.session["address"] = address
		request.session["remark"] = remark
		request.session["school_id"] = school_id
		request.session["time_id"] = time_id
		return HttpResponseRedirect("/user/mobile/verify?id=%s&next=%s"%(userprofile.id, request.path))

	order = Order()
	order.min_total = cart.min_total
	order.max_total = cart.max_total
	order.delivery_fee = cart.delivery_fee
	order.discount_price = cart.discount
	order.content = ""
	for fruit in cart.fruits:
		 order.content += "%s%d"%(fruit.name, fruit.count)

	order.address = address	
	order.mobile = mobile
	order.phone = phone
	order.remark = remark
	
	time_interval = DeliveryTimeInterval.objects.get(id = time_id)
	order.today = time_interval.today 
	order.delivery_start_time = time_interval.start_time
	order.delivery_end_time = time_interval.end_time
	order.school = School.objects.get(id = school_id)
	order.datetime = datetime.datetime.now()
	order.school_order_id = order.school.next_order_id()
	
	order.userprofile = userprofile
	order.save()
	sms.send_order(order)
	
	if cart.coupon:
		cart.coupon.delete()
	
	request.session["menu"] = "[]"
	response = HttpResponseRedirect("/myorders")
	response.set_cookie("mobile", order.mobile, max_age = 365 * 24 * 60 * 60)
	response.set_cookie("phone", order.phone, max_age = 365 * 24 * 60 * 60)
	response.set_cookie("address", order.address.encode('utf-8'), max_age = 365 * 24 * 60 * 60)
	
	return response 

def myorders(request):
	try:
		mobile = request.COOKIES["mobile"]
		userprofile = UserProfile.objects.get(mobile = mobile)
		orders = userprofile.order_set.all().order_by("-id")
		return render_to_response("myorders.html", locals())
	except:
		return render_to_response("error.html", {"message":"对不起，请先登录"})

def evaluation(request):
	try:
		order = Order.objects.get(id = request.POST["id"])
		if order.evaluated:
			return render_to_response("error.html", {"title":"订单评价", "message":"您已经评价过了，不用再评价了"})
		if datetime.datetime.now() - order.datetime <= datetime.timedelta(minutes = 5):
			return render_to_response("error.html", {"title":"订单评价", "message":"下单5分钟后才能评价"})
		evaluation = Evaluation()
		evaluation.order = order
		evaluation.general = request.POST["general"] 
		evaluation.remark = request.POST["remark"]
		evaluation.datetime = datetime.datetime.now()
		evaluation.save()
		
		try:
			order.customer_total = int(request.POST["total"])
		except:
			order.customer_total = -1  
		order.evaluated = True
		order.save()
		
		order.userprofile.score += int(order.min_pay() * 10)
		order.userprofile.save()

		return render_to_response("error.html", {"title":"订单评价", "message":"评价成功"})
	except:
		return render_to_response("error.html", {"title":"订单评价","message":"评价出错了！请返回重新评价"})
