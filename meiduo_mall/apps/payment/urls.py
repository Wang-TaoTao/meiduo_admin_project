from django.conf.urls import url
from apps.payment import views

urlpatterns = [

    url(r'^payment/(?P<order_id>\d+)/$',views.PaymentView.as_view(),name='payment'),
    url(r'^payment/status/$',views.PaymentStatusView.as_view(),name='status'),
]