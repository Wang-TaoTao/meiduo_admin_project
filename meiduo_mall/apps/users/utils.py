import re

from django.contrib.auth.backends import ModelBackend

from apps.users.models import User


class UsernameMobileModelBackend(ModelBackend):

    def authenticate(self, request, username=None, password=None, **kwargs):

        if request is None:
            #后台登陆
            try:
                user = User.objects.get(username=username,is_staff=True)
            except User.DoesNotExist:
                return None
            #验证密码
            if user.check_password(password):
                return user


        else:
            #前台登陆
            # username 有可能是 用户名也有可能是手机号
            # 1.区分 username
            if re.match(r'1[3-9]\d{9}',username):
                # username 是手机号,根据手机号查询
                user = User.objects.get(mobile=username)
            else:
                user = User.objects.get(username=username)

            #2.验证密码是否正确
            if user and user.check_password(password):
                return user

            return None


from itsdangerous import TimedJSONWebSignatureSerializer as Serializer,BadData
from django.conf import settings

def generate_verify_email_url(user):
    """
    生成邮箱验证链接
    :param user: 当前登录用户
    :return: verify_url
    """
    serializer = Serializer(settings.SECRET_KEY, expires_in=3600)
    data = {'user_id': user.id, 'email': user.email}
    token = serializer.dumps(data).decode()
    verify_url = settings.EMAIL_VERIFY_URL + '?token=' + token
    return verify_url

def check_verify_email_token(token):
    """
    验证token并提取user
    :param token: 用户信息签名后的结果
    :return: user, None
    """
    serializer = Serializer(settings.SECRET_KEY, expires_in=3600)
    try:
        data = serializer.loads(token)
    except BadData:
        return None
    else:
        user_id = data.get('user_id')
        email = data.get('email')
        try:
            user = User.objects.get(id=user_id, email=email)
        except User.DoesNotExist:
            return None
        else:
            return user