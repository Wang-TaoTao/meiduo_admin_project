from django.conf.urls import url
from . import views
from rest_framework_jwt.views import obtain_jwt_token
urlpatterns = [


    url(r'^authorizations/$', views.IndexAPIView.as_view()),
]