# *_* coding:utf-8 *_*
# created by Soft on 2019/1/16 21:21

from PIL import Image,ImageDraw,ImageFont
import random
from io import BytesIO


def get_random_color():
    return (random.randint(0, 256), random.randint(0, 256), random.randint(0, 256))


def get_valid_code_img(request):
    # 方式1： 写死了
    # with open('1.jpg','rb') as f:
    #     data = f.read()

    # 方式2：随机生成一张图片，图像处理模块pillow——PIL
    # 安装：pip install pillow  from PIL import Image
    # 第一步：生成随机颜色的图片对象
    # color可以接受指定的如red；也可以接收一个元组，表示颜色三要素
    # img = Image.new('RGB',(200,34),color=get_random_color())   # 图片对象
    # 第二步：将图片加载到磁盘
    # f = open('validCode.png','wb')  # 句柄，生成随机颜色的图片
    # img.save(f,'png')      # 保存图片，默认保存到根路径下
    # # with open('validCode.png','wb') as f:   # 生成随机颜色的图片，与上面二选一
    # #     img.save(f,'png')
    # 第三步：从磁盘中读取出图片数据
    # with open('validCode.png','rb') as f:   # 读取刚刚生成的随机颜色图片
    #     data = f.read()
    # 磁盘处理速度太慢（open都是磁盘操作），所以不用该方法

    # 方式3：BytesIO是一个内存管理工具，不再用文件操作（涉及到磁盘，速度慢），直接内存处理，速度快
    # img = Image.new('RGB',(220,34),color=get_random_color())
    # f = BytesIO()    # 内存句柄
    # img.save(f,'png')   # 存数据
    # data = f.getvalue() # 取数据

    # 方式4：
    img = Image.new('RGB', (220, 40), color=get_random_color())  # 画板
    # 该画笔draw只为img这个画板服务
    draw = ImageDraw.Draw(img)  # 画笔，可以往画板上写文字（包括下方生成的随机字符串）
    # 设置字体
    kumo_font = ImageFont.truetype('static/blog/font/kumo-2.ttf', size=28)

    valid_code_str = ''
    # 生成随机字符串
    for i in range(5):
        random_num = str(random.randint(0, 9))
        random_lower_alpha = chr(random.randint(97, 122))
        random_upper_alpha = chr(random.randint(65, 90))
        random_char = random.choice([random_num, random_lower_alpha, random_upper_alpha])
        # 往画板上画文字，（i * 40 + 20, 2）表示坐标，每个字符往右移40个单位
        draw.text((i * 40 + 20, 2), random_char, get_random_color(), font=kumo_font)

        # 保存验证码
        valid_code_str += random_char

    # 噪点躁线
    width = 220
    height = 40
    # for i in range(10):   # 躁线
    #     x1 = random.randint(0, width)
    #     x2 = random.randint(0, width)
    #     y1 = random.randint(0, height)
    #     y2 = random.randint(0, height)
          # 往画板上画线
    #     draw.line((x1, y1, x2, y2), fill=get_random_color())
    #
    for i in range(80):   # 噪点
        # 往画板上画点
        draw.point([random.randint(0, width), random.randint(0, height)], fill = get_random_color())
        x = random.randint(0, width)
        y = random.randint(0, height)
        draw.arc((x, y, x + 4, y + 4), 0, 90, fill=get_random_color())

    print(valid_code_str)

    # 将该随机验证码保存到session中，每个用户单独保存一份，该变量就成了该用户的全局变量，
    # 其他视图函数下也可以调用了。便于验证时，与用户输入的对比
    request.session['valid_code_str'] = valid_code_str

    '''
    1 sdajjfdsf7fdsf    生成随机字符串
    2 COOKIE {‘session_id’:sdajjfdsf7fdsf}     # 设置cookie
    3 django-session表：      # 存储到django-session表
            session-key:sdajjfdsf7fdsf
            session-data:{'valid_code_str':'124gs'}
    '''

    f = BytesIO()  # 内存句柄
    img.save(f, 'png')
    data = f.getvalue()

    return data
