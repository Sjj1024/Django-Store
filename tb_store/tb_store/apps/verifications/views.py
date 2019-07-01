from django.shortcuts import render
from django.http import HttpResponse
from django_redis import get_redis_connection
from rest_framework.views import APIView
from tb_store.libs.captcha.captcha import captcha

from verifications import constants
# Create your views here.

class ImageCodeView(APIView):
    def get(self, request, image_code_id):
        # 接收参数校验参数,这一步已经在ｕｒｌ匹配中实现了
        # 生成图片验证码
        text, image = captcha.generate_captcha()
        redis_conn = get_redis_connection('verify_codes')
        redis_conn.setex('img_%s' % image_code_id, constants.IMAGE_CODE_REDIS_EXPIRES, text)

        # 返回给前端数据
        return HttpResponse(image, content_type='image/jpg')
