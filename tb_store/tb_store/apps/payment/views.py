import os
from alipay import AliPay
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from orders.models import OrderInfo
from payment.models import Payment
from tb_store.settings import dev


class PaymentView(APIView):
    """
    支付
    """
    permission_classes = (IsAuthenticated,)

    def get(self, request, order_id):
        """
        获取支付链接
        """
        # 判断订单信息是否正确
        try:
            order = OrderInfo.objects.get(order_id=order_id, user=request.user,
                                          pay_method=OrderInfo.PAY_METHODS_ENUM["ALIPAY"],
                                          status=OrderInfo.ORDER_STATUS_ENUM["UNPAID"])
        except OrderInfo.DoesNotExist:
            return Response({'message': '订单信息有误'}, status=status.HTTP_400_BAD_REQUEST)

        # 构造支付宝支付链接地址
        alipay = AliPay(
            appid=dev.ALIPAY_APPID,
            app_notify_url=None,  # 默认回调url
            app_private_key_path=os.path.join(os.path.dirname(os.path.abspath(__file__)), "keys/app_private_key.pem"),
            alipay_public_key_path=os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                                "keys/alipay_public_key.pem"),  # 支付宝的公钥，验证支付宝回传消息使用，不是你自己的公钥,
            sign_type="RSA2",  # RSA 或者 RSA2
            debug=dev.ALIPAY_DEBUG  # 默认False
        )

        order_string = alipay.api_alipay_trade_page_pay(
            out_trade_no=order_id,
            total_amount=str(order.total_amount),
            subject="东京商城%s" % order_id,
            return_url="http://www.meiduo.site:8080/pay_success.html",
        )
        # 需要跳转到https://openapi.alipay.com/gateway.do? + order_string
        # 拼接链接返回前端
        alipay_url = dev.ALIPAY_URL + "?" + order_string
        return Response({'alipay_url': alipay_url})


# 支付宝回调函数接口 put /payment/status/?支付宝参数
class PaymentStatusView(APIView):
    def put(self, request):
        # 接收参数，效验参数
        # 构造支付宝支付链接地址
        alipay_req_data = request.query_params
        if not alipay_req_data:
            return Response({"message": "缺啥参数"}, status=status.HTTP_400_BAD_REQUEST)
        alipay_req_dict = alipay_req_data.dict()
        sign = alipay_req_dict.pop("sign")

        alipay = AliPay(
            appid=dev.ALIPAY_APPID,
            app_notify_url=None,  # 默认回调url
            app_private_key_path=os.path.join(os.path.dirname(os.path.abspath(__file__)), "keys/app_private_key.pem"),
            alipay_public_key_path=os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                                "keys/alipay_public_key.pem"),  # 支付宝的公钥，验证支付宝回传消息使用，不是你自己的公钥,
            sign_type="RSA2",  # RSA 或者 RSA2
            debug=dev.ALIPAY_DEBUG  # 默认False
        )

        result = alipay.verify(alipay_req_dict, sign)
        # 保存数据，保存支付结果数据
        if result:
            order_id = alipay_req_dict.get("out_trade_no")
            trade_id = alipay_req_dict.get("trade_no")
            # 修改订单状态
            Payment.objects.create(
                order_id=order_id,
                trade_id=trade_id
            )
            OrderInfo.objects.filter(order_id=order_id).update(status=OrderInfo.ORDER_STATUS_ENUM["UNCOMMENT"])
            return Response({"trade_id": trade_id})
        else:
            return Response({"message": "参数有误"}, status=status.HTTP_400_BAD_REQUEST)