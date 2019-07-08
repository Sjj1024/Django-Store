from celery_tasks.main import celery_app
from django.core.mail import send_mail
from django.conf import settings


@celery_app.task(name="send_active_email")
def send_verify_email(to_email, verify_url):
    """
    发送验证码邮件
    :return:
    """
    subject = "淘宝商城邮箱验证"
    html_message = '<p>尊敬的用户您好！</p>' \
                   '<p>感谢您使用淘宝商城。</p>' \
                   '<p>您的邮箱为：%s 。请点击此链接激活您的邮箱：</p>' \
                   '<p><a href="%s">请点击链接以确认</a></p>' % (to_email, verify_url)
    send_mail(subject, "", settings.EMAIL_FROM, [to_email], html_message=html_message)
    print("邮箱发送成功")
