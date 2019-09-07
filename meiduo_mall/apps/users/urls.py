from django.conf.urls import url
from . import views

urlpatterns = [
    # 注册
    url(r'^register/$', views.RegisterView.as_view(), name='register'),
    url(r'^usernames/(?P<username>[a-zA-Z0-9_]{5,20})/count/$',views.RegisterUsernameCountView.as_view(),name='username'),
    url(r'^mobiles/(?P<mobile>1[3-9]\d{9})/count/$',views.RegisterMobileCountView.as_view(),name='mobile'),
    url(r'^login/$',views.LoginView.as_view(),name='login'),
    url(r'^logout/$',views.LogoutView.as_view(),name='logout'),
    url(r'^info/$',views.UserInfoView.as_view(),name='info'),
    url(r'^emails/$',views.EmailView.as_view(),name='email'),
    url(r'^emails/verification/$',views.VerifyEmailView.as_view(),name='verification'),
    url(r'^addresses/$',views.AddressView.as_view(),name='address'),
    url(r'^addresses/create/$',views.CreateAddressView.as_view(),name='createaddress'),
    url(r'^addresses/(?P<address_id>\d+)/$',views.UpdateDestroyAddressView.as_view(),name='updatedestoryaddress'),
    url(r'^addresses/(?P<address_id>\d+)/default/$',views.DefaultAddressView.as_view(),name='defaultaddress'),
    url(r'^addresses/(?P<address_id>\d+)/title/$',views.UpdateTitleAddressView.as_view(),name='updatetitleaddress'),
    url(r'^changepassword/$',views.ChangePasswordView.as_view(),name='changepassword'),
    url(r'^browse_histories/$',views.UserHistoryView.as_view(),name='history'),
]