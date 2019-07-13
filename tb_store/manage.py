#!/usr/bin/env python
# 启动redis和celery
# redis-server /etc/redis/redis.conf
# celery -A celery_tasks.main worker -l info
# docker run -dti --network=host --name tracker -v /var/fdfs/tracker:/var/fdfs delron/fastdfs tracker
# docker run -dti --network=host --name storage -e TRACKER_SERVER=192.168.11.68:22122 -v /var/fdfs/storage:/var/fdfs delron/fastdfs storage
import os
import sys


if __name__ == "__main__":
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "tb_store.settings.dev")
    try:
        from django.core.management import execute_from_command_line
    except ImportError:
        # The above import may fail for some other reason. Ensure that the
        # issue is really that Django is missing to avoid masking other
        # exceptions on Python 2.
        try:
            import django
        except ImportError:
            raise ImportError(
                "Couldn't import Django. Are you sure it's installed and "
                "available on your PYTHONPATH environment variable? Did you "
                "forget to activate a virtual environment?"
            )
        raise
    execute_from_command_line(sys.argv)
