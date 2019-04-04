# *_* coding:utf-8 *_*
# created by Soft on 2019/3/26 15:46
import random
from PIL import Image,ImageDraw,ImageFont


def get_random_color():
    return (random.randint(0, 256), random.randint(0, 256), random.randint(0, 256))

a = get_random_color()
print(a)

# for i in range(5):
#     random_num = str(random.randint(0, 9))
#     random_lower_alpha = chr(random.randint(97, 122))
#     random_upper_alpha = chr(random.randint(65, 90))
#     random_char = random.choice([random_num, random_lower_alpha, random_upper_alpha])

#     # 保存验证码
#     valid_code_str += random_char
