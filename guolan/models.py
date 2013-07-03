#-*- coding: utf-8 -*-

from django.contrib.auth.models import User
from django.db import models
import datetime

# Create your models here.
class AdminCtrl(models.Model):
	close_website = models.BooleanField("关闭全站", default = False)
	test_mode = models.BooleanField("测试模式", default = False)
	mobile = models.CharField("监控手机", max_length = 11)
	fetion = models.CharField("飞信手机", max_length = 11)
	password = models.CharField("飞信密码", max_length = 100)
	zuitu = models.URLField("最土地址")
	public = models.TextField("首页公告", blank = True)
	service_begin_time = models.TimeField('客服服务开始时间')
	service_end_time = models.TimeField('客服服务结束时间')
	qq = models.CharField('QQ', max_length = 20)
	email = models.EmailField('Email', max_length = 255)
	service_phone = models.CharField('客服电话', max_length = 20)
	
	def __str__(self):
		return self.__unicode__()
	def __unicode__(self):
		return u"关闭网站:%s 测试模式:%s 短信监控:%s 飞信帐号:%s"%(
		self.close_website, self.test_mode, self.mobile, self.fetion)	
		
class Mobile(models.Model):
	name = models.CharField("机主", max_length = 30)
	number = models.CharField("号码", max_length = 11)
	send_fetion = models.BooleanField("发送飞信")
	send_zuitu = models.BooleanField("发送最土")
	def __str__(self):
		return self.__unicode__()
	def __unicode__(self):
		return u"%s %s f:%d z:%d"%(self.name, self.number, self.send_fetion, self.send_zuitu)

class School(models.Model):
	mobiles = models.ManyToManyField(Mobile, verbose_name = u'电话', blank = True, null = True)

	valid = models.BooleanField(u"是否生效", default = True) 
	name = models.CharField(u"名称", max_length = 255)
	description = models.TextField(u"描述", blank = True, null = True)
	speed = models.IntegerField("送餐速度", default = 40)
	latitude = models.FloatField("纬度lat", default = 39.99150077)
	longitude = models.FloatField("经度lng", default = 116.309251)
	zoom = models.IntegerField("缩放", default = 14)
	total_order_count = models.IntegerField("总订单数", default = 0)
	delay_open_datetime = models.DateTimeField('延迟开启时间', default = datetime.datetime.now())
	temporarily_closed_reason = models.CharField("临时关闭原因", max_length = 255, blank = True)

	def next_order_id(self):
		self.total_order_count += 1
		self.save()
		order_id = self.total_order_count % 1000 + self.id * 1000
		return order_id 
		
	def temporarily_closed(self):
		return datetime.datetime.now() < self.delay_open_datetime 
		
	def delay(self, timedelta, reason):
		self.delay_open_datetime = datetime.datetime.now() + timedelta
		self.temporarily_closed_reason = reason
		self.save()

	def sold_out_count(self):
		items = self.menuitem_set.all()
		count = 0
		for item in items:
			if item.sold_out():
				count += 1
		return count

	def estimate_speed(self):
		return self.speed + 7 * self.waiting_order_count(30);
	
	def average_speed(self):
		evas = self.evaluation_set.filter(success = True)
		total = 0
		for eva in evas:
			total += eva.speed
		return (total+10*self.speed)/(len(evas)+10)

	def evaluation_count(self, general):
		return self.evaluation_set.filter(general = general).count()

	def good_evaluation_count(self):
		return self.evaluation_count(1) 

	def normal_evaluation_count(self):
		return self.evaluation_count(2) 

	def bad_evaluation_count(self):
		return self.evaluation_count(3) 
	
	def __str__(self):
		return self.__unicode__()
	def __unicode__(self):
		return '%s'%(self.name)	

class Category(models.Model):
	name = models.CharField(u"名称", max_length = 255)
	description = models.TextField(u"描述", blank = True)
	def __str__(self):
		return self.__unicode__()
	def __unicode__(self):
		return u"%s"%(self.name)
	
class Fruit(models.Model):
	# 基本信息
	valid = models.BooleanField(u"是否显示", default = True)
	category = models.ForeignKey(Category, verbose_name = "所属类别")
	school = models.ForeignKey(School, verbose_name = "所属学校")
	
	name = models.CharField("名称", max_length = 255)
	description = models.TextField("描述", blank = True)
	cost = models.FloatField(u"成本")
	price = models.FloatField(u"价格")
	min_weight = models.FloatField(u"重量区间下")
	max_weight = models.FloatField(u"重量区间上")
	unit = models.CharField(u"规格", default = "500g", max_length = 100)
	order = models.IntegerField(u"顺序", help_text = u"从小到大排列", default = 0)
	image_small = models.ImageField(u"小图", upload_to = 'images/fruit/')
	image_large = models.ImageField(u"大图", upload_to = 'images/fruit/', blank = True, null = True)
	least = models.IntegerField("最少点几份")

	# 统计信息
	stock = models.PositiveIntegerField(u"库存", blank = True, null = True)
	order_count = models.IntegerField("被点次数", default = 0)
	sold_out_datetime = models.DateTimeField('下次上架时间', default = datetime.datetime.now(), blank = True, null = True)
	
	def min_price(self):
		return self.price * self.min_weight * 2 / 1000.0

	def max_price(self):
		return self.price * self.max_weight * 2 / 1000.0
		
	def sold_out(self):
		return self.sold_out_datetime >= datetime.datetime.now()
		
	def __str__(self):
		return self.__unicode__()
	def __unicode__(self):
		return u"%s"%(self.name)

class DeliveryTimeInterval(models.Model):
	today = models.BooleanField(u"今天", default = True)
	stop_order_time = models.TimeField()
	start_time = models.TimeField()
	end_time = models.TimeField()

	def is_today(self):
		if self.today:
			return u"今天"
		else:
			return u"明天"
	def __str__(self):
		return self.__unicode__()
	def __unicode__(self):
		if self.today:
			return u'今天 %s-%s'%(self.start_time, self.end_time)
		else:
			return u'明天 %s-%s'%(self.start_time, self.end_time)
	
class DeliveryAddress(models.Model):
	mobile = models.CharField("手机", max_length = 11)
	phone = models.CharField('备用电话', max_length = 20, blank = True)
	address = models.CharField("地址", max_length = 255)

	def __str__(self):
		return self.__unicode__()
	def __unicode__(self):
		return '%s %s %s'%(self.mobile, self.phone, self.address)	

class UserProfile(models.Model):
	valid = models.BooleanField("验证通过", default = True)
	verify_code = models.CharField("短信验证码", max_length = 20, blank=True, null=True)
	
	school = models.ForeignKey(School, verbose_name = "所属地区", blank = True, null=True)

	mobile = models.CharField("手机", max_length = 11, blank=True, null=True)
	phone = models.CharField('备用电话', max_length = 20, blank = True) 	
	address = models.CharField("地址", max_length = 255, blank=True, null=True)
	addresses = models.ManyToManyField(DeliveryAddress, verbose_name = u'配送地址', blank = True, null = True)

	score = models.IntegerField("积分", default = 0, blank=True, null=True)

	ip = models.IPAddressField("最后一次IP地址", max_length=20, blank=True, null=True)
	order_datetime = models.DateTimeField("最后一次点餐时间", blank = True, null = True)
	register_datetime = models.DateTimeField("注册时间", blank = True, null = True)

	user = models.OneToOneField(User, blank = True, null = True)
	
#	infomation from renren
	json = models.TextField('人人资料', blank = True, null = True)
	name = models.CharField('姓名', max_length = 255, blank = True, null = True) 
	sex = models.NullBooleanField('性别', choices = ((True, '男'), (False, '女')), blank = True, null = True)
	avatar = models.URLField('头像', blank = True, null = True)
	
	def add_coupon(self, coupontype):
		coupon = Coupon()
		coupon.type = coupontype
		coupon.userprofile = self
		coupon.expire_date = datetime.date.today() + datetime.timedelta(days = 30)
		coupon.save()
	
	def add_coupon_by_price(self, price):
		coupontype = CouponType.objects.filter(price = price, least_consumption__gt = 0)[0]
		self.add_coupon(coupontype)
	
	def has_coupontype(self, coupontype):
		return self.coupon_set.filter(type = coupontype, expire_date__gte = datetime.date.today()).count() > 0

	def order_count(self):
		return self.order_set.filter(valid = True).count()
		
	def coupon_count(self):
		for coupon in self.coupon_set.all():
			if coupon.expire_date < datetime.date.today():
				coupon.delete()
		return self.coupon_set.all().count()
		
	def __str__(self):
		return self.__unicode__()
	def __unicode__(self):
		return u"%s %s"%(self.mobile, self.address)

class Order(models.Model):
	school = models.ForeignKey(School, verbose_name = "配送学校", blank = True, null = True)  
	userprofile = models.ForeignKey(UserProfile, verbose_name = "订餐用户", blank = True, null = True)

	school_order_id = models.PositiveIntegerField("订单号") 
	valid = models.BooleanField("成功交易", default = True)
	evaluated = models.BooleanField('已评价', default = False)
	confirm = models.BooleanField('已确认', default = False)
	
	mobile = models.CharField("顾客电话", max_length = 11)
	phone = models.CharField('备用电话', max_length = 20, blank = True)
	address = models.TextField("顾客地址")
	remark = models.TextField("顾客留言", blank = True)
	content = models.TextField("订单内容")
	datetime = models.DateTimeField("下单时间")
	today = models.BooleanField("今天配送", default = True)
	delivery_start_time = models.TimeField("配送起始时间")
	delivery_end_time = models.TimeField("配送结束时间")

	price = models.FloatField("总价格", default = 0)
	min_total = models.FloatField("价格区间下", default = 0)
	max_total = models.FloatField("价格区间上", default = 0)
	customer_total = models.FloatField("顾客确认价格", default = 0)
	cost_total = models.FloatField("成本价格", default = 0)
	discount_price = models.IntegerField('优惠价格', default = 0)
	delivery_fee = models.IntegerField("外送费", default = 0)
	
	urge_count_left = models.IntegerField("剩余催促次数", default = 3)
	estimate_speed = models.IntegerField("预计送餐时间", blank = True, null = True, default = 30)
	
	def delivery_today(self):
		today = datetime.date.today()
		return self.delivery_datetime().month == today.month and self.delivery_datetime().day == today.day
		
	def delivery_datetime(self):
		my_datetime = datetime.datetime(year = self.datetime.year, month = self.datetime.month,
			day = self.datetime.day, hour = self.delivery_start_time.hour, minute = self.delivery_start_time.minute)  
		if not self.today:
			my_datetime += datetime.timedelta(days = 1)
		return my_datetime  
		
	def min_pay(self):
		return self.min_total - self.discount_price + self.delivery_fee

	def max_pay(self):
		return self.max_total - self.discount_price + self.delivery_fee
		
	def add_status(self, who, message):
		status = OrderStatus()
		status.message = message
		status.datetime = datetime.datetime.now()
		status.who = who
		status.order = self
		status.save()

	def is_today(self):
		if self.today:
			return u"今天"
		else:
			return u"明天"

	def sms(self):
		return u"%d-%s%s:%s到%s:%s之间配送[价格区间%s~%s元, 扣%s元抵价券, 运费%s元]%s,%s%s[%s]%s"%(
			self.school_order_id, self.is_today(),
			self.delivery_start_time.hour, self.delivery_start_time.minute,
			self.delivery_end_time.hour, self.delivery_end_time.minute,
			self.min_total, self.max_total, self.discount_price, self.delivery_fee, 
			self.mobile, self.phone, self.address, self.content, self.remark) 
		
	def __str__(self):
		return self.__unicode__()
	def __unicode__(self):
		return u"%s(%s) %s %s %s"%(self.id, self.school_order_id, self.mobile, self.address, self.content)

class Evaluation(models.Model):
	order = models.ForeignKey(Order, verbose_name = u'订单号')
	general = models.IntegerField('总体评价', choices = ((1, '好评'), (0, '中评'), (-1, '差评')), default = 1)
	remark = models.TextField('用户留言', blank = True, help_text = "您有任何的体会,建议或投诉，请给我们留言，我们将在未来的某个时刻给予热心的顾客优惠回报或礼品：")
	datetime = models.DateTimeField('评价时间')
	
	def __str__(self):
		return self.__unicode__()
	def __unicode__(self):
		return u"订单号[%d] 评价[%d] 留言[%s]"%(self.order.id, self.general, self.remark)

class OrderStatus(models.Model):
	order = models.ForeignKey(Order, verbose_name = '所属订单')
	datetime = models.DateTimeField('日期') 
	message = models.CharField('信息', max_length = 255)
	who = models.IntegerField('消息发出者', choices = ((0, '系统'), (1, '客服'), (2, '顾客')), default = 0) 
	def __str__(self):
		return self.__unicode__()
	def __unicode__(self):
		return u"%s %s"%(self.datetime, self.message)

class SensitiveItem(models.Model):
	word = models.CharField(verbose_name = '敏感词', max_length = 255)
	replace = models.CharField(verbose_name = '替换词', max_length = 255)
	def __str__(self):
		return self.__unicode__()
	def __unicode__(self):
		return u"%s %s"%(self.word, self.replace)

class Visitor(models.Model):
	ip = models.IPAddressField(verbose_name = "IP")
	address = models.CharField(verbose_name = "地址", max_length = 255)
	datetime = models.DateTimeField(verbose_name = "访问时间", auto_now = True)
	school = models.ForeignKey(School, verbose_name = '访问地区', null = True, blank = True)
	def __str__(self):
		return self.__unicode__()
	def __unicode__(self):
		return u"%s %s %s"%(self.datetime, self.ip, self.address)

class Sms(models.Model):
	mobile = models.CharField("目标手机", max_length=20)
	message = models.TextField("发送内容")
	datetime = models.DateTimeField("发送时间", auto_now=True)
	sent = models.BooleanField("已发送", default = False)
	fetion_or_zuitu = models.BooleanField("发飞信还是最土", default = True)
	def __str__(self):
		return self.__unicode__()
	def __unicode__(self):
		return u"[%s] %s %s"%(self.datetime, self.mobile, self.message)

class CouponType(models.Model):
	price = models.PositiveIntegerField('价格')
	least_consumption = models.PositiveIntegerField('最低消费')
	exchange_score = models.PositiveIntegerField('所需积分')
	def __str__(self):
		return self.__unicode__()
	def __unicode__(self):
		if self.least_consumption == 0:
			return u"%s元,不限额抵价券"%(self.price)
		else:
			return u"%s元,满%s元可使用,需%s积分可换取"%(self.price, self.least_consumption, self.exchange_score)

class Coupon(models.Model):
	type = models.ForeignKey(CouponType, verbose_name = '代金券类型')
	expire_date = models.DateField('有效期', default = datetime.date.today() + datetime.timedelta(days = 30))
	userprofile = models.ForeignKey(UserProfile, verbose_name = '所属用户', blank = True, null = True)
	
	def valid(self):
		return self.expire_date >= datetime.date.today()
	def __str__(self):
		return self.__unicode__()
	def __unicode__(self):
		return u'%s元,消费%s元可以使用,%s过期'%(self.type.price, self.type.least_consumption, self.expire_date)

class ErrorLog(models.Model):
	content = models.TextField("错误内容")
	datetime = models.DateTimeField("出错时间", auto_now = True)
	
	def __str__(self):
		return self.__unicode__()
	def __unicode__(self):
		return u"%s %s"%(self.datetime, self.content)
