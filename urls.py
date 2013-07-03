from django.conf.urls.defaults import patterns, include, url

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    url(r'^$', 'guolan.views.index'),
    url(r'^checkout$', 'guolan.views.checkout'),
    url(r'^submit$', 'guolan.views.submit'),
    url(r'^myorders$', 'guolan.views.myorders'),
    url(r'^mycoupons$', 'guolan.user.mycoupons'),
    url(r'^myscore$', 'guolan.user.myscore'),
    url(r'^evaluation$', 'guolan.views.evaluation'),
 
    # renren login   
    url(r'^renrenlogout$', 'guolan.renren.renren_logout'),
    url(r'^renrenlogin$', 'guolan.renren.renren_login'),
    url(r'^oauth_redirect$', 'guolan.renren.renren_oauth'),
        
    # user infomation
    url(r'^user/init$', 'guolan.user.init'),
    url(r'^user/init/submit$', 'guolan.user.init_submit'),
    url(r'^user/login$', 'guolan.user.mylogin'),
    url(r'^user/mobile/confirm$', 'guolan.user.mobile_confirm'),
    url(r'^user/mobile/verify$', 'guolan.user.mobile_verify'),
    url(r'^user/coupon/exchange$','guolan.user.exchange_coupon'),
   
    # cart
    url(r'^cart/add$', 'guolan.cart.add'),
    url(r'^cart/del$', 'guolan.cart.delete'),
    url(r'^cart/clear$', 'guolan.cart.clear'),
    url(r'^cart/show$', 'guolan.cart.show'),
    url(r'^cart/remove$', 'guolan.cart.remove'),
    url(r'^cart/update$', 'guolan.cart.update'),
    url(r'^cart/coupon$', 'guolan.cart.coupon'),
    
    # myadmin
    url(r'^myadmin/fruit$', 'guolan.myadmin.fruit'),
    url(r'^myadmin/sold_out$', 'guolan.myadmin.sold_out'),
    url(r'^myadmin/top$', 'guolan.myadmin.top'),
    url(r'^myadmin/$', 'guolan.myadmin.index'),


    # Uncomment the next line to enable the admin:
    url(r'^admin/', include(admin.site.urls)),
    
    # url(r'^guolan/', include('guolan.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),
)

