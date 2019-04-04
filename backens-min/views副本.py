from django.shortcuts import render,redirect,HttpResponse
from django.http import JsonResponse
from django.contrib import auth
from blog.utils.validCode import get_valid_code_img
from blog.Myforms import UserForm
from blog.models import *
from django.db.models import Avg,Max,Min,Count
from django.db.models.functions import TruncMonth


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


def get_validCode_img(request):
    '''
    基于PIL模块，动态生成响应状态码
    :param request:
    :return:
    '''
    data = get_valid_code_img(request)
    return HttpResponse(data)


def index(request):

    article_list = Article.objects.all()
    print(article_list)


    return render(request,'index.html', {'article_list':article_list})


def register(request):
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
            email = form.cleaned_data.get('email')
            tel = form.cleaned_data.get('tel')
            user = form.cleaned_data.get('user')
            print('user:', user)
            pwd = form.cleaned_data.get('pwd')

            avatar_obj = request.FILES.get('avatar')

            extra = {}
            UserInfo.objects.create_user(username=user, password=pwd, email=email, telephone=tel, **extra)
            if avatar_obj:
                extra['avatar'] = avatar_obj
        else:
            response['msg'] = form.errors

        return JsonResponse(response)

    form = UserForm()     # 渲染页面
    return render(request,'register.html',locals())


def logout(request):
    auth.logout(request)   # request.session.flush()

    return redirect('/login/')


def home_site(request,username,**kwargs):

    print('username:', username)
    print('kwargs:',kwargs)

    user_obj = UserInfo.objects.filter(username=username).first()
    if not user_obj:
        return render(request,'not_found.html')

    blog_obj = user_obj.blog

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

    cate_list = Category.objects.values('pk').filter(blog=blog_obj).annotate(count=Count('article__title')).values_list('title', 'count')

    tag_list = Tag.objects.values('pk').filter(blog=blog_obj).annotate(count=Count('article__title')).values('title', 'count')

    date_list1 = Article.objects.filter(user=user_obj).extra(select={'Y_m_date':"date_format(create_time,'%%Y-%%m')"}).\
                                  values('Y_m_date').annotate(c=Count('nid')).values('Y_m_date','c')

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

    # context = get_classification_data(username)

    article_obj = Article.objects.filter(pk=article_id).first()


    return render(request,'article_detail.html', locals())







