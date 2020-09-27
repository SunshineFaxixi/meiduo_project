from itsdangerous import TimedJSONWebSignatureSerializer as Serialier
from django.conf import settings
from itsdangerous import BadData

from . import constants


def generate_access_token(openid):
    """
    签名、序列化openid
    :param openid: openid明文
    :return: token(openid密文)
    """
    # 创建序列化对象
    # s = Serialier('秘钥：越复杂越安全', '过期时间')
    s = Serialier(settings.SECRET_KEY, constants.ACCESS_TOKEN_EXPIRES)

    # 准备待序列化的字典参数
    data = {'openid': openid}

    # 调用dumps方法进行序列化：类型是bytes
    token = s.dumps(data)

    # 返回序列化后的数据
    return token.decode()


def check_access_token(access_token_openid):
    """
    反解、反序列化access_token_openid
    :param access_token_openid: openid密文
    :return:openid明文
    """
    # 创建序列化器对象：序列化和反序列化的参数必须一模一样
    s = Serialier(settings.SECRET_KEY, constants.ACCESS_TOKEN_EXPIRES)

    # 反序列化openid密文
    try:
        data = s.loads(access_token_openid)
    except BadData: # openid密文过期
        return None
    else:
        # 返回openid明文
        return data.get('openid')