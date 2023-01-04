from peewee import *

from goods_srv.settings import settings
from passlib.hash import pbkdf2_sha256


class BaseModel(Model):
    class Meta:
        database = settings.db


class User(BaseModel):
    GENDER_CHOICES  = (
        ('female', '女'),
        ('male', '男'),
    )
    ROLE_CHOICES = (
        ('0', 'admin'),
        ('1', 'user'),
    )
    mobile = CharField(max_length=11,index=True,unique=True,verbose_name='手机号码')   #用索引方便查找，unique表示唯一
    password = CharField(max_length=100,verbose_name='密码')  #密码不能明文，所以是加密的，长度设置大一点   密文要求不能反解出来
    nickname = CharField(max_length=20,null=True,verbose_name='昵称')   #可空
    head_url= CharField(max_length=200,null=True,verbose_name='头像')   #可空
    birthday = DateField(null=True,verbose_name='生日')        #可空，生日的形式，各语言不太一样，待定
    address = CharField(null=True,verbose_name='地址')               #可空
    desc = TextField(null=True,verbose_name="个人简介")     #长度可能需要大一点，用Textfield ,可空
    gender = CharField(max_length=6,choices=GENDER_CHOICES,null=True,verbose_name="性别")  #枚举类型
    role = IntegerField(default=1,choices=GENDER_CHOICES,verbose_name='用户角色')  #枚举类型，默认为普通用户

if __name__ == '__main__':
    settings.db.create_tables([User])

#密码需要加密
#     m=hashlib.md5()
#     #m.update('123456'.encode('utf8'))#e10adc3949ba59abbe56e057f20f883e
#     m.update(b'123456')#e10adc3949ba59abbe56e057f20f883e
#     print(m.hexdigest())
#常用密码可能还是会被破解，需要加上salt值
#     salt='alice'
#     password='123456'
#     m.update((salt+password).encode('utf8'))
#     print(m.hexdigest())
# #为了不需要记录salt，可以用paslib库
#     from passlib.hash import pbkdf2_sha256
#     hash = pbkdf2_sha256.hash(password)
#     print(hash)
#     print(pbkdf2_sha256.verify(password,hash))

#批量创建用户
    for i in range(10):
        user=User()
        user.nickname=f"test00{i}"
        user.mobile=f'1881234567{i}'
        user.password=pbkdf2_sha256.hash('admin123')
        user.save()

#时间转换  date转换字符串
#     for user in User.select():
#         import time
#         from datetime import date
#         if user.birthday    :
#             u_time = time.mktime(user.birthday.timetuple())  #2022-07-20
#             print(u_time)#float类型  1658246400.
#             print(date.fromtimestamp(u_time))  #转换回来日期

#     users = User.select()
#     users = users.limit(2).offset(2)#test002  test003
#     users = users.limit(8).offset(4)#test004--test009
#     users = users.limit(2).offset(9)#test009
#     for user in users:
#         print(user.nickname)



