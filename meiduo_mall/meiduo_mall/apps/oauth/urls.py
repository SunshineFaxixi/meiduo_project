from django.conf.urls import url, include

from . import views

urlpatterns = [
    url(r'^qq/login/$', views.QQAuthURLView.as_view()),
    url(r'^oauth_callback/$', views.QQAuthUserView.as_view()),
]