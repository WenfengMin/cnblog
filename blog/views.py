from django.shortcuts import render,redirect,HttpResponse
from PIL import Image,ImageDraw,ImageFont
import random
from io import BytesIO
from django.http import JsonResponse

# Create your views here.


def login(request):

    if request.method == 'POST':
        response = {
            'user':None,
            'msg':None
        }
        user = request.POST.get('user')
        pwd = request.POST.get('pwd')
        valid_code = request.POST.get('valid_code')

        valid_code_str=request.session.get('valid_code_str')
        if valid_code.upper() == valid_code_str:
            pass
        else:
            response['msg']='Valid code error'

        return JsonResponse(response)


    return render(request,'login.html')


def get_validCode_img(request):
    # 方式1： 写死了
    # with open('1.jpg','rb') as f:
    #     data = f.read()

    def get_random_color():
        return (random.randint(0,256),random.randint(0,256),random.randint(0,256))

    # 方式2：随机生成一张图片，图像处理模块pillow——PIL
    # pip install pillow  from PIL import Image
    # 磁盘处理速度太慢（open都是磁盘操作），所以不用该方法
    # img = Image.new('RGB',(200,34),color=get_random_color())
    # f = open('validCode.png','wb')  # 句柄
    # img.save(f,'png')
    # # with open('validCode.png','wb') as f:
    # #     img.save(f,'png')
    #
    # with open('validCode.png','rb') as f:
    #     data = f.read()

    # 方式3：BytesIO是一个内存管理工具，不再用文件操作（涉及到磁盘，速度慢），直接内存处理，速度快
    # img = Image.new('RGB',(220,34),color=get_random_color())
    # f = BytesIO()    # 内存句柄
    # img.save(f,'png')
    # data = f.getvalue()

    # 方式4：
    img = Image.new('RGB', (220, 40), color=get_random_color())   # 画板
    # 该画笔draw只为img这个画板服务
    draw = ImageDraw.Draw(img)      # 画笔
    # 设置字体
    kumo_font = ImageFont.truetype('static/blog/font/kumo-2.ttf',size=28)

    valid_code_str = ''
    # 生成随机字符串
    for i in range(5):
        random_num = str(random.randint(0,9))
        random_lower_alpha = chr(random.randint(97,122))
        random_upper_alpha = chr(random.randint(65,90))
        random_char = random.choice([random_num,random_lower_alpha,random_upper_alpha])
        draw.text((i*40+20,2),random_char,get_random_color(),font=kumo_font)

        # 保存验证码字符串
        valid_code_str += random_char

    # 噪点躁线
    # width = 220
    # height = 40
    # for i in range(10):   # 躁线
    #     x1 = random.randint(0, width)
    #     x2 = random.randint(0, width)
    #     y1 = random.randint(0, height)
    #     y2 = random.randint(0, height)
    #     draw.line((x1, y1, x2, y2), fill=get_random_color())
    #
    # for i in range(80):   # 噪点
    #     draw.point([random.randint(0, width), random.randint(0, height)], fill = get_random_color())
    #     x = random.randint(0, width)
    #     y = random.randint(0, height)
    #     draw.arc((x, y, x + 4, y + 4), 0, 90, fill=get_random_color())

    print(valid_code_str)
    # 将该随机验证码保存到session中，每个用户单独保存一份，便于验证时使用，与用户输入的对比
    request.session['valid_code_str']=valid_code_str

    f = BytesIO()  # 内存句柄
    img.save(f, 'png')
    data = f.getvalue()

    return HttpResponse(data)

