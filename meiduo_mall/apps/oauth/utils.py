from itsdangerous import BadData
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from django.conf import settings


def generate_eccess_token(openid):
    """
    签名openid
    :param openid: 用户的openid
    :return: access_token
    """
    serializer = Serializer(settings.SECRET_KEY, expires_in=3600)
    data = {'openid': openid}
    token = serializer.dumps(data)
    return token.decode()

def check_access_token(access_token):
    """
    提取openid
    :param access_token: 签名后的openid
    :return: openid or None
    """
    serializer = Serializer(settings.SECRET_KEY, expires_in=3600)
    try:
        data = serializer.loads(access_token)
    except BadData:
        return None
    else:
        return data.get('openid')