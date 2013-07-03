# -*- coding:utf-8 -*-
from django.contrib import admin
from django.shortcuts import *
from models import *

from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin

class UserProfileInline(admin.StackedInline):
    model = UserProfile

class UserProfileAdmin(UserAdmin):
    inlines = [UserProfileInline,]
    
class DeliveryTimeIntervalAdmin(admin.ModelAdmin):
	list_display = ("today", "stop_order_time", "start_time", "end_time")

class SmsAdmin(admin.ModelAdmin):
	list_display = ("sent", "fetion_or_zuitu", "mobile", "message", "datetime")
	search_fields = ('mobile', )
	date_hierarchy = 'datetime'

class OrderAdmin(admin.ModelAdmin):
	list_display = ("today", "delivery_start_time", "delivery_end_time", "mobile", "content", "datetime")
	search_fields = ('mobile', )
	date_hierarchy = 'datetime'
	raw_id_fields = ('userprofile', ) 

class EvaluationAdmin(admin.ModelAdmin):
	list_display = ("order", "general", "remark", "datetime")
	list_filter = ("general", )
	date_hierarchy = 'datetime'
	
class UserProfileAdmin(admin.ModelAdmin):
	list_display = ("id", "name", "sex", "mobile", "address", "order_count", "coupon_count", "verify_code")
	list_filter = ("sex", )

class FruitAdmin(admin.ModelAdmin):
	list_display = ("name", "valid", "price", "min_price", "max_price", "unit", "least", "order")
	ordering = ("-valid", "order")
	
class SchoolAdmin(admin.ModelAdmin):
	filter_horizontal = ('mobiles', )

admin.site.register(DeliveryTimeInterval, DeliveryTimeIntervalAdmin)
admin.site.register(Sms, SmsAdmin)
admin.site.register(Order, OrderAdmin)
admin.site.register(Evaluation, EvaluationAdmin)
admin.site.register(UserProfile, UserProfileAdmin)
admin.site.register(Fruit, FruitAdmin)
admin.site.register(School, SchoolAdmin)

admin.site.register(Category)
admin.site.register(DeliveryAddress)
admin.site.register(OrderStatus)
admin.site.register(Visitor)
admin.site.register(SensitiveItem)
admin.site.register(Coupon)
admin.site.register(CouponType)
admin.site.register(AdminCtrl)
admin.site.register(ErrorLog)
admin.site.register(Mobile)

