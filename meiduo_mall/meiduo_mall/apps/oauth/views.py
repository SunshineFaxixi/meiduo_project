from django.shortcuts import render, redirect
from QQLoginTool.QQtool import OAuthQQ
from django import http
from django.conf import settings
from django.views import View
import logging, re
from django.contrib.auth import login
from django.urls import reverse
from django_redis import get_redis_connection

from meiduo_mall.utils.response_code import RETCODE
from .models import OAuthQQUser
from .utils import generate_access_token, check_access_token
# Create your views here.


# 创建日志输出器
logger = logging.getLogger('django')


class QQAuthUserView(View):
    """处理QQ登录回调： oauth_callback"""
    def get(self, request):
        """处理QQ登录回调的业务逻辑"""
        # 获取code
        code = request.GET.get('code')
        if not code:
            return http.HttpResponseForbidden('获取code失败')

        # 创建工具对象
        oauth = OAuthQQ(client_id=settings.QQ_CLIENT_ID, client_secret=settings.QQ_CLIENT_SECRET,
                            redirect_uri=settings.QQ_REDIRECT_URI)
        try:
            # 使用code获取access_token
            access_token = oauth.get_access_token(code)

            # 使用access_token获取openid
            openid = oauth.get_open_id(access_token)
        except Exception as e:
            logger.error(e)
            return http.HttpResponseServerError('OAuth2.0认证失败')

        # 使用openid判断该QQ用户是否绑定过美多商城的用户
        try:
            oauth_user = OAuthQQUser.objects.get(openid=openid)
        except OAuthQQUser.DoesNotExist:
            # openid没绑定美多商城用户
            access_token_openid = generate_access_token(openid)
            context = {'access_token_openid': access_token_openid}
            return render(request, 'oauth_callback.html', context)
        else:
            # openid已绑定美多商城用户
            # 实现状态保持
            login(request, oauth_user.user)

            # 重定向到首页
            response = redirect(reverse('contents:index'))

            # 将用户名写到cookie
            response.set_cookie('username', oauth_user.user.username, max_age=3600 * 24 * 15)

            # 响应结果
            return response

    def post(self, request):
        """实现绑定用户的逻辑"""
        # 接收参数
        mobile = request.POST.get('mobile')
        password = request.POST.get('password')
        sms_code_client = request.POST.get('sms_code')
        access_token_openid = request.POST.get('access_token_openid')
        # 校验参数
        # 判断参数是否齐全
        if not all([mobile, password, sms_code_client, access_token_openid]):
            return http.HttpResponseForbidden('缺少必传参数')
        # 判断手机号是否合法
        if not re.match():
            return http.HttpResponseForbidden('请输入正确的手机号码')
        # 判断密码是否合格
        if not re.match():
            return http.HttpResponseForbidden('请输入8-20位的密码')
        # 判断短信验证码是否一致
        redis_conn = get_redis_connection('verify_code')
        sms_code_server = redis_conn.get('sms_%s' % mobile)
        if sms_code_server is None:
            return render(request, 'oauth_callback.html', {'sms_code_errmsg': '无效的短信验证码'})
        if sms_code_client != sms_code_server.decode():
            return render(request, 'oauth_callback.html', {'sms_code_errmsg': '输入短信验证码有误'})
        # 判断openid是否有效：openid使用itsdangerous签名之后只有600秒的有效期
        openid = check_access_token(access_token_openid)
        if not openid:
            return render(request, 'oauth_callback.html', {'openid_errmsg': 'openid已失效'})


class QQAuthURLView(View):
    """提供QQ登录扫码页面"""
    def get(self, request):
        # 接收next
        next = request.GET.get('next')

        # 创建工具对象
        oauth = OAuthQQ(client_id=settings.QQ_CLIENT_ID, client_secret=settings.QQ_CLIENT_SECRET, redirect_uri=settings.QQ_REDIRECT_URI, state=next)

        # 生成QQ登录扫码链接地址
        login_url = oauth.get_qq_url()

        # 响应
        return http.JsonResponse({'code': RETCODE.OK, 'errmsg': 'OK', 'login_url': login_url})
