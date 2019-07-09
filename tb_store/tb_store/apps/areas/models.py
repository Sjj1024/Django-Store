from django.db import models


# Create your models here.
from tb_store.utils.models import BaseModel
from users.models import User


class Area(models.Model):
    """
    收货地址模型类
    """
    name = models.CharField(max_length=20, verbose_name='名称')
    parent = models.ForeignKey('self', on_delete=models.SET_NULL, related_name='subs', null=True, blank=True,
                               verbose_name='上级行政区划')

    class Meta:
        db_table = "tb_areas"
        verbose_name = "行政区划"
        verbose_name_plural = "行政区划"

    def __str__(self):
        return self.name
