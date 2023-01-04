from datetime import datetime

from peewee import *
from playhouse.shortcuts import  ReconnectMixin
from playhouse.pool import PooledMySQLDatabase

from playhouse.mysql_ext import JSONField

class ReconnectMySQLDatabase(ReconnectMixin, PooledMySQLDatabase):
    # python的mro
    pass
db = ReconnectMySQLDatabase("mxshop_goods_srv",host='192.168.18.160',port=3306,user='root',password='root')


class BaseModel(Model):
    add_time=DateTimeField(default=datetime.now,verbose_name="记录生成时间")
    #逻辑删除，
    is_deleted=BooleanField(verbose_name="删除时间",default=False)
    update_time=DateTimeField(default=datetime.now,verbose_name="更新时间")

    #save方法时，如何只修改update_time

    # 每个继承的不用单独处理
    def save(self,*args,**kwargs):
        if self._pk is not None:
            self.update_time=datetime.now()
        return super().save(*args,**kwargs)

    # 类删除方法 ，加个参数
    @classmethod
    def delete(cls,Permanently=False):#true代表永久删除
        if Permanently:
            return super().delete()
        else:
            return super().update(is_deleted=True)
        # return ModelDelete(cls)
    #实例的删除方法
    def delete_instance(self,Permanently=False, recursive=False, delete_nullable=False):
        if Permanently:
            return self.delete(Permanently).where(self._pk_expr()).execute()
        else:
            self.is_deleted=True
            self.save()

    #查询 select is_deleted=false
    @classmethod
    def select(cls, *fields):
        return super().select(*fields).where(cls.is_deleted==False)

    class Meta:
        database=db


class Category(BaseModel):#如果是Model，报错database attribute does not appear to be set on the model: <Model: Category>
    name = CharField(max_length=20,verbose_name="名称")
    # 子类指向父类
    parent_category = ForeignKeyField("self", verbose_name="父类别",null = True)  # 一级没有父类别
    level = IntegerField(default=1,verbose_name="级别")
    is_tab = BooleanField(default=False,verbose_name="是否显示在首页tab")

class Brands(BaseModel):
    #品牌
    name = CharField(max_length=50, verbose_name="名称", index=True, unique=True)
    logo = CharField(max_length=200, null=True, verbose_name="图标", default="")


class Goods(BaseModel):
    """
    商品， 分布式的事务最好的解决方案 就是不要让分布式事务出现
    """
    category = ForeignKeyField(Category, verbose_name="商品类目", on_delete='CASCADE')
    brand = ForeignKeyField(Brands, verbose_name="品牌", on_delete='CASCADE')
    on_sale = BooleanField(default=True, verbose_name="是否上架")
    goods_sn = CharField(max_length=50, default="", verbose_name="商品唯一货号")
    name = CharField(max_length=100, verbose_name="商品名")
    click_num = IntegerField(default=0, verbose_name="点击数")
    sold_num = IntegerField(default=0, verbose_name="商品销售量")
    fav_num = IntegerField(default=0, verbose_name="收藏数") #库存是电商中一个重要的环节
    market_price = FloatField(default=0, verbose_name="市场价格")
    shop_price = FloatField(default=0, verbose_name="本店价格")
    goods_brief = CharField(max_length=200, verbose_name="商品简短描述")
    ship_free = BooleanField(default=True, verbose_name="是否承担运费")
    images = JSONField(verbose_name="商品轮播图")
    desc_images = JSONField(verbose_name="详情页图片")
    goods_front_image = CharField(max_length=200, verbose_name="封面图")
    is_new = BooleanField(default=False, verbose_name="是否新品")
    is_hot = BooleanField(default=False, verbose_name="是否热销")


class GoodsCategoryBrand(BaseModel):
    #品牌分类
    id = AutoField(primary_key=True, verbose_name="id")#手动设置，避免联合主键影响
    category = ForeignKeyField(Category, verbose_name="类别")
    brand = ForeignKeyField(Brands, verbose_name="品牌")

    class Meta:
        indexes = (
            #联合主键
            (("category", "brand"), True),
        )


class Banner(BaseModel):
    """
    轮播的商品
    """
    image = CharField(max_length=200, default="", verbose_name="图片url")
    url = CharField(max_length=200, default="", verbose_name="访问url")
    index = IntegerField(default=0, verbose_name="轮播顺序")

if __name__=='__main__':
    #测试save delete select

    db.create_tables([Category,Goods,Brands,GoodsCategoryBrand,Banner])
    #
    # c1=Category(name="alice1",level="1")
    # c2=Category(name="alice2",level="1")
    # c1.save()
    # c2.save()

    # 删除
    # c1=Category.get(Category.id==1)
    # c1.delete_instance()

    #查询不到alice1
    # for c in Category.select():
    #     print(c.name)

    # Category.delete().where(Category.id==2).execute()

    # 永久删除，改成未删除0
    # c1=Category.get(Category.id==1)
    # c1.delete_instance(Permanently=True)


