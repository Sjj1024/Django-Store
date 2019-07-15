import  pickle
import base64
from django_redis import get_redis_connection


def merge_cart_cookie_to_redis(request, user, response):
    """
    合并请求用户的购物车数据，将未登录保存的cookie数据保存到redis中
    :param request:
    :param user:
    :param response:
    :return:
    :return:
    """