# -*- coding:utf-8 -*-

from django.shortcuts import *
from django.contrib.auth.decorators import *

from models import *

import time
import datetime
import random
import sms

def user_from_renren(user):
	return user.is_authenticated()
	
def mobile_verification(request, userprofile, redirect_uri = '/user/init/submit'):
	sms.send_verify(userprofile)
	request.session["mobile"] = userprofile.mobile
	request.session["phone"] = userprofile.phone
	request.session["address"] = userprofile.address
	return HttpResponseRedirect("/user/mobile/verify?id=%s&next=%s"%(userprofile.id, redirect_uri))

def mobile_confirm(request):
	try:
		code = request.GET['code']
		userprofile = UserProfile.objects.get(id = request.GET['id'])
	except:
		return HttpResponse("<font color=red size=2>您输入的验证码错误，请重新输入</font>")
		
	if code != userprofile.verify_code:
		return HttpResponse("<font color=red size=2>您输入的验证码错误，请重新输入</font>")
	
	userprofile.valid = True
	userprofile.save()
	return HttpResponse("//")

def init(request):
	mobile = request.COOKIES.get('mobile', '') 
	phone = request.COOKIES.get('phone', '') 
	address = request.COOKIES.get('address', '') 
	return render_to_response("init.html", locals())

def init_submit(request):
	try:
		mobile = request.POST['mobile']
		phone = request.POST.get('phone', '')
		address = request.POST['address']
	except:
		try:
			mobile = request.session['mobile']
			phone = request.session.get('phone', '')
			address = request.session['address']
		except:
			return render_to_response("error.html", {'message':"您的信息输入有错，请检查后重新提交"})

	try:
		userprofile = UserProfile.objects.get(mobile = mobile)
	except:
		userprofile = UserProfile()
		userprofile.valid = False
	
	userprofile.mobile = mobile
	userprofile.phone = phone
	userprofile.address = address
	userprofile.save()
	
	if userprofile.valid:
		return connect_userprofile(request, userprofile, '/mycoupons')
	else:
		return mobile_verification(request, userprofile, request.path)

def connect_userprofile(request, userprofile, redirect_uri):
	try:
		temp_userprofile = request.user.get_profile()
		if userprofile.name == None or len(userprofile.name) == 0:
			userprofile.add_coupon_by_price(1)
			userprofile.add_coupon_by_price(2)
			userprofile.add_coupon_by_price(3)
			userprofile.add_coupon_by_price(4)
			userprofile.add_coupon_by_price(8)
			
		userprofile.json = temp_userprofile.json
		userprofile.name = temp_userprofile.name
		userprofile.sex = temp_userprofile.sex
		userprofile.avatar = temp_userprofile.avatar
		if temp_userprofile.id != userprofile.id:
			temp_userprofile.delete()
		userprofile.valid = True
		userprofile.user = request.user
		userprofile.save()	
	except:
		return render_to_response("error.html", {'message': "登录信息出错，请重新登录"})
		
	response = HttpResponseRedirect(redirect_uri)
	if userprofile.mobile:
		response.set_cookie('mobile', userprofile.mobile, max_age = 365*24*60*60)
	if userprofile.phone:
		response.set_cookie('phone', userprofile.phone, max_age = 365*24*60*60)
	if userprofile.address:
		userprofile.address = userprofile.address.encode("utf-8")
		userprofile.save()
		response.set_cookie('address', userprofile.address, max_age = 365*24*60*60)
		
	return response

def mylogin(request):
	return render_to_response("login.html", locals())

@user_passes_test(user_from_renren, login_url="/user/login")	
def mycoupons(request):
	try:
		coupons = request.user.get_profile().coupon_set.all().order_by('-id')
	except:
		return HttpResponseRedirect("/user/login")
	return render_to_response('mycoupons.html', locals())

@user_passes_test(user_from_renren, login_url="/user/login")
def exchange_coupon(request):
	try:
		if 'mobile' in request.COOKIES:
			mobile = request.COOKIES['mobile']
		else:
			mobile = request.COOKIES['phone']
		userprofile = UserProfile.objects.get(mobile = mobile) 
	except:
		return render_to_response("error.html", {'message':'无法获得您当前的用户信息'})
		
	try:
		coupontype = CouponType.objects.get(id = int(request.POST['coupontype']))
	except:
		return render_to_response("error.html", {'message':'您选择了错误的抵价券类型'})
		
	if coupontype.exchange_score > userprofile.score:
		return render_to_response("error.html", {'message':'对不起，您的积分不够'})

	userprofile.score -= coupontype.exchange_score
	userprofile.add_coupon(coupontype)
	userprofile.save()
	return HttpResponseRedirect("/mycoupons")
 
@user_passes_test(user_from_renren, login_url="/user/login")
def myscore(request):
	coupontypes = CouponType.objects.all()
	return render_to_response('myscore.html', locals())

def mobile_verify(request):
	userprofile_id = request.GET["id"] 
	redirect_uri = request.GET["next"]
	return render_to_response("mobile.html", locals()) 