import base64
import pickle

from django.shortcuts import render
from .serializers import CartSKUSerializer

# Create your views here.
from django_redis import get_redis_connection
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from carts import constants
from goods.models import SKU
from .serializers import CartSerializer


class CartView(APIView):
    """
    购物车
    """

    def perform_authentication(self, request):
        """
        重写父类的用户验证方法，不在进入试图前就检查JWT
        :param request:
        :return:
        """
        pass

    def get(self, request):
        """
        获取购物车
        :return:
        """
        try:
            user = request.user
        except Exception:
            user = None

        if user is not None and user.is_authenticated:
            # 用户已登录，从redis中读取
            redis_conn = get_redis_connection('cart')
            redis_cart = redis_conn.hgetall('cart_%s' % user.id)
            redis_cart_selected = redis_conn.smembers('cart_selected_%s' % user.id)
            cart = {}
            for sku_id, count in redis_cart.items():
                cart[int(sku_id)] = {
                    'count': int(count),
                    'selected': sku_id in redis_cart_selected
                }
        else:
            # 用户未登录，从cookie中读取
            cart = request.COOKIES.get('cart')
            if cart is not None:
                cart = pickle.loads(base64.b64decode(cart.encode()))
            else:
                cart = {}

                # 遍历处理购物车数据
        skus = SKU.objects.filter(id__in=cart.keys())
        for sku in skus:
            sku.count = cart[sku.id]['count']
            sku.selected = cart[sku.id]['selected']

        serializer = CartSKUSerializer(skus, many=True)
        return Response(serializer.data)


    def post(self, request):
        """
        添加购物车
        :param request:
        :return:
        """
        serializer = CartSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        sku_id = serializer.validated_data.get("sku_id")
        count = serializer.validated_data.get("count")
        selected = serializer.validated_data.get("selected")

        # 尝试对请求的用户进行验证
        try:
            user = request.user
        except Exception:
            # 验证失败，用户未登录
            user = None

        if user is not None and user.is_authenticated:
            # 用户已登录，在redis中保存
            redis_conn = get_redis_connection("cart")
            p1 = redis_conn.pipeline()
            p1.hincrby("cart_%s" % user.id, sku_id, count)
            if selected:
                p1.sadd("cart_selected_%s" % user.id, sku_id)
            p1.execute()

            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            cart = request.COOKIES.get("cart")
            if cart is not None:
                cart = pickle.loads(base64.b64decode(cart.encode()))
            else:
                cart = {}

            sku = cart.get(sku_id)
            if sku:
                count += int(sku.get("count"))

            cart[sku_id] = {
                "count": count,
                "selected": selected
            }

            cookie_cart = base64.b64encode(pickle.dumps(cart)).decode()
            response = Response(serializer.data, status=status.HTTP_201_CREATED)

            # 设置购物车的cookie，需要设置有效期，否则是临时cookie
            response.set_cookie("cart", cookie_cart, max_age=constants.CART_COOKIE_EXPIRES)
            return response
