import os
from django.core.management.base import BaseCommand
from guolan.fetion.PyFetion import PyFetion
from guolan.sms import send_zuitu
from guolan.models import *
from django.core.files.storage import default_storage
import time

def fetion_login(admin):
	p = PyFetion(admin.fetion, admin.password)
	retry = 0
	while retry < 5:
		try:
			p.login()
			return p
		except:
			retry += 1
			time.sleep(1)
	return None

def send_fetion(admin, p, fetion):
	retry = 0
	while retry < 5:
		try:
			p.send_sms(fetion.message.encode('utf-8'), to = fetion.mobile)
			return True
		except:
			retry += 1
			time.sleep(1)
	return False
			
def send_fetions(admin, path):
	fetions = Sms.objects.filter(sent = False, fetion_or_zuitu = True)
	if len(fetions) == 0:
		return
		
	file(path, "wb")
	p = fetion_login(admin)
	if p == None:
		os.remove(path)
		print datetime.datetime.now().__str__() + "\tlogin error"
		return
		
	sent_count = 0
	for fetion in fetions:
		if send_fetion(admin, p, fetion) == False:
			send_zuitu(fetion.mobile, fetion.message)
			send_zuitu(admin.mobile, "fetion is down")
			print datetime.datetime.now().__str__() + "\tsend error"
			os.remove(path)
			return
		fetion.sent = True
		fetion.save()
		sent_count += 1
		time.sleep(1)
	print datetime.datetime.now().__str__() + "\t%s fetions sent"%sent_count
	os.remove(path)

def send_zuitus(admin, path):
	zuitus = Sms.objects.filter(sent = False, fetion_or_zuitu = False)
	if len(zuitus) == 0:
		return

	file(path, "wb")
	sent_count = 0
	for zuitu in zuitus:
		send_zuitu(zuitu.mobile, zuitu.message)
		zuitu.sent = True
		zuitu.save()
		sent_count += 1
	print datetime.datetime.now().__str__() + "\t%s zuitus sent"%sent_count
	os.remove(path)

class Command(BaseCommand):
	def handle(self,**options):
		#path = default_storage.path('guolanr-fetion-lock')
		path = "/home/doukao/www/fetion.lock"
		admin = AdminCtrl.objects.all()[0]
		
		if os.path.exists(path):
			if datetime.datetime.now().minute % 3 == 0:
				send_zuitus(admin, path)
			print datetime.datetime.now().__str__() + '\t' + path + " locked"
			return
		else:
			try:
				send_zuitus(admin, path)
				send_fetions(admin, path)
			except:
				os.remove(path)
