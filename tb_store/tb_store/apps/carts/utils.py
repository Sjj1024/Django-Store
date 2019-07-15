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
    cookie_cart = request.COOKIES.get('cart')
    if not cookie_cart:
        return response

    # 解析cookie购物车数据
    cookie_cart = pickle.loads(base64.b64decode(cookie_cart.encode()))

    # 获取redis中购物车数据
    redis_conn = get_redis_connection('cart')
    redis_cart = redis_conn.hgetall('cart_%s' % user.id)

    # 用于保存最终购物车数据的字典
    cart = {}

    # 将redis中购物车数据的键值对转换为整型
    for sku_id, count in redis_cart.items():
        cart[int(sku_id)] = int(count)

    # 记录redis勾选状态中应该增加的sku_id
    redis_cart_selected_add = []

    # 记录redis勾选状态中应该删除的sku_id
    redis_cart_selected_remove = []

    # 合并cookie购物车与redis购物车，保存到cart字典中
    for sku_id, count_selected_dict in cookie_cart.items():
        # 处理商品数量
        cart[sku_id] = count_selected_dict['count']

        if count_selected_dict['selected']:
            redis_cart_selected_add.append(sku_id)
        else:
            redis_cart_selected_remove.append(sku_id)

    if cart:
        pl = redis_conn.pipeline()
        pl.hmset('cart_%s' % user.id, cart)
        if redis_cart_selected_add:
            pl.sadd('cart_selected_%s' % user.id, *redis_cart_selected_add)
        if redis_cart_selected_remove:
            pl.srem('cart_selected_%s' % user.id, *redis_cart_selected_remove)
        pl.execute()

    response.delete_cookie('cart')

    return response