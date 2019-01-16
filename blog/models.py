from django.db import models

# Create your models here.

from django.contrib.auth.models import User,AbstractUser


class UserInfo(AbstractUser):
    '''
    用户信息
        用了继承关系AbstractUser之后，不会再生成auth_user表了
    '''
    nid = models.AutoField(primary_key=True)
    telephone = models.CharField(max_length=11,null=True,unique=True)
    avatar = models.FileField(upload_to='avatars/',default='/avatars/default.png')
    create_time = models.DateTimeField(verbose_name='创建时间',auto_now_add=True)

    blog = models.OneToOneField(to='Blog',to_field='nid',null=True,on_delete=models.CASCADE)

    def __str__(self):
        return self.username


class Blog(models.Model):
    '''
    博客信息表（用户站点表，即每个用户的主页）
    '''
    nid = models.AutoField(primary_key=True)
    title = models.CharField(verbose_name='个人博客标题',max_length=64)
    site_name = models.CharField(verbose_name='站点名称',max_length=64)
    theme = models.CharField(verbose_name='博客主题',max_length=32)

    def __str__(self):
        return self.title


class Category(models.Model):
    '''
    博主个人文章分类表
    '''
    nid = models.AutoField(primary_key=True)
    title = models.CharField(verbose_name='分类标题',max_length=32)
    blog = models.ForeignKey(verbose_name='所属博客',to='Blog',to_field='nid',on_delete=models.CASCADE)

    def __str__(self):
        return self.title


class Tag(models.Model):
    '''
    博主个人文章标签表
    '''
    nid = models.AutoField(primary_key=True)
    title = models.CharField(verbose_name='标签名称', max_length=32)
    blog = models.ForeignKey(verbose_name='所属博客', to='Blog', to_field='nid',on_delete=models.CASCADE)

    def __str__(self):
        return self.title


class Article(models.Model):
    nid = models.AutoField(primary_key=True)
    title = models.CharField(max_length=50,verbose_name='文章标题')
    desc = models.CharField(max_length=255,verbose_name='文章描述')
    create_time = models.DateTimeField(verbose_name='创建时间',auto_now_add=True)
    content = models.TextField()

    # 文章的评论数、点赞数，涉及到跨表查询（效率低），所以此处添加了下面3分字段
    # 这3个字段只在添加时涉及到跨表查询，而查询次数远大于添加次数，所以此处是保证
    # 查询（占70%以上）的效率，而牺牲了增删改（占30%以下）的效率
    comment_count = models.IntegerField(default=0)
    up_count = models.IntegerField(default=0)
    down_count = models.IntegerField(default=0)

    user = models.ForeignKey(verbose_name='作者',to='UserInfo',to_field='nid',on_delete=models.CASCADE)
    # 一对多，一个分类下面可以有多篇文章，一篇文章只能属于一个分类
    category = models.ForeignKey(to='Category',to_field='nid',null=True,on_delete=models.CASCADE)
    # 多对多：一篇文章可以有多个标签，一个标签里也有多篇文章
    tags = models.ManyToManyField(
        to='Tag',
        through='Article2Tag',     # 中间模型，手动创建关联表
        through_fields=('article','tag'),
    )

    def __str__(self):
        return self.title


class Article2Tag(models.Model):
    nid = models.AutoField(primary_key=True)
    article = models.ForeignKey(verbose_name='文章',to='Article',to_field='nid',on_delete=models.CASCADE)
    tag = models.ForeignKey(verbose_name='标签',to='Tag',to_field='nid',on_delete=models.CASCADE)

    class Meta:     # article和tag联合唯一
        unique_together = [
            ('article','tag'),
        ]
        def __str__(self):
            v = self.article.title + '---' + self.tag.title
            return v


class ArticleUpDown(models.Model):
    '''
    点赞表
    '''
    nid = models.AutoField(primary_key=True)
    # 一个用户可以点多个赞，一个赞只能属于一个用户
    user = models.ForeignKey('UserInfo', null=True,on_delete=models.CASCADE)
    # 一篇文章可以有多个赞，一个赞只能属于一篇文章
    article = models.ForeignKey('Article', null=True,on_delete=models.CASCADE)
    is_up = models.BooleanField(default=True)

    class Meta:
        unique_together = [
            ('article','user'),
        ]


class Comment(models.Model):
    '''
    评论表：
        哪一个用户，对哪一篇文章，在什么时间，做了什么评论
    '''
    nid = models.AutoField(primary_key=True)

    # 一个用户可以有多个评论，一个评论只能属于一个用户
    user = models.ForeignKey(verbose_name='评论者',to='UserInfo',to_field='nid',on_delete=models.CASCADE)
    # 一篇文章可以有多个评论，一个评论只能属于一篇文章
    article = models.ForeignKey(verbose_name='评论文章',to='Article',to_field='nid',on_delete=models.CASCADE)
    create_time = models.DateTimeField(verbose_name='创建时间',auto_now_add=True)
    content = models.CharField(verbose_name='评论内容',max_length=25)

    # 自关联
    # parent_comment_id = models.ForeignKey('Comment',null=True)
    # parent_comment_id = models.ForeignKey('self',null=True)
    # 没必要加id，因为ForeignKey默认会给补上id
    parent_comment = models.ForeignKey('self',null=True,on_delete=models.CASCADE)

    def __str__(self):
        return self.content
