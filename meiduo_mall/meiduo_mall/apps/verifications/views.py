import random, logging
from django.shortcuts import render
from django.views import View
from django_redis import get_redis_connection
from django import http

from verifications.libs.captcha.captcha import captcha
from . import constants
from meiduo_mall.utils.response_code import RETCODE
from verifications.libs.yuntongxun.ccp_sms import CCP

# Create your views here.

# 创建日志记录器
logger = logging.getLogger('django')

class SMSCodeView(View):
    def get(self, request, mobile):
        # 接收参数
        image_code_client = request.GET.get('image_code')
        uuid = request.GET.get('uuid')

        # 创建连接到redis的对象
        redis_conn = get_redis_connection('verify_code')

        # 校验参数
        if not all([image_code_client, uuid]):
            return http.HttpResponseForbidden('缺少必传参数')

        # 避免频繁发送短信验证码
        send_flag = redis_conn.get('send_flag_%s' % mobile)
        if send_flag:
            return http.JsonResponse({'code': RETCODE.THROTTLINGERR, 'errmsg': '发送短信过于频繁'})

        # 提取图形验证码

        image_code_server = redis_conn.get('img_%s' % uuid)

        if not image_code_server:
            return http.JsonResponse({'code': RETCODE.IMAGECODEERR, 'errmsg': '图形验证码已失效'})

        # 删除图形验证码
        redis_conn.delete('img_%s' % uuid)

        # 对比图形验证码
        image_code_server = image_code_server.decode()
        if image_code_server.lower() != image_code_client.lower():
            return http.JsonResponse({'code': RETCODE.IMAGECODEERR, 'errmsg': '输入图形验证码有误'})

        # 生成短信验证码
        sms_code = '%06d' % random.randint(0, 999999)
        logger.info(sms_code)

        # 保存短信验证码
        redis_conn.setex('sms_%s' % mobile, constants.IMAGE_CODE_REDIS_EXPIRES, sms_code)

        # 保存发送短信验证码的标记
        redis_conn.setex('send_flag_%s' % mobile, constants.SEND_SMS_CODE_INTERVAL, 1)

        # 发送短信验证码
        CCP().send_template_sms('17301768520', [sms_code, constants.IMAGE_CODE_REDIS_EXPIRES / 60], 1)

        # 响应结果
        return http.JsonResponse({'code': RETCODE.OK, 'errmsg': '发送短信成功'})


class ImageCodeView(View):
    def get(self, request, uuid):
        """
        :parms uuid: 通用唯一识别码，用于唯一标识该图形验证码属于哪个用户的
        :return: image/jpg
        """
        # 接收和校验参数（uuid）
        # 主体业务逻辑
        # 1. 生成图形验证码（captcha）
        text, image = captcha.generate_captcha()

        # 2. 保存图形验证码(redis)
        redis_conn = get_redis_connection('verify_code')
        redis_conn.setex("img_%s" % uuid, constants.IMAGE_CODE_REDIS_EXPIRES, text)

        # 响应结果（图形验证码）
        return http.HttpResponse(image, content_type='image/jpg')