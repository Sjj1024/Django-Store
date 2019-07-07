from celery import Celery

# 为celery使用django配置文件进行设置
import os
if not os.getenv('DJANGO_SETTINGS_MODULE'):
    os.environ['DJANGO_SETTINGS_MODULE'] = 'tb_store.settings.dev'


# 创建celery对象
celery_app = Celery("store")

# 导入celery配置
celery_app.config_from_object("celery_tasks.config")

# 导入任务
celery_app.autodiscover_tasks(["celery_tasks.sms", "celery_tasks.email"])