import grpc
from loguru import logger
from peewee import DoesNotExist

from goods_srv.proto import goods_pb2_grpc, goods_pb2
from goods_srv.model.models import Goods, Category, Brands, Banner, GoodsCategoryBrand
from goods_srv.proto.goods_pb2 import BatchGoodsIdInfo

from google.protobuf import empty_pb2


class GoodsService(goods_pb2_grpc.GoodsServicer):
    def convert_model_to_message(self, goods):
        rsp_info = goods_pb2.GoodsInfoResponse()

        rsp_info.id = goods.id
        rsp_info.categoryId = goods.category_id
        rsp_info.name = goods.name
        rsp_info.goodsSn = goods.goods_sn
        rsp_info.clickNum = goods.click_num
        rsp_info.soldNum = goods.sold_num
        rsp_info.favNum = goods.fav_num
        rsp_info.marketPrice = goods.market_price
        rsp_info.shopPrice = goods.shop_price
        rsp_info.goodsBrief = goods.goods_brief
        rsp_info.shipFree = goods.ship_free
        rsp_info.goodsFrontImage = goods.goods_front_image
        rsp_info.isNew = goods.is_new
        rsp_info.isHot = goods.is_hot
        rsp_info.onSale = goods.on_sale

        rsp_info.category.id = goods.category.id
        rsp_info.category.name = goods.category.name

        rsp_info.brand.id = goods.brand.id
        rsp_info.brand.name = goods.brand.name
        rsp_info.brand.logo = goods.brand.logo
        rsp_info.images.extend(goods.desc_images)
        rsp_info.descImages.extend(goods.desc_images)
        return rsp_info

    @logger.catch
    def GoodsList(self, request: goods_pb2.GoodsFilterRequest, context):
        # 返回值
        rsp = goods_pb2.GoodsListResponse()

        goods = Goods.select()
        if request.keyWords:
            goods = goods.where(Goods.name.contains(request.keyWords))
        if request.isHot:
            goods = goods.filter(Goods.is_hot == True)
        if request.isNew:
            goods = goods.filter(Goods.is_new == True)
        if request.priceMin:
            goods = goods.filter(Goods.shop_price >= request.priceMin)
        if request.priceMax:
            goods = goods.filter(Goods.shop_price <= request.priceMax)
        if request.brand:
            goods = goods.filter(Goods.brand == request.brand)

        # 先pass，写好分页。
        if request.topCategory:
            # 按类别查询，首先查询根据类别id查询level
            category = Category.get(Category.id == request.topCategory)
            level = category.level

            categorys_contained = []  # 需要查询哪些类
            # 分类查询：
            # 查询第一级的分类，要返回该一级下面所有二级和三级的商品
            # 查询第二级的分类，要返回该二级下面所有第三级的商品
            if level == 1:
                c2 = Category.alias()
                categorys = Category.select().where(Category.parent_category_id.in_(
                    c2.select(c2.id).where(c2.parent_category_id == request.topCategory)))
                for category in categorys:
                    categorys_contained.append(category.id)
            elif level == 2:
                categorys = Category.select().wheree(Category.parent_category_id == request.topCategory)
                for category in categorys:
                    categorys_contained.append(category.id)
            elif level == 3:
                categorys_contained.append(request.topCategory)

            goods = goods.where(Goods.category_id.in_(categorys_contained))
        # 默认值为第一页，每页十个
        start = 0
        pageSize = 10

        if request.pagePerNums:
            pageSize = request.pagePerNums
        if request.pages:
            start = +pageSize * (start - 1)

        # 记录总数，查询出数据库对象
        rsp.total = goods.count()
        goods = goods.limit(pageSize).offset(start)
        # 把数据库对象转成返回商品列表的圣品信息,封装个函数convert_model_to_message
        for good in goods:
            rsp.data.append(self.convert_model_to_message(good))

        return rsp

    @logger.catch()
    def BatchGetGoods(self, request: BatchGoodsIdInfo, context):

        rsp = goods_pb2.GoodsListResponse()
        goods = Goods.select().where(Goods.id.in_(request.id))
        rsp = goods.count()
        for good in goods:
            rsp.data.append(self.convert_model_to_message(good))
        return rsp

    @logger.catch()
    def DeleteGoods(self, request: goods_pb2.DeleteGoodsInfo, context):

        # goods = Goods.delete().where(Goods.id==request.id)可能查不到
        try:
            goods = Goods.select().where(Goods.id == request.id)
            goods.delete_instance()
            return empty_pb2.Empty()  # 需不需要？

        except DoesNotExist as e:
            context.set_code(grpc.StatusCode.NOT_FOUND)
            context.set_details("记录不存在")
            return empty_pb2.Empty()
        except Exception as e:
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(str(e))
            return empty_pb2.Empty()

    @logger.catch()
    def CreateGoods(self, request: goods_pb2.CreateGoodsInfo, context):
        try:
            category = Category.get(Category.id == request.categoryId)
        except DoesNotExist as e:
            context.set_code(grpc.StatusCode.NOT_FOUND)
            context.set_details("商品分类不存在")
            return goods_pb2.GoodsInfoResponse()

        try:
            brand = Brands.get(Brands.id == request.brandId)
        except DoesNotExist as e:
            context.set_code(grpc.StatusCode.NOT_FOUND)
            context.set_details("品牌不存在")
            return goods_pb2.GoodsInfoResponse()

        goods = Goods()
        goods.brand = brand
        goods.category = category
        goods.name = request.name
        goods.goods_sn = request.goodsSn
        goods.market_price = request.marketPrice
        goods.shop_price = request.shopPrice
        goods.goods_brief = request.goodsBrief
        goods.ship_free = request.shipFree
        goods.images = list(request.images)
        goods.desc_images = list(request.descImages)
        goods.goods_front_image = request.goodsFrontImage
        goods.is_new = request.isNew
        goods.is_hot = request.isHot
        goods.on_sale = request.onSale

        goods.save()

        # TODO 此处完善库存的设置 - 分布式事务
        return self.convert_model_to_message(goods)

    @logger.catch()
    def UpdateGoods(self, request: goods_pb2.CreateGoodsInfo, context):
        try:
            category = Category.get(Category.id == request.categoryId)
        except DoesNotExist as e:
            context.set_code(grpc.StatusCode.NOT_FOUND)
            context.set_details("商品分类不存在")
            return goods_pb2.GoodsInfoResponse()

        try:
            brand = Brands.get(Brands.id == request.brandId)
        except DoesNotExist as e:
            context.set_code(grpc.StatusCode.NOT_FOUND)
            context.set_details("品牌不存在")
            return goods_pb2.GoodsInfoResponse()

        try:
            goods = Goods.select().where(Goods.id == request.id)
        except DoesNotExist as e:
            context.set_code(grpc.StatusCode.NOT_FOUND)
            context.set_details("商品不存在")
            return goods_pb2.GoodsInfoResponse()

        goods = Goods()
        goods.brand = brand
        goods.category = category
        goods.name = request.name
        goods.goods_sn = request.goodsSn
        goods.market_price = request.marketPrice
        goods.shop_price = request.shopPrice
        goods.goods_brief = request.goodsBrief
        goods.ship_free = request.shipFree
        goods.images = list(request.images)
        goods.desc_images = list(request.descImages)
        goods.goods_front_image = request.goodsFrontImage
        goods.is_new = request.isNew
        goods.is_hot = request.isHot
        goods.on_sale = request.onSale

        goods.save()

        # TODO 此处完善库存的设置 - 分布式事务
        return self.convert_model_to_message(goods)

    @logger.catch()
    def GetGoodsDetail(self, request: goods_pb2.GoodInfoRequest, context):
        try:
            goods = Goods.select().where(Goods.id == request.id)

            goods.click_num += 1  # 浏览量+1
            goods.save()

            return self.convert_model_to_message(goods)

        except DoesNotExist as e:
            context.set_code(grpc.StatusCode.NOT_FOUND)
            context.set_details("记录不存在")
            return goods_pb2.GoodsInfoResponse

    def category_nodel_to_dict(self, category):
        ca = {}
        ca['id'] = category.id
        ca['name'] = category.name
        ca['level'] = category.level
        ca['parent'] = category.parent_category
        ca['is_tab'] = category.is_tab

        return ca

    @logger.catch()
    def GetAllCategorysList(self, context):
        # 品牌分类
        level1 = []
        level2 = []
        level3 = []
        category_list_rsp = goods_pb2.CategoryListResponse()
        category_list_rsp.total = Category.select().count()

        for category in Category.select():
            category_rsp = goods_pb2.CategoryInfoResponse()
            category_rsp.id = category.id
            category_rsp.name = category.name
            category_rsp.parentCategory = category.parent_category
            category_rsp.level = category.level
            category_rsp.isTab = category.is_tab

            category_list_rsp.data.append(category_rsp)

            if category.level == 1:
                level1.append(self.category_nodel_to_dict(category))
            elif category.level == 2:
                level2.append(self.category_nodel_to_dict(category))
            elif category.level == 3:
                level3.append(self.category_nodel_to_dict(category))

            # 倒序整理:分类列表
            for data3 in level3:
                for data2 in level2:
                    if data3['parent'] == data2['id']:
                        if "sub_category" not in data2:
                            data2['sub_category'] = data3  # 第一个子分类
                        else:
                            data2['sub_category'].append(data3)  # 增加子分类

            for data2 in level2:
                for data1 in level1:
                    if "sub_category" not in data1:
                        data1['sub_category'] = data2  # 第一个子分类
                    else:
                        data1['sub_category'].append(data2)  # 增加子分类

    @logger.catch()
    def GetSubCategory(self, req: goods_pb2.CategoryListRequest, context):
        # 一级要查
        category_list_rsp = goods_pb2.SubCategoryListResponse()

        try:
            category_info = Category.get(Category.id == req.id)
            category_list_rsp.info.id = category_info.id
            category_list_rsp.info.name = category_info.name
            category_list_rsp.info.level = category_info.level
            category_list_rsp.info.isTab = category_info.is_tab
            if category_info.parent_category:
                category_list_rsp.info.parentCategory = category_info.parent_category_id
        except DoesNotExist:
            context.set_code(grpc.StatusCode.NOT_FOUND)
            context.set_details("记录不存在")
            return goods_pb2.SubCategoryListResponse()

        categorys = Category.select().where(Category.parent_category == req.id)

        category_list_rsp.total = categorys.count()
        for category in categorys:
            category_rsp = goods_pb2.CategoryInfoRespons()
            category_rsp.id = category.id
            category_rsp.name = category.name
            if category_info.parent_category:
                category_rsp.parentCategory = category_info.parent_category_id
            category_rsp.level = category.level
            category_rsp.isTab = category.is_tab

            category_list_rsp.sunCategory.append(category_rsp)

        return category_list_rsp

    @logger.catch()
    def CreateCategory(self, request: goods_pb2.CategoryInfoRequest, context):
        try:
            category = Category()
            category.name = request.name
            if request.level != 1:
                category.parent_category = request.parentCategory
            category.level = request.level
            category.is_tab = request.isTab
            category.save()

            category_rsp = goods_pb2.CategoryInfoResponse()
            category_rsp.id = category.id
            category_rsp.name = category.name
            if category.parent_category:
                category_rsp.parentCategory = category.parent_category.id
            category_rsp.level = category.level
            category_rsp.isTab = category.is_tab

        except Exception as e:
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details("插入数据失败" + str(e))
            return goods_pb2.CategoryInfoResponse()

        return category_rsp

    @logger.catch()
    def DeleteCategory(self, request: goods_pb2.DeleteCategoryRequest, context):
        try:
            category = Category.get(request.id)
            category.delete_instance()

            # todo 删除相应的category下的商品
            return empty_pb2.Empty()

        except DoesNotExist:
            context.set_code(grpc.StatusCode.NOT_FOUND)
            context.set_details('记录不存在')
            return empty_pb2.Empty()

    @logger.catch
    def UpdateCategory(self, request: goods_pb2.CategoryInfoRequest, context):
        try:
            category = Category.get(request.id)
            if request.name:
                category.name = request.name
            if request.parentCategory:
                category.parent_category = request.parentCategory
            if request.level:
                category.level = request.level
            if request.isTab:
                category.is_tab = request.isTab
            category.save()

            return empty_pb2.Empty()
        except DoesNotExist:
            context.set_code(grpc.StatusCode.NOT_FOUND)
            context.set_details('记录不存在')
            return empty_pb2.Empty()

    ##轮播图
    @logger.catch
    def BannerList(self, request: empty_pb2.Empty, context):
        # 获取分类列表
        rsp = goods_pb2.BannerListResponse()
        banners = Banner.select()

        rsp.total = banners.count()
        for banner in banners:
            banner_rsp = goods_pb2.BannerResponse()

            banner_rsp.id = banner.id
            banner_rsp.image = banner.image
            banner_rsp.index = banner.index
            banner_rsp.url = banner.url

            rsp.data.append(banner_rsp)

        return rsp

    @logger.catch
    def CreateBanner(self, request: goods_pb2.BannerRequest, context):
        banner = Banner()

        banner.image = request.image
        banner.index = request.index
        banner.url = request.url
        banner.save()

        banner_rsp = goods_pb2.BannerResponse()
        banner_rsp.id = banner.id
        banner_rsp.image = banner.image
        banner_rsp.url = banner.url

        return banner_rsp

    @logger.catch
    def DeleteBanner(self, request: goods_pb2.BannerRequest, context):
        try:
            banner = Banner.get(request.id)
            banner.delete_instance()

            return empty_pb2.Empty()
        except DoesNotExist:
            context.set_code(grpc.StatusCode.NOT_FOUND)
            context.set_details('记录不存在')
            return empty_pb2.Empty()

    @logger.catch
    def UpdateBanner(self, request: goods_pb2.BannerRequest, context):
        try:
            banner = Banner.get(request.id)
            if request.image:
                banner.image = request.image
            if request.index:
                banner.index = request.index
            if request.url:
                banner.url = request.url

            banner.save()

            return empty_pb2.Empty()
        except DoesNotExist:
            context.set_code(grpc.StatusCode.NOT_FOUND)
            context.set_details('记录不存在')
            return empty_pb2.Empty()

    # 品牌相关的接口

    @logger.catch
    def BrandList(self, request: empty_pb2.Empty, context):
        # 获取品牌列表
        rsp = goods_pb2.BrandListResponse()
        brands = Brands.select()

        rsp.total = brands.count()
        for brand in brands:
            brand_rsp = goods_pb2.BrandInfoResponse()

            brand_rsp.id = brand.id
            brand_rsp.name = brand.name
            brand_rsp.logo = brand.logo

            rsp.data.append(brand_rsp)

        return rsp

    @logger.catch
    def CreateBrand(self, request: goods_pb2.BrandRequest, context):
        brands = Brands.select().where(Brands.name == request.name)
        if brands:
            context.set_code(grpc.StatusCode.ALREADY_EXISTS)
            context.set_details('记录已经存在')
            return goods_pb2.BrandInfoResponse()

        brand = Brands()

        brand.name = request.name
        brand.logo = request.logo

        brand.save()

        rsp = goods_pb2.BrandInfoResponse()
        rsp.id = brand.id
        rsp.name = brand.name
        rsp.logo = brand.logo

        return rsp

    @logger.catch
    def DeleteBrand(self, request: goods_pb2.BrandRequest, context):
        try:
            brand = Brands.get(request.id)
            brand.delete_instance()

            return empty_pb2.Empty()
        except DoesNotExist:
            context.set_code(grpc.StatusCode.NOT_FOUND)
            context.set_details('记录不存在')
            return empty_pb2.Empty()

    @logger.catch
    def UpdateBrand(self, request: goods_pb2.BrandRequest, context):
        try:
            brand = Brands.get(request.id)
            if request.name:
                brand.name = request.name
            if request.logo:
                brand.logo = request.logo

            brand.save()

            return empty_pb2.Empty()
        except DoesNotExist:
            context.set_code(grpc.StatusCode.NOT_FOUND)
            context.set_details('记录不存在')
            return empty_pb2.Empty()

    @logger.catch
    def CategoryBrandList(self, request: empty_pb2.Empty, context):
        # 获取品牌分类列表
        rsp = goods_pb2.CategoryBrandListResponse()
        category_brands = GoodsCategoryBrand.select()

        # 分页
        start = 0
        per_page_nums = 10
        if request.pagePerNums:
            per_page_nums = request.PagePerNums
        if request.pages:
            start = per_page_nums * (request.pages - 1)

        category_brands = category_brands.limit(per_page_nums).offset(start)

        rsp.total = category_brands.count()
        for category_brand in category_brands:
            category_brand_rsp = goods_pb2.CategoryBrandResponse()

            category_brand_rsp.id = category_brand.id
            category_brand_rsp.brand.id = category_brand.brand.id
            category_brand_rsp.brand.name = category_brand.brand.name
            category_brand_rsp.brand.logo = category_brand.brand.logo

            category_brand_rsp.category.id = category_brand.category.id
            category_brand_rsp.category.name = category_brand.category.name
            category_brand_rsp.category.parentCategory = category_brand.category.parent_category_id
            category_brand_rsp.category.level = category_brand.category.level
            category_brand_rsp.category.isTab = category_brand.category.is_tab

            rsp.data.append(category_brand_rsp)
        return rsp

    @logger.catch
    def GetCategoryBrandList(self, request, context):
        # 获取某一个分类的所有品牌
        rsp = goods_pb2.BrandListResponse()
        try:
            category = Category.get(Category.id == request.id)
            category_brands = GoodsCategoryBrand.select().where(GoodsCategoryBrand.category == category)
            rsp.total = category_brands.count()
            for category_brand in category_brands:
                brand_rsp = goods_pb2.BrandInfoResponse()
                brand_rsp.id = category_brand.brand.id
                brand_rsp.name = category_brand.brand.name
                brand_rsp.logo = category_brand.brand.logo

                rsp.data.append(brand_rsp)
        except DoesNotExist as e:
            context.set_code(grpc.StatusCode.NOT_FOUND)
            context.set_details('记录不存在')
            return rsp

        return rsp

    @logger.catch
    def CreateCategoryBrand(self, request: goods_pb2.CategoryBrandRequest, context):
        category_brand = GoodsCategoryBrand()

        try:
            brand = Brands.get(request.brandId)
            category_brand.brand = brand
            category = Category.get(request.categoryId)
            category_brand.category = category
            category_brand.save()

            rsp = goods_pb2.CategoryBrandResponse()
            rsp.id = category_brand.id  # 是另外一种思路

            return rsp
        except DoesNotExist:
            context.set_code(grpc.StatusCode.NOT_FOUND)
            context.set_details('记录不存在')
            return goods_pb2.CategoryBrandResponse()
        except Exception as e:
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details('内部错误')
            return goods_pb2.CategoryBrandResponse()

    @logger.catch
    def DeleteCategoryBrand(self, request: goods_pb2.CategoryBrandRequest, context):
        try:
            category_brand = GoodsCategoryBrand.get(request.id)
            category_brand.delete_instance()

            return empty_pb2.Empty()
        except DoesNotExist:
            context.set_code(grpc.StatusCode.NOT_FOUND)
            context.set_details('记录不存在')
            return empty_pb2.Empty()

    @logger.catch
    def UpdateCategoryBrand(self, request: goods_pb2.CategoryBrandRequest, context):
        try:
            category_brand = GoodsCategoryBrand.get(request.id)
            brand = Brands.get(request.brandId)
            category_brand.brand = brand
            category = Category.get(request.categoryId)
            category_brand.category = category
            category_brand.save()

            return empty_pb2.Empty()
        except DoesNotExist:
            context.set_code(grpc.StatusCode.NOT_FOUND)
            context.set_details('记录不存在')
            return empty_pb2.Empty()
        except Exception as e:
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details('内部错误')
            return empty_pb2.Empty()
