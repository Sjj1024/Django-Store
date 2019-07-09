from django.conf.urls import url
from rest_framework.routers import DefaultRouter

from . import views

urlpatterns = [

]

router = DefaultRouter()
router.register(r'areas', views.AreasViewSet, base_name='areas')

urlpatterns += router.urls

