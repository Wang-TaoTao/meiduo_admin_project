from django.conf.urls import url
from . import views
urlpatterns = [
    url(r'^qq/login/$',views.QQOauthURLView.as_view(),name='qqurl'),
    url(r'^oauth_callback/$',views.QQOauthUserView.as_view(),name='qquser'),
]