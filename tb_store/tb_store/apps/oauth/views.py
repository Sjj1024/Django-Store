from django.shortcuts import render

# Create your views here.
from rest_framework import status
from rest_framework.generics import CreateAPIView
from rest_framework.response import Response
from rest_framework.settings import api_settings
from rest_framework.views import APIView

from oauth.exceptions import OAuthQQAPIError
from oauth.models import OAuthQQUser
from oauth.serializers import OAuthQQUserSerializer
from oauth.utils import OAuthQQ


class QQAuthURLView(APIView):
    """
    获取ｑｑ登录的ｕｒｌ
    """

    def get(self, request):
        """
        提供ｑｑ登录的ｕｒｌ
        :param request:
        :return:
        """
        next = request.query_params.get("next")
        oauth = OAuthQQ(state=next)
        login_url = oauth.get_qq_login_url()
        return Response({'login_url': login_url})


class QQAuthUserView(CreateAPIView):
    """
    用与ｑｑ登录的用户:?code=XXX
    """
    serializer_class = OAuthQQUserSerializer

    def get(self, request):
        # 获取ｃｏｄｅ
        code = request.query_params.get("code")
        if not code:
            return Response({"message": "缺少code"}, status=status.HTTP_400_BAD_REQUEST)
        oauth_qq = OAuthQQ()

        try:
            # 凭借ｃｏｄｅ获取access_token
            access_token = oauth_qq.get_access_token(code)
            # 凭借access_token获取openid
            openid = oauth_qq.get_openid(access_token)
        except OAuthQQAPIError:
            return Response({"message": "QQ服务异常"}, status=status.HTTP_503_SERVICE_UNAVAILABLE)

        try:
            qq_user = OAuthQQUser.objects.get(openid=openid)
        except OAuthQQUser.DoesNotExist:
            # 如果数据不存在，处理openid并返回
            token = oauth_qq.generate_save_user_token(openid)
            return Response({"access_token": token})
        else:
            # 如果数据存在，表示用户已经绑定过身份,签发ＪＷＴ　ｔｏｋｅｎ
            # 找到用户, 生成token
            user = qq_user.user
            jwt_payload_handler = api_settings.JWT_PAYLOAD_HANDLER
            jwt_encode_handler = api_settings.JWT_ENCODE_HANDLER

            payload = jwt_payload_handler(user)
            token = jwt_encode_handler(payload)

            response = Response({
                'token': token,
                'user_id': user.id,
                'username': user.username
            })
            return response


