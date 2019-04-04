# *_* coding:utf-8 *_*
# created by Soft on 2019/1/21 20:04

from django import forms
from django.forms import widgets
from blog.models import UserInfo
from django.core.exceptions import NON_FIELD_ERRORS, ValidationError


class UserForm(forms.Form):
    user = forms.CharField(max_length=32, label='用户名',
                           error_messages={'required': '该字段不能为空'},
                           widget=widgets.TextInput(attrs={'class':'form-control','placeholder':'登录用户名，不少于4个字符'}))
    pwd = forms.CharField(max_length=32,label='密码',
                          error_messages={'required': '该字段不能为空'},
                          widget=widgets.PasswordInput(attrs={'class': 'form-control','placeholder':'至少8位，必须包含字母、数字、特殊字符'}))
    r_pwd = forms.CharField(max_length=32,label='确认密码',
                          error_messages={'required': '该字段不能为空'},
                          widget=widgets.PasswordInput(attrs={'class': 'form-control','placeholder':'请输入确认密码'}))
    email = forms.EmailField(label='邮箱', error_messages={'required': '该字段不能为空', 'invalid': '邮箱格式错误'},
                             widget=widgets.EmailInput(attrs={'class': 'form-control', 'placeholder': '需要通过邮件激活账户'}))
    tel = forms.CharField(label='手机号',
                          error_messages={'required': '该字段不能为空', 'invalid': '格式错误'},
                          widget=widgets.TextInput(attrs={'class': 'form-control', 'placeholder': '激活账户需要手机短信验证'}))

    def clean_user(self):    # 局部钩子——校验用户是否已经被注册
        val = self.cleaned_data.get('user')
        user_obj = UserInfo.objects.filter(username=val).first()
        if not user_obj:   # 该用户名未被注册，直接返回用户输入的名字val
            return val
        else:
            raise ValidationError('该用户已注册')

    def clean_tel(self):   # 局部钩子——校验手机号格式
        val = self.cleaned_data.get('tel')
        if len(val) == 11:
            return val
        else:
            raise ValidationError('手机号格式错误！')

    def clean(self):    # 全局钩子
        pwd = self.cleaned_data.get('pwd')
        r_pwd = self.cleaned_data.get('r_pwd')

        if pwd and r_pwd:
            if pwd == r_pwd:
                return self.cleaned_data
            else:
                raise ValidationError('两次密码不一致')
        else:   # 但凡有一个为none，就不会通过前面的字段校验，所以此处不对其做任何处理，直接返回其原本应有的值cleaned_data
            return self.cleaned_data







