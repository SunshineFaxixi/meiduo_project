from django.shortcuts import render, redirect
from django.views import View
from django import http
import re
from django.db import DatabaseError
from django.urls import reverse
from django.contrib.auth import login, authenticate, logout
from django_redis import get_redis_connection
from django.contrib.auth.mixins import LoginRequiredMixin

from meiduo_mall.utils.response_code import RETCODE
from users.models import User
# Create your views here.


class UserInfoView(LoginRequiredMixin, View):
    """用户中心"""
    def get(self, request):
        # if request.user.is_authenticated:
        #     return render(request, 'user_center_info.html')
        # else:
        #     return redirect(reverse('users:login'))
        return render(request, 'user_center_info.html')


class RegisterView(View):
    def get(self, request):
        return render(request, 'register.html')

    def post(self, request):
        """实现用户注册业务逻辑"""
        # 接收参数：表单参数
        username = request.POST.get('username')
        password = request.POST.get('password')
        password2 = request.POST.get('password2')
        sms_code_client = request.POST.get('sms_code')
        mobile = request.POST.get('mobile')
        allow = request.POST.get('allow')
        # 校验参数: 前后端的校验需要分开，避免恶意用户越过前端逻辑发请求，要保证后端的安全，前后端的校验逻辑相同
        # 1. 判断参数是否齐全： all([列表]),会校验列表中的元素是否为空，只要有一个为空，返回false
        if not all([username, password, password2, mobile, allow]):
            return http.HttpResponseForbidden('缺少必传参数')
        # 2. 判断用户名是否是5-20个字符
        if not re.match(r'^[a-zA-Z0-9_-]{5,20}$', username):
            return http.HttpResponseForbidden('请输入5-10个字符的用户名')
        # 3. 判断密码是否是8-20个字符
        if not re.match(r'^[a-zA-Z0-9_-]{8,20}$', password):
            return http.HttpResponseForbidden('请输入8-20位的密码')
        # 4. 判断两次密码是否一致
        if password != password2:
            return http.HttpResponseForbidden('两次输入的密码不一致')
        # 5. 判断手机号是否一致
        if not re.match(r'^1[3-9]\d{9}$', mobile):
            return http.HttpResponseForbidden('请输入正确的手机号码')
        # 判断短信验证码是否输入正确
        redis_conn = get_redis_connection('verify_code')
        sms_code_server = redis_conn.get('sms_%s' % mobile)
        if sms_code_server is None:
            return render(request, 'register.html', {'sms_code_errmsg': '短信验证码已失效'})
        if sms_code_client != sms_code_server.decode():
            return render(request, 'register.html', {'sms_code_errmsg': '输入短信验证码有误'})
        # 6. 判断是否勾选用户协议
        if allow != 'on':
            return http.HttpResponseForbidden('请勾选用户协议')
        # 保存注册数据：注册业务的核心
        # return render(request, 'register.html', {'register_errmsg': '注册失败'}) # 测试错误信息渲染是否正确
        try:
            user = User.objects.create_user(username=username, password=password, mobile=mobile)
        except DatabaseError:
            return render(request, 'register.html', {'register_errmsg': '注册失败'})
        # 状态保持
        login(request, user)
        response = redirect(reverse('contents:index'))

        # 需要将用户名缓存到cookie中，实现首页右上角展示用户名信息
        response.set_cookie('username', user.username, max_age=3600 * 24 * 15)

        # 响应结果
        return response


class LoginView(View):
    """用户登录"""
    def get(self, request):
        return render(request, 'login.html')
    def post(self, request):
        # 接收参数
        username = request.POST.get('username')
        password = request.POST.get('password')
        remembered = request.POST.get('remembered')

        # 校验参数
        if not all([username, password]):
            return http.HttpResponseForbidden('缺少必传参数')
        if not re.match(r'^[a-zA-Z0-9_-]{5,20}$', username):
            return http.HttpResponseForbidden('请输入正确的用户名或手机号')
        if not re.match(r'^[a-zA-Z0-9]{8,20}$', password):
            return http.HttpResponseForbidden('密码最少8位，最长20位')

        # 认证用户: 使用账户查询用户是否存在，如果用户存在，再校验密码是否正确
        user = authenticate(username=username, password=password)
        if user is None:
            return render(request, 'login.html', {'account_errmsg': '账号或密码错误'})

        # 状态保持
        login(request, user)
        # 使用remembered确定状态保持周期（实现记住登录）
        if remembered != 'on':
            # 没有记住密码：状态保持在浏览器会话结束后就销毁
            request.session.set_expiry(0) # 单位是秒
        else:
            # 记住登录：状态保持周期为2周：默认是2周
            request.session.set_expiry(None)

        response = redirect(reverse('contents:index'))

        # 先取出next
        next = request.GET.get('next')
        if next:
            # 重定向到next
            response = redirect(next)
        else:
            # 重定向到首页
            redirect(reverse('contents:index'))

        # 需要将用户名缓存到cookie中，实现首页右上角展示用户名信息
        response.set_cookie('username', user.username, max_age=3600 * 24 * 15)

        # 响应结果
        return response


class LogoutView(View):
    def get(self, request):
        # 清理session
        logout(request)
        # 退出登录，重定向到登录页
        response = redirect(reverse('contents:index'))
        # 退出登录时清除cookie中的username
        response.delete_cookie('username')
        return response


class UsernameCountView(View):
    """判断用户名是否重复注册"""

    def get(self, request, username):
        """
        :param request:
        :param username: 用户名
        :return: JSON
        """
        # 实现主体业务逻辑
        count = User.objects.filter(username=username).count()
        # 响应结果
        return http.JsonResponse({'code': RETCODE.OK, 'errmsg': 'OK', 'count': count})
