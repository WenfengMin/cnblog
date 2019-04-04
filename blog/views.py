import os
import json
from threading import Thread
from bs4 import BeautifulSoup
from django.shortcuts import render,redirect,HttpResponse
from django.http import JsonResponse
from django.contrib import auth
from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail
from django.db import transaction
from django.db.models import F
from django.db.models import Avg,Max,Min,Count
from django.db.models.functions import TruncMonth
from django.views.decorators.csrf import csrf_exempt
from cnblog import settings
from blog.utils.validCode import get_valid_code_img
from blog.Myforms import UserForm
from blog.models import *


@csrf_exempt
def login(request):
    if request.method == 'POST':
        response = {
            'user':None,
            'msg':None
        }
        user_name = request.POST.get('user')
        pwd = request.POST.get('pwd')
        valid_code = request.POST.get('valid_code')

        valid_code_str=request.session.get('valid_code_str')

        # 先校验验证码
        if valid_code.upper() == valid_code_str.upper():
            user = auth.authenticate(username=user_name,password=pwd)
            if user:
                # 注册session，未执行这一步时，request.user==匿名用户对象
                auth.login(request,user)        # request.user==当前登录对象
                # response['user'] = request.user  # ??
                response['user'] = user.username
            else:
                response['msg'] = '用户名或密码错误'
        else:
            response['msg']='验证码错误'

        # JsonResponse()会直接将{}序列化成json字符串，ajax拿到之后，也不用反序列化
        return JsonResponse(response)

    return render(request,'login.html')


# 构建验证码图片，基于PIL模块创建出来的
def get_validCode_img(request):
    '''
    基于PIL模块，动态生成响应状态码
    '''
    data = get_valid_code_img(request)
    return HttpResponse(data)


def index(request):
    article_list = Article.objects.all()
    print(article_list)

    return render(request,'index.html', {'article_list':article_list})


def register(request):
    # if request.method == 'POST':
    if request.is_ajax():
        print(request.POST)

        response = {
            'user': None,
            'msg': None
        }

        form = UserForm(request.POST)     # 校验字段
        if form.is_valid():
            print(form.cleaned_data)
            response['user'] = form.cleaned_data.get('user')

            # 生成一条用户记录（即，将注册的用户添加到数据库）
            # form组件只帮忙校验了以下4个字段
            user = form.cleaned_data.get('user')
            print('user:', user)
            pwd = form.cleaned_data.get('pwd')
            email = form.cleaned_data.get('email')
            tel = form.cleaned_data.get('tel')

            # 未配制media路径时：django会默认将文件对象下载到“项目根目录”下的avatars文件夹中（若没有该文件夹，django会自动创建）
            # 若配置了MEDIA_ROOT，则会将将文件对象下载到“MEDIA_ROOT”的avatars文件夹中（若没有该文件夹，django会自动创建）
            # user_obj的avatar保存的是文件的相对路径？
            avatar_obj = request.FILES.get('avatar')

            # if avatar_obj:   # 用户上传了文件，此处就将其传给服务器
            #     user_obj = UserInfo.objects.create_user(username=user,password=pwd,email=email,avatar=avatar_obj,telephone=tel)
            # else:     # 用户未选择文件，此时若还给给服务器传递avatar，那么传递的将会是一个空值，会报错；所以，此处，不给服务器传递avatar字段，那么服务器将会使用默认的值'/avatars/default.png'
            #           # 注意区分：传空值  和  不传值 的区别：传空值：服务器get不到，会报错；不传该字段，服务器则会使用默认值
            #     user_obj = UserInfo.objects.create_user(username=user,password=pwd,email=email,telephone=tel)
            # 因为逻辑上用不到user_obj，所以可以不用赋值，直接执行=右边的代码即可

            # 对上面if...else的优化：
            extra_fields = {}
            UserInfo.objects.create_user(username=user, password=pwd, email=email, telephone=tel, **extra_fields)
            if avatar_obj:
                extra_fields['avatar'] = avatar_obj

        else:
            # print(form.cleaned_data)
            # print(form.errors)
            response['msg'] = form.errors
            # 该errors里面包含一个全局错误，而全局错误的键为__all__

        return JsonResponse(response)

    form = UserForm()     # 渲染页面
    return render(request,'register.html',locals())


def logout(request):
    auth.logout(request)   # request.session.flush()
    return redirect('/login/')


def home_site(request,username,**kwargs):
    '''
    个人站点
    :param request:
    :return:
    '''
    print('username:', username)
    print('kwargs:',kwargs)

    user_obj = UserInfo.objects.filter(username=username).first()
    print('user_obj:',user_obj)

    # 判断用户是否存在
    if not user_obj:
        return render(request,'not_found.html')

    # 查询当前站点对象
    blog_obj = user_obj.blog

    # 获取当前用户（站点）对应的所有文章
    # 1 基于对象查询
    # article_list = user_obj.article_set.all()
    # print(article_list)
    # 2 基于双下划线__查询
    # Article.objects.filter(user_id=user_obj.pk)
    article_list = Article.objects.filter(user=user_obj)

    if kwargs:              # 区分访问的是站点页面，还是站点下的跳转页面
        condition = kwargs.get('condition')
        param = kwargs.get('param')
        print(condition)
        print(param)

        if condition == 'tag':
            article_list = Article.objects.filter(user=user_obj,tags__title=param)
            print('article_list:',article_list)

        elif condition == 'category':
            article_list = Article.objects.filter(user=user_obj).filter(category__title=param)
            print('article_list:',article_list)
        elif condition == 'archive':
            year,month = param.split('-')
            article_list = Article.objects.filter(user=user_obj,create_time__year=year,create_time__month=month)


    # 练习：查询每一个分类名称及对应的文章数
    # ret1 = Category.objects.values('pk').annotate(count=Count('article__title')).values('title','count')
    # print(ret1)

    # 难点！！！

    # 1 查询当前站点的每一个分类名称及对应的文章数
    # cate_list = Category.objects.values('pk').filter(blog=blog_obj).annotate(count=Count('article__title')).values('title', 'count')
    # cate_list = Category.objects.values('pk').filter(blog=blog_obj).annotate(count=Count('article__title')).values_list('title', 'count')
    # print('category_list:',cate_list)
    # values('title', 'count')得到的是字典，前端可通过cate.title/cate.count获取
    # values_list('title', 'count')得到的是元组，可通过cate.0/cate.1获取


    # 2 查询当前站点的每一个标签名称及对应的文章数
    # tag_list = Tag.objects.values('pk').filter(blog=blog_obj).annotate(count=Count('article__title')).values_list('title', 'count')
    # print('tag_list:',tag_list)


    # 3 查询当前站点每一个年月的名称以及对应的文章数

    # 补充：django中，关于extra()函数的用法
    # date = Article.objects.extra(select={'is_recent': "create_time > '2018-01-26'"}).values('title','is_recent')
    # print(date)

    # article_obj = Article.objects.extra(select={'standard_time':"strftime('%%Y-%%m-%%d',create_time)"})    # sqlite数据库的用法
    # 方式1：
    # date_list = Article.objects.filter(user=user_obj).extra(select={'Y_m_date':"date_format(create_time,'%%Y-%%m')"}).\
    #                               values('Y_m_date').annotate(c=Count('nid')).values_list('Y_m_date','c')
    # print('date_list:', date_list)

    # 方式2：  直接使用django提供的TruncMonth函数，推荐
    # date_list2 = Article.objects.filter(user=user_obj).annotate(month=TruncMonth('create_time'))\
    #                             .values('month').annotate(c=Count('nid')).values('month','c')
    # print(date_list2)
    #  报错 ValueError: Database returned an invalid datetime value. Are time zone definitions for your database installed?

    return render(request, 'home_site.html',locals())


# def get_classification_data(username):
#     user_obj = UserInfo.objects.filter(username=username).first()
#     blog_obj = user_obj.blog
#     cate_list = Category.objects.values('pk').filter(blog=blog_obj).annotate(count=Count('article__title')).values_list('title', 'count')
#     tag_list = Tag.objects.values('pk').filter(blog=blog_obj).annotate(count=Count('article__title')).values('title', 'count')
#     date_list1 = Article.objects.filter(user=user_obj).extra(select={'Y_m_date': "date_format(create_time,'%%Y-%%m')"}). \
#                                 values('Y_m_date').annotate(c=Count('nid')).values('Y_m_date', 'c')
#
#     return {'user_obj':user_obj,'blog_obj':blog_obj,'cate_list':cate_list,'tag_list':tag_list,'date_list1':date_list1}


def article_detail(request,username,article_id):

    # print('username1:', username)

    article_obj = Article.objects.filter(pk=article_id).first()

    # 过滤出当前文章的评论列表
    comment_list = Comment.objects.filter(article_id=article_id)


    return render(request,'article_detail.html', locals())


# 点赞视图函数
def digg(request):

    print('request.POST:',request.POST)
    # print(type(request.user))
    print('request.user:',request.user)

    article_id = request.POST.get('article_id')

    # is_up1 = request.POST.get('is_up')
    # print(is_up1)
    # print(type(is_up1))     # str
    is_up = json.loads(request.POST.get('is_up'))
    # print(is_up)
    # print(type(is_up))    # bool

    # 点赞人即当前登录人
    user_id = request.user.pk

    # 判断当前用户是否对当前文章做过点赞或反对操作
    ard_obj = ArticleUpDown.objects.filter(user_id=user_id,article_id=article_id).first()

    response = {
        'state':True,
        # 'msg':None
    }

    if not ard_obj:
        # 将点赞/反对的数据添加到ArticleUpDown表
        ard = ArticleUpDown.objects.create(article_id=article_id,user_id=user_id,is_up=is_up)

        # 更新Article表的up_count/down_count字段
        queryset = Article.objects.filter(pk=article_id)
        if is_up:
            queryset.update(up_count=F('up_count')+1)
        else:
            queryset.update(down_count=F('down_count')+1)
    else:
        response['state'] = False
        response['handled'] = ard_obj.is_up

    return JsonResponse(response)


def comment(request):

    print('request.POST:',request.POST)

    user_id = request.user.pk
    article_id = request.POST.get('article_id')
    content = request.POST.get('content')
    pid = request.POST.get('pid')

    article_obj = Article.objects.filter(pk=article_id).first()

    # 事物操作
    with transaction.atomic():    # 事物语法
        # 下面的两行事物同进退，要么都成功，要么都失败
        comment_obj = Comment.objects.create(user_id=user_id, article_id=article_id, content=content,
                                             parent_comment_id=pid)
        # print('comment_obj:', comment_obj)
        Article.objects.filter(pk=article_id).update(comment_count=F('comment_count')+1)


    # comment_obj = Comment.objects.create(user_id=user_id,article_id=article_id,content=content,parent_comment_id=pid)
    # print('comment_obj:',comment_obj)

    # 发送邮件
    # send_mail(
    #     '您的文章%s新增了一条评论内容' % article_obj.title,
    #     content,
    #     settings.EMAIL_HOST_USER,
    #     ['xxx@qq.com']
    # )    # 速度太慢，提交评论是会卡2s，主要耗时在连接网络

    # 单独开一个线程来执行该任务，不影响主程序继续往下走
    t = Thread(target=send_mail,args=('您的文章%s新增了一条评论内容' % article_obj.title, content, settings.EMAIL_HOST_USER,['xxx@qq.com']))
    t.start()

    response = {
        'create_time':comment_obj.create_time.strftime('%Y-%m-%d %X'),
        'username':request.user.username,
        # 'username':comment_obj.user.username,
        'content':content
    }

    # response = {}
    # response['create_time']=comment_obj.create_time.strftime('%Y-%m-%d %X')
    # response['username']=request.user.username
    # response['content'] = content

    return JsonResponse(response)


def get_comment_tree(request):

    article_id = request.GET.get('article_id')

    ret1 = Comment.objects.filter(article_id=article_id).values('pk','content','parent_comment_id')
    ret = list(ret1)

    return JsonResponse(ret,safe=False)

# 给回调函数successs用的变量，一般都是通过response构造的字典，将需要的变量放到该字典中
# 再通过return JsonResponse(response)返回给回调函数successs中的data，拿去用


@login_required
def cn_backend(request):

    article_list = Article.objects.filter(user=request.user)

    return render(request,'backend/backend.html',locals())


@login_required
def add_articles(request):
    if request.method == 'POST':
        title = request.POST.get('title')
        content = request.POST.get('content')

        # 摘要的获取：调用BeautifulSoup()方法，获取文本进行截取，赋值给desc字段
        soup = BeautifulSoup(content, 'html.parser')

        # 过滤
        for tag in soup.find_all():
            print(tag.name)
            # 过滤
            if tag.name == 'script':
                tag.decompose()

        # 只取soup的文本部分
        desc = soup.text[0:150]

        Article.objects.create(title=title,content=str(soup),desc=desc,user=request.user)

        return redirect('/cn_backend/')

    return render(request,'backend/add_articles.html')


# 对用户基于文本编辑器上传的文件下载到本地
def upload(request):
    print(request.FILES)
    img = request.FILES.get('upload_img')
    print(img.name)

    path = os.path.join(settings.MEDIA_ROOT,'add_article_img',img.name)
    with open(path,'wb') as f:
        for line in f:
            f.write(line)

    response = {
        'error':0,
        'url':'/media/add_article_img/%s' % img.name,
    }

    return HttpResponse(json.dumps(response))
