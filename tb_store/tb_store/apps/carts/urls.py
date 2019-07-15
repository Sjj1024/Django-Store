from django.conf.urls import url
from rest_framework.routers import DefaultRouter

from . import views


urlpatterns = [
    url(r'^cart/$', views.CartView.as_view()),
    url(r"^cart/selection/$", views.CartSelectAllView.as_view())
]