from django.db import models
from django.contrib.auth.models import AbstractUser


# Create your models here.

class User(AbstractUser):
    """
    用户模型类
    """
    mobile = models.CharField(max_length=11, unique=True, verbose_name="手机号")
    email_active = models.BooleanField(default=False, verbose_name='邮箱验证状态')

    # 添加额外说明，flask中的__table__也是这个作用
    class Meta:
        db_table = "tb_users"
        verbose_name = "用户"
        # 显示有用户名的时候，不以复数形式显示
        verbose_name_plural = verbose_name
