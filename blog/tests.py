from django.test import TestCase

print('hello'[0:150])


from bs4 import BeautifulSoup
s1 = '<h1>hello</h1><span>123</span>'
# html.parser为解析器
soup = BeautifulSoup(s1,'html.parser')
print(soup.text)


# xss攻击验证：验证是否含有非法标签script
s2 = '<h1>hello</h1><span>123</span><script>alert(123)</script>'
soup = BeautifulSoup(s2,'html.parser')
print(soup.find_all())

for tag in soup.find_all():
    print(tag.name)
    # 过滤
    if tag.name == 'script':
        tag.decompose()    # 删除该标签

print(str(soup))