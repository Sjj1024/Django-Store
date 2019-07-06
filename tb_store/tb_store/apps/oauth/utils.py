import json
import logging
import urllib
from urllib.parse import urlencode, parse_qs
from urllib.request import urlopen

from django.conf import settings
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer

from oauth.exceptions import OAuthQQAPIError
from . import constants

logger = logging.getLogger("django")


class OAuthQQ(object):
    """
    添加ｑｑ认证辅助工具类
    """

    def __init__(self, client_id=None, client_secret=None, redirect_uri=None, state=None):
        self.client_id = client_id or settings.QQ_CLIENT_ID
        self.client_secret = client_secret or settings.QQ_CLIENT_SECRET
        self.redirect_uri = redirect_uri or settings.QQ_REDIRECT_URI
        self.state = state or settings.QQ_STATE  # 用于保存登录后跳转页面的路径

    def get_qq_login_url(self):
        """
        获取ｑｑ登录的网址
        ｒｅｔｕｒｎ：ｕｒｌ网址
        :return:
        """
        params = {
            'response_type': "code",
            'client_id': self.client_id,
            'redirect_uri': self.redirect_uri,
            'state': self.state,
            'scope': "get_user_info",
        }
        url = 'https://graph.qq.com/oauth2.0/authorize?' + urlencode(params)
        return url

    # 验证开发者身份
    def get_access_token(self, code):
        url = 'https://graph.qq.com/oauth2.0/token?'
        params = {
            "grant_type": "authorization_code",
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "code": code,
            "redirect_uri": self.redirect_uri,
        }
        url += urllib.parse.urlencode(params)
        try:
            #  发送请求
            resp = urlopen(url)
            # 读取相应体数据,字节转成字符串
            resp_data = resp.read().decode()
            # 解析access_token
            resp_dict = urllib.parse.parse_qs(resp_data)
        except Exception as e:
            logger.error("获取access_token异常：%s" % e)
            raise OAuthQQAPIError
        else:
            access_token = resp_dict.get("access_token")
            return access_token[0]

    def get_openid(self, access_token):
        """
        获取用户的openid
        :param access_token: qq提供的access_token
        :return: open_id
        """
        url = 'https://graph.qq.com/oauth2.0/me?access_token=' + access_token
        response = urlopen(url)
        response_data = response.read().decode()
        try:
            # 返回的数据 callback( {"client_id":"YOUR_APPID","openid":"YOUR_OPENID"} )\n;
            data = json.loads(response_data[10:-4])
        except Exception:
            data = parse_qs(response_data)
            logger.error('code=%s msg=%s' % (data.get('code'), data.get('msg')))
            raise OAuthQQAPIError
        openid = data.get('openid', None)
        return openid

    @staticmethod
    def generate_save_user_token(openid):
        """
        生成保存用户数据的token
        :param openid: 用户的openid
        :return: token
        """
        serializer = Serializer(settings.SECRET_KEY, expires_in=constants.SAVE_QQ_USER_TOKEN_EXPIRES)
        data = {'openid': openid}
        token = serializer.dumps(data)
        return token.decode()
