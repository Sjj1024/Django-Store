from django.db import models


class BaseModel(models.Model):
    """
    为模型类补充字段
    """
    create_time = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")
    update_time = models.DateTimeField(auto_now=True, verbose_name="更新时间")

    class Mate:
        abstract = True  # 指明是抽象类模型，用于集成

