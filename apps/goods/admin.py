from django.contrib import admin
from goods.models import *
from django.core.cache import cache


class BaseModelAdmin(admin.ModelAdmin):
    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)
        # 发出任务，让celery worker重新生成首页静态页面
        from celery_tasks.tasks import generate_static_index_html
        generate_static_index_html.delay()

        # 清除缓存
        cache.delete('index_page_data')

    def delete_model(self, request, obj):
        """
        删除表中数据时调用
        :param request:
        :param obj:
        :return:
        """
        super().delete_model(request, obj)
        from celery_tasks.tasks import generate_static_index_html
        generate_static_index_html.delay()

        # 清除缓存
        cache.delete('index_page_data')


@admin.register(Goods)
class GoodsAdmin(BaseModelAdmin):
    pass


@admin.register(GoodsSKU)
class GoodsSKUAdmin(BaseModelAdmin):
    pass


@admin.register(GoodsType)
class GoodsTypeAdmin(BaseModelAdmin):
    pass


@admin.register(IndexPromotionBanner)
class IndexPromotionBannerAdmin(BaseModelAdmin):
    pass


@admin.register(IndexTypeGoodsBanner)
class IndexTypeGoodsBannerAdmin(BaseModelAdmin):
    pass


@admin.register(IndexGoodsBanner)
class IndexGoodsBannerAdmin(BaseModelAdmin):
    pass

# admin.site.register(GoodsType, GoodsTypeAdmin)
# admin.site.register(IndexTypeGoodsBanner, IndexTypeGoodsBannerAdmin)
# admin.site.register(IndexPromotionBanner, IndexPromotionBannerAdmin)
# admin.site.register(IndexGoodsBanner, IndexGoodsBannerAdmin)
