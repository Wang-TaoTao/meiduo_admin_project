from django.conf.urls import url
from apps.orders import views

urlpatterns = [
    url(r'^place/$',views.OrderSettlementView.as_view(),name='settle'),
    url(r'^orders/commit/$',views.OrderCommitView.as_view(),name='commit'),
    url(r'^orders/success/$',views.OrderSuccessView.as_view(),name='success'),

]