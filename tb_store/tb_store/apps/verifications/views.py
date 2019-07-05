import random
import logging
from django.shortcuts import render
from django.http import HttpResponse
from django_redis import get_redis_connection
from rest_framework import status
from rest_framework.generics import GenericAPIView
from rest_framework.response import Response
from rest_framework.views import APIView
from tb_store.libs.captcha.captcha import captcha
from tb_store.utils.yuntongxun.sms import CCP

from verifications import constants, serializers
from celery_tasks.sms.tasks import send_sms_code


# Create your views here.
logger = logging.getLogger('django')

class ImageCodeView(APIView):
    def get(self, request, image_code_id):
        # 接收参数校验参数,这一步已经在ｕｒｌ匹配中实现了
        # 生成图片验证码
        text, image = captcha.generate_captcha()
        redis_conn = get_redis_connection('verify_codes')
        redis_conn.setex('img_%s' % image_code_id, constants.IMAGE_CODE_REDIS_EXPIRES, text)
        print(text)

        # 返回给前端数据
        return HttpResponse(image, content_type='image/jpg')


class SMSCodeView(GenericAPIView):
    """
    短信验证码接口
    """
    serializer_class = serializers.ImageCodeCheckSerializer

    def get(self, request, mobile):
        """
        创建短信验证码
        """
        # 判断图片验证码, 判断是否在60s内
        serializer = self.get_serializer(data=request.query_params)
        serializer.is_valid(raise_exception=True)

        # 生成短信验证码
        sms_code = "%06d" % random.randint(0, 999999)

        # 保存短信验证码与发送记录,使用redis管道
        redis_conn = get_redis_connection('verify_codes')
        pl = redis_conn.pipeline()
        pl.setex("sms_%s" % mobile, constants.SMS_CODE_REDIS_EXPIRES, sms_code)
        pl.setex("send_flag_%s" % mobile, constants.SEND_SMS_CODE_INTERVAL, 1)
        # 让管道通知redis执行命令
        pl.execute()

        # 发送短信验证码
        # try:
        #     sms_code_expires = str(constants.SMS_CODE_REDIS_EXPIRES // 60)
        #     ccp = CCP()
        #     result = ccp.send_template_sms(mobile, [sms_code, sms_code_expires], constants.SMS_CODE_TEMP_ID)
        # except Exception as e:
        #     logger.info("发送验证码异常mobile:%s, message:%s" % (mobile, e), status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        # else:
        #     if result == 0:
        #         logger.info("发送验证码短信正常mobile:%s" % mobile)
        #         return Response({"message": "OK"})
        #     else:
        #         logger.warning("发送短信验证码失败mobile:%s" % mobile)
        #         return Response({"message": "failed"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        # 使用celery队列发送短信验证码
        sms_code_expires = str(constants.SMS_CODE_REDIS_EXPIRES // 60)
        send_sms_code.delay(mobile, sms_code, sms_code_expires)
        print(sms_code)
        return Response({"message": "OK"})