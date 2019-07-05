import logging
from urllib.parse import urlencode

from django.conf import settings

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
