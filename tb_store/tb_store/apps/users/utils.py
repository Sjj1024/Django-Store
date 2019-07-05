import re

from django.contrib.auth.backends import ModelBackend

from users.models import User


def jwt_response_payload_handler(token, user=None, request=None):
    """
    自定义jwt认证成功返回数据
    """
    return {
        'token': token,
        'user_id': user.id,
        'username': user.username
    }


def get_user_by_account(account):
    """
    根据账号获取user对象
    ：param account 账号，可以是用户名或手机号
    ：return user 对象
    :return:
    """
    try:
        if re.match('^1[3-9]\d{9}$', account):
            # 用户名是手机号
            print(account)
            user = User.objects.get(mobile=account)
        else:
            #　账号是用户名
            print(account)
            user = User.objects.get(username=account)
    except User.DoesNotExist:
        return None
    else:
        return user

class UsernameMobileAuthBackend(ModelBackend):
    """
    自定义用户名或手机号认证
    """
    def authenticate(self, request, username=None, password=None, **kwargs):
        user = get_user_by_account(username)
        print(username, password)
        if user is not None and user.check_password(password):
            return user