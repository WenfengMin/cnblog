"""cnblog URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path,re_path
from blog import views
from django.views.static import serve
from cnblog import settings


urlpatterns = [
    path('admin/', admin.site.urls),
    path('login/', views.login),
    path('get_validCode_img/', views.get_validCode_img),
    path('index/', views.index),
    path('logout/', views.logout),
    re_path('^$', views.index),      # 用户无输入，默认跳转到index页面
    path('register/', views.register),

    path('upload/', views.upload),

    # 点赞
    path('digg/', views.digg),

    # 评论
    path('comment/', views.comment),

    # 评论树
    path('get_comment_tree/', views.get_comment_tree),

    # media配制（记住）  用于用户访问media静态文件夹下的文件，static文件夹用户也可以访问，但是不用我们配制，因为django已经为我们配制好了，但是此次的media需要我们手动配置
    # 该正则表达式表示：只要以media开头的路径即可
    re_path(r'media/(?P<path>.*)$',serve,{'document_root':settings.MEDIA_ROOT}),


    # 个人站点的访问（如soft） 如http://127.0.0.1:8000/soft
    re_path('^(?P<username>\w+)/$', views.home_site),     # home_site(request,username='soft')

    # 个人页面下的跳转
    re_path('^(?P<username>\w+)/(?P<condition>tag|category|archive)/(?P<param>.*)/$', views.home_site),
    # home_site接收的参数：home_site(request,username='soft',condition='tag',param='Python...')

    # 个人站点下的文章详情页
    re_path('^(?P<username>\w+)/articles/(?P<article_id>\d+)$', views.article_detail),


    # 后台管理
    re_path('cn_backend/$',views.cn_backend),
    re_path('cn_backend/add_articles/$',views.add_articles),

]


# \w+：包含数字和字母，但不包含特殊符号
# .*包含特殊符号
# ?P<username>：有名分组，该username是用户访问时输入的如soft等名字，其会作为参数传递给home_site视图函数


# (?P<name>)：分别起别名
# (?P=name)：引用别名为name分组匹配到的字符串

# (?P<key1>)：给匹配规则起的别名，不代表内容，后面的.+才是代表匹配规则的内容部分
# (?P=key1)：使用别名为key1匹配好的分组字符串


