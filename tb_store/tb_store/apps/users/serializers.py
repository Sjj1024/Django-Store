import re

from django_redis import get_redis_connection
from rest_framework import serializers

from celery_tasks.email.tasks import send_verify_email
from goods.models import SKU
from users import constants
from users.models import User, Address


class UserAddressSerializer(serializers.ModelSerializer):
    """
    用户地址序列化器
    """
    province = serializers.StringRelatedField(read_only=True)
    city = serializers.StringRelatedField(read_only=True)
    district = serializers.StringRelatedField(read_only=True)
    province_id = serializers.IntegerField(label='省ID', required=True)
    city_id = serializers.IntegerField(label='市ID', required=True)
    district_id = serializers.IntegerField(label='区ID', required=True)

    class Meta:
        model = Address
        exclude = ('user', 'is_deleted', 'create_time', 'update_time')

    def validate_mobile(self, value):
        """
        验证手机号
        """
        if not re.match(r'^1[3-9]\d{9}$', value):
            raise serializers.ValidationError('手机号格式错误')
        return value

    def create(self, validated_data):
        """
        保存
        """
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)


class AddressTitleSerializer(serializers.ModelSerializer):
    """
    地址标题
    """

    class Meta:
        model = Address
        fields = ('title',)


class CreateUserSerializer(serializers.ModelSerializer):
    """
    创建用户序列化器
    """
    # 额外增加的字段选项
    password2 = serializers.CharField(label='确认密码', write_only=True)
    sms_code = serializers.CharField(label='短信验证码', write_only=True)
    allow = serializers.CharField(label='同意协议', write_only=True)
    token = serializers.CharField(label="JWT token", read_only=True)

    class Meta:
        model = User
        fields = ('id', 'username', 'password', 'password2', 'sms_code', 'mobile', 'allow', "token")
        extra_kwargs = {
            'username': {
                'min_length': 5,
                'max_length': 20,
                'error_messages': {
                    'min_length': '仅允许5-20个字符的用户名',
                    'max_length': '仅允许5-20个字符的用户名',
                }
            },
            'password': {
                'write_only': True,
                'min_length': 8,
                'max_length': 20,
                'error_messages': {
                    'min_length': '仅允许8-20个字符的密码',
                    'max_length': '仅允许8-20个字符的密码',
                }
            }
        }

    def validate_mobile(self, value):
        """验证手机号"""
        if not re.match(r'^1[3-9]\d{9}$', value):
            raise serializers.ValidationError('手机号格式错误')
        return value

    def validate_allow(self, value):
        """检验用户是否同意协议"""
        if value != 'true':
            raise serializers.ValidationError('请同意用户协议')
        return value

    def validate(self, data):
        # 判断两次密码
        if data['password'] != data['password2']:
            raise serializers.ValidationError('两次密码不一致')

        # 判断短信验证码
        redis_conn = get_redis_connection('verify_codes')
        mobile = data['mobile']
        real_sms_code = redis_conn.get('sms_%s' % mobile)
        if real_sms_code is None:
            raise serializers.ValidationError('无效的短信验证码')
        if data['sms_code'] != real_sms_code.decode():
            raise serializers.ValidationError('短信验证码错误')

        return data

    def create(self, validated_data):
        """
        创建用户
        """
        # 移除数据库模型类中不存在的属性
        del validated_data['password2']
        del validated_data['sms_code']
        del validated_data['allow']

        # user= User.objects.create(**validated_data)
        user = super().create(validated_data)

        # 调用django的认证系统加密密码
        user.set_password(validated_data['password'])
        user.save()
        # print("新用户注册成功")
        from rest_framework_jwt.settings import api_settings

        jwt_payload_handler = api_settings.JWT_PAYLOAD_HANDLER
        jwt_encode_handler = api_settings.JWT_ENCODE_HANDLER

        payload = jwt_payload_handler(user)
        token = jwt_encode_handler(payload)

        # 给user添加token字段
        user.token = token

        return user


class UserDetailSerializer(serializers.ModelSerializer):
    """
    用户详情序列化器
    """

    class Meta:
        model = User
        fields = ("id", "username", "mobile", "email", "email_active")


class EmailSerializer(serializers.ModelSerializer):
    """
    用户邮箱序列化器
    """

    class Meta:
        model = User
        fields = ("id", "email")
        extra_kwargs = {
            "email": {
                "required": True
            }
        }

    def update(self, instance, validated_data):
        email = validated_data["email"]
        instance.email = email
        instance.save()

        # 　生成验证了链接
        verify_url = instance.generate_verify_email_url()

        # 发送验证邮件
        send_verify_email.delay(email, verify_url)

        return instance


class AddUserBrowsingHistorySerializer(serializers.Serializer):
    """
    添加用户浏览历史序列化器
    """
    sku_id = serializers.IntegerField(label="商品SKU编号", min_value=1)

    def validate_sku_id(self, value):
        """
        检验sku_id是否存在
        """
        try:
            SKU.objects.get(id=value)
        except SKU.DoesNotExist:
            raise serializers.ValidationError('该商品不存在')
        return value

    def create(self, validated_data):
        """
        保存
        """
        user_id = self.context['request'].user.id
        sku_id = validated_data['sku_id']

        redis_conn = get_redis_connection("history")
        pl = redis_conn.pipeline()

        # 移除已经存在的本商品浏览记录
        pl.lrem("history_%s" % user_id, 0, sku_id)
        # 添加新的浏览记录
        pl.lpush("history_%s" % user_id, sku_id)
        # 只保存最多5条记录
        pl.ltrim("history_%s" % user_id, 0, constants.USER_BROWSING_HISTORY_COUNTS_LIMIT - 1)

        pl.execute()

        return validated_data


class PasswordSerializer(serializers.ModelSerializer):
    """
    用户密码修改序列化器类
    """
    # 额外增加的字段选项
    ipassword = serializers.CharField(label='原始密码', write_only=True)
    password2 = serializers.CharField(label='确认密码', write_only=True)

    class Meta:
        model = User
        fields = ("id", "ipassword", "password", "password2")
        extra_kwargs = {
            'ipassword': {
                'write_only': True,
                'min_length': 8,
                'max_length': 20,
                'error_messages': {
                    'min_length': '仅允许8-20个字符的密码',
                    'max_length': '仅允许8-20个字符的密码',
                }
            },
            'password2': {
                'write_only': True,
                'min_length': 8,
                'max_length': 20,
                'error_messages': {
                    'min_length': '仅允许8-20个字符的密码',
                    'max_length': '仅允许8-20个字符的密码',
                }
            },
        }

    # 判断新的两个密码是否正确
    def validate(self, data):
        # 判断两次密码
        if data['password'] != data['password2']:
            raise serializers.ValidationError('两次密码不一致')
        return data

    def update(self, instance, validated_data):
        """
        更新用户密码
        """
        # 移除数据库模型类中不存在的属性
        del validated_data['password2']
        ipassword = validated_data['ipassword']
        del validated_data['ipassword']

        user = super().create(validated_data)

        user.check_password(ipassword)

        user.set_password(validated_data['password'])
        user.save()

        return instance
