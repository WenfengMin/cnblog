from django.db import models
from django.contrib.auth.models import User,AbstractUser

class UserInfo(AbstractUser):
    nid =            models.AutoField(primary_key=True)
    telephone =      models.CharField(max_length=11,null=True,unique=True)
    avatar =         models.FileField(upload_to='avatars/',default='/avatars/default.png')
    create_time =    models.DateTimeField(verbose_name='创建时间',auto_now_add=True)
    comment_count =  models.IntegerField(default=0)
    price =          models.DecimalField(max_digits=8, decimal_places=2)  # 浮点数 222234.43
    email =          models.EmailField(verbose_name='邮箱', max_length=32)
    content =        models.TextField()    # 用于存储大容量的文本
    is_up =          models.BooleanField(default=True)

    blog =           models.OneToOneField(to='Blog',to_field='nid',null=True,on_delete=models.CASCADE)
    blog2 =          models.ForeignKey(verbose_name='所属博客',to='Blog',to_field='nid',on_delete=models.CASCADE)
    parent_comment = models.ForeignKey('self',null=True,on_delete=models.CASCADE)     # 自关联

    roles =          models.ManyToManyField(verbose_name='拥有的所有角色',to='Role',blank=True)
    tags =           models.ManyToManyField(
        to='Tag',
        through='Article2Tag',     # 中间模型，手动创建关联表
        through_fields=('article','tag'),
    )


class Article2Tag(models.Model):
    article =      models.ForeignKey(verbose_name='文章',to='Article',to_field='nid',on_delete=models.CASCADE)
    tag =          models.ForeignKey(verbose_name='标签',to='Tag',to_field='nid',on_delete=models.CASCADE)

    class Meta:     # article和tag联合唯一
        unique_together = [
            ('article','tag'),
        ]

class ArticleUpDown(models.Model):
    user =        models.ForeignKey('UserInfo', null=True,on_delete=models.CASCADE)
    article =     models.ForeignKey('Article', null=True,on_delete=models.CASCADE)

    class Meta:     # article和user联合唯一
        unique_together = [
            ('article','user'),
        ]


