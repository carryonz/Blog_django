from django.contrib import admin
from .models import UserInfo, Article, Profile, ArticleColumn
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
# Register your models here.


# 定义一个行内 admin
class ProfileInline(admin.StackedInline):
    model = Profile
    can_delete = False
    verbose_name_plural = 'UserProfile'


# 将 Profile 关联到 User 中
class UserAdmin(BaseUserAdmin):
    inlines = (ProfileInline,)


# admin.site.unregister(UserInfo)
admin.site.register(UserInfo, UserAdmin)
admin.site.register(Article)

# 注册文章栏目
admin.site.register(ArticleColumn)
