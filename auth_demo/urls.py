"""bbs URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.11/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url, include
from django.contrib import admin
from django.urls import path
from app01 import views
from django.views.static import serve
from django.conf import settings
from django.conf.urls.static import static


urlpatterns = [
    path('admin/', admin.site.urls),
    path('login/', views.login, name='login'),
    path('logout/', views.logout, name='logout'),
    path('reg/', views.register,name='register'),
    path('index/', views.index, name='index'),
    path('', views.list, name='list'),
    path('library/',views.library, name='library'),
    path('library_out/',views.lib_out,name='library_out'),
    path('article_detail/<int:id>/', views.article_detail, name='article_detail'),
    # 写文章
    path('article_create/', views.article_create, name='article_create'),
    # 删除文章
    path('article_delete/<int:id>/', views.article_delete, name='article_delete'),
    # 更新文章
    path('article_update/<int:id>/', views.article_update, name='article_update'),
    path('password_reset/', include('password_reset.urls')),
    path('edit/<int:id>/',views.profile_edit, name='edit'),
    path('comment/', include('comment.urls', namespace='comment')),
    path('pwchange/',views.pwchange.as_view(), name='pwchange'),
    # 极验滑动验证码 获取验证码的url
    path('pc-geetest/register', views.get_geetest, name='geetest'),
    path('send_msg/', views.send_msg, name='send_msg'),
    # media相关的路由设置
    # path('media/(?P<path>.*)$', serve, {"document_root": settings.MEDIA_ROOT}),
]

#添加这行
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
