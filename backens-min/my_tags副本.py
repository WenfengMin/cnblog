# -*- coding:utf-8 -*-
# created by Soft on  2019/1/29 23:23

from django import template
from blog.models import *
from django.db.models import Avg,Max,Min,Count


register = template.Library()


# @register.simple_tag
# def multi_tag(x,y):        # 自定义标签
#     return x*y


@register.inclusion_tag('classification.html')
def get_classification_style(username):
    user_obj = UserInfo.objects.filter(username=username).first()
    blog_obj = user_obj.blog
    cate_list = Category.objects.values('pk').filter(blog=blog_obj).annotate(count=Count('article__title')).values_list(
        'title', 'count')
    tag_list = Tag.objects.values('pk').filter(blog=blog_obj).annotate(count=Count('article__title')).values_list('title',
                                                                                                             'count')
    date_list1 = Article.objects.filter(user=user_obj).extra(select={'Y_m_date': "date_format(create_time,'%%Y-%%m')"}). \
        values('Y_m_date').annotate(c=Count('nid')).values_list('Y_m_date', 'c')

    # 这些数据都是给classification.html模板用的，用于其页面的渲染

    return {'user_obj':user_obj,'blog_obj':blog_obj,'cate_list':cate_list,'tag_list':tag_list,'date_list1':date_list1}


# inclusion_tag用法解析：
#     执行get_classification_style函数后，会把里面的变量都交给classification.html文件，进行模板渲染
#     所以，调用get_classification_style()函数，实际上得到的是一个渲染好的classification.html文件

# 与直接调用函数相比（直接调用函数，得到返回值，返回值需要传给模板，模板渲染后才能得到页面，共分2步），
# 而用inclusion_tag，只需要调用get_classification_style函数即可得到渲染的页面，1步就完成了,即将数据和样式结合在一起了
# 该方法主要用于解决数据复用性的问题，


