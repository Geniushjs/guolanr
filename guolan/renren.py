# -*- coding:utf-8 -*-
from django.shortcuts import *
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.models import User
from models import *

import json
import urllib
import base64
import Cookie
import email.utils
import hashlib
import hmac
import logging
import os.path
import time

RENREN_APP_API_KEY = "0876e2603155434c9669fcba274dc503"
RENREN_APP_SECRET_KEY = "8f907670df284e65a926b28f6528e014"

RENREN_AUTHORIZATION_URI = "http://graph.renren.com/oauth/authorize"
RENREN_ACCESS_TOKEN_URI = "http://graph.renren.com/oauth/token"
RENREN_SESSION_KEY_URI = "http://graph.renren.com/renren_api/session_key"
RENREN_API_SERVER = "http://api.renren.com/restserver.do"
RENREN_GRANT_URI = "http://graph.renren.com/oauth/grant"

class RenRenAPIClient(object):
    def __init__(self, session_key = None, api_key = None, secret_key = None):
        self.session_key = session_key
        self.api_key = api_key
        self.secret_key = secret_key
    def request(self, params = None):
        """Fetches the given method's response returning from RenRen API.

        Send a POST request to the given method with the given params.
        """
        params["api_key"] = self.api_key
        params["call_id"] = str(int(time.time() * 1000))
        params["format"] = "json"
        params["session_key"] = self.session_key
        params["v"] = '1.0'
        sig = self.hash_params(params);
        params["sig"] = sig
        
        post_data = None if params is None else urllib.urlencode(params)
        
        #logging.info("request params are: " + str(post_data))
        
        file = urllib.urlopen(RENREN_API_SERVER, post_data)
        
        try:
            s = file.read()
            logging.info("api response is: " + s)
            response = json.loads(s)
        finally:
            file.close()
        if type(response) is not list and response["error_code"]:
            logging.info(response["error_msg"])
            raise RenRenAPIError(response["error_code"], response["error_msg"])
        return response
    def hash_params(self, params = None):
        hasher = hashlib.md5("".join(["%s=%s" % (self.unicode_encode(x), self.unicode_encode(params[x])) for x in sorted(params.keys())]))
        hasher.update(self.secret_key)
        return hasher.hexdigest()
    def unicode_encode(self, str):
        """
        Detect if a string is unicode and encode as utf-8 if necessary
        """
        return isinstance(str, unicode) and str.encode('utf-8') or str

def renren_login(request):
	args = dict(client_id = RENREN_APP_API_KEY,
					response_type = "code", 
					display = "page",
					secure = "true",
					redirect_uri = "http://guolanr.com/oauth_redirect")
	return HttpResponseRedirect(RENREN_GRANT_URI + "?" + urllib.urlencode(args))

def renren_oauth(request):
	args = dict(code = request.GET.get('code'), 
					client_id = RENREN_APP_API_KEY, 
					client_secret = RENREN_APP_SECRET_KEY,
					redirect_uri = "http://guolanr.com/oauth_redirect",
					grant_type = "authorization_code")
	f = urllib.urlopen(RENREN_ACCESS_TOKEN_URI + "?" + urllib.urlencode(args)).read()
	json_content = json.loads(f)
	
	args = dict(oauth_token = json_content['access_token'])
	f = urllib.urlopen(RENREN_SESSION_KEY_URI + "?" + urllib.urlencode(args)).read()	
	json_content = json.loads(f)
	
	session_key = json_content["renren_token"]["session_key"]
	api_client = RenRenAPIClient(session_key, RENREN_APP_API_KEY, RENREN_APP_SECRET_KEY)
	params = {"method": "users.getInfo", "fields": ""}
	response = api_client.request(params)
	
	if type(response) is list:
		response = response[0]
	
	username = "renren@%s"%response["uid"]
	if not User.objects.filter(username = username).exists():
		user = User()
		user.username = username
		user.set_password(username)
		user.save()
		userprofile = UserProfile()
		userprofile.user = user
		userprofile.save()
		
	user = authenticate(username = username, password = username)
	
	try:
		userprofile = user.get_profile()
	except:
		userprofile = UserProfile()
		userprofile.user = user
		userprofile.save()
				
	userprofile.name = response["name"]
	if response["sex"] == 1:
		userprofile.sex = True
	else: 
		userprofile.sex = False
	userprofile.avatar = response["headurl"]
	userprofile.json = json.dumps(response)
	userprofile.save()
	
	if userprofile.mobile and len(userprofile.mobile) != 0 and userprofile.valid:
		response = HttpResponseRedirect("/")
	else:
		response = HttpResponseRedirect("/user/init")
		
	if userprofile.mobile:
		response.set_cookie('mobile', userprofile.mobile, max_age = 365*24*60*60)
	if userprofile.phone:
		response.set_cookie('phone', userprofile.phone, max_age = 365*24*60*60)
	if userprofile.address:
		userprofile.address = userprofile.address.encode("utf-8")
		userprofile.save()
		response.set_cookie('address', userprofile.address, max_age = 365*24*60*60)
		
	login(request, user)
	return response
		
def renren_logout(request):
	logout(request)
	return HttpResponseRedirect("/")
