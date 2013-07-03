# -*- coding: utf-8 -*-
from models import *
import urllib
import time
import random

def send(to, content, fetion_or_zuitu):
	if len(to) != 11:
		return
	sms = Sms()
	sms.fetion_or_zuitu = fetion_or_zuitu
	sms.mobile = to
	sms.message = content
	sms.sent = False
	sms.save()

def send_fetion(to, content):
	send(to, content, True)

def send_zuitu(to, content):
	if len(to) != 11:
		return False
	
	# sensitive words filter
	items = SensitiveItem.objects.all()
	for item in items:
		content = content.replace(item.word, item.replace)
		
	admin = AdminCtrl.objects.all()[0]
	url = admin.zuitu.replace("PHONE_NUMBER", to).replace("MESSAGE_CONTENT", content);
	url = url.encode("utf-8")
	try:
		data = urllib.urlopen(url).read()
	except IOError:
		try:
			time.sleep(1)
			data = urllib.urlopen(url).read()
		except IOError:
			log = ErrorLog()
			log.content = "最土发送时出现IOError"
			log.save()
			send_fetion(admin.mobile, '最土发送失败，请查看Error Logs数据库')
			return False
			
	if data == "+OK":
		return True
		
	log = ErrorLog()
	log.content = "最土发送失败，错误类型：%s"%pagevalue
	log.save() 
	send_fetion(admin.mobile, '最土发送失败，请查看Error Logs数据库')
	
	return False

def send_mobile(mobile, msg):
	if mobile.send_fetion:
		send(mobile.number, msg, True)
	if mobile.send_zuitu:
		send(mobile.number, msg, False)

def send_mobiles(mobiles, msg):
	for mobile in mobiles:
		send_mobile(mobile, msg)

def send_order(order):
	admin = AdminCtrl.objects.all()[0]
	send(admin.mobile, order.sms(), True)
	send_mobiles(order.school.mobiles.all(), order.sms())
		
def send_verify(userprofile):
	userprofile.verify_code = random.randint(1000, 9999)
	userprofile.save()
	msg = u"您在果篮儿网的验证码为：%s"%(userprofile.verify_code)
	send_zuitu(userprofile.mobile, msg)
	
def send_urge(order):
	if order.urge_count_left <= 0:
		return False
	order.urge_count_left -= 1
	order.save()
	msg = u"订单号%d(%s, %.1f元,下单时间%s-%s %s:%s)催促您尽快配送"%(
		order.school_order_id, order.mobile, order.pay_price(),
		order.datetime.month, order.datetime.day, order.datetime.hour, order.datetime.minute)
	send_mobiles(order.school.mobiles.all())

