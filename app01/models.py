from PIL import Image
from django.urls import reverse
from django.utils import timezone
from django.db import models
from django.contrib.auth.models import User, AbstractUser
# Create your models here.
from taggit.managers import TaggableManager


class UserInfo(AbstractUser):
    phone = models.CharField(max_length=11)
    addr = models.CharField(max_length=128)


class ArticleColumn(models.Model):
    # 栏目标题
    title = models.CharField(max_length=100, blank=True)
    # 创建时间
    created = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return self.title


class Article(models.Model):
    author = models.ForeignKey(UserInfo, on_delete=models.CASCADE)
    title = models.CharField(max_length=100)
    # 文章标签
    tags = TaggableManager(blank=True)
    avatar = models.ImageField(upload_to='article/%Y%m%d/', blank=True)
    body = models.TextField()
    total_views = models.PositiveIntegerField(default=0)
    created = models.DateTimeField(default=timezone.now)
    updated = models.DateTimeField(auto_now=True)
    # 文章栏目的 “一对多” 外键
    column = models.ForeignKey(
        ArticleColumn,
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        related_name='article'
    )

    class Meta:
        ordering = ('-created',)

    def save(self, *args, **kwargs):
        # 调用原有的 save() 的功能
        article = super(Article, self).save(*args, **kwargs)

        # 固定宽度缩放图片大小
        if self.avatar and not kwargs.get('update_fields'):
            image = Image.open(self.avatar)
            (x, y) = image.size
            new_x = 400
            new_y = int(new_x * (y / x))
            resized_image = image.resize((new_x, new_y), Image.ANTIALIAS)
            resized_image.save(self.avatar.path)
        return article

    def __str__(self):
        return self.title

        # 获取文章地址
    def get_absolute_url(self):
        return reverse('article_detail', args=[self.id])


# 用户扩展信息
class Profile(models.Model):
    # 与 User 模型构成一对一的关系
    user = models.OneToOneField(UserInfo, on_delete=models.CASCADE, related_name='profile')
    # 头像
    avatar = models.ImageField(upload_to='avatar/%Y%m%d/', blank=True)
    # 个人简介
    bio = models.TextField(max_length=500, blank=True)

    def __str__(self):
        return 'user {}'.format(self.user.username)

