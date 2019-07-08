from django.shortcuts import render

# Create your views here.
from rest_framework.viewsets import ReadOnlyModelViewSet

from areas.models import Area
from areas.serializers import AreaSerializer, SubAreaSerializer


class AreasViewSet(ReadOnlyModelViewSet):
    """
    行政区划信息
    """
    pagination_class = None

    def get_queryset(self):
        """
        提供数据集
        :return:
        """
        if self.action == "list":
            return Area.objects.filter(parent=None)
        else:
            return Area.objects.all()

    def get_serializer_class(self):
        """
        提供序列化器
        :return:
        """
        if self.action == "list":
            return AreaSerializer
        else:
            return SubAreaSerializer