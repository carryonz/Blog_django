from ckeditor.fields import RichTextField
from django.db import models
from django.contrib.auth.models import User
from app01.models import Article, UserInfo
# Create your models here.


# 博文的评论
class Comment(models.Model):
    article = models.ForeignKey(
        Article,
        on_delete=models.CASCADE,
        related_name='comments'
    )
    user = models.ForeignKey(
        UserInfo,
        on_delete=models.CASCADE,
        related_name='comments'
    )
    body = RichTextField()
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ('created',)

    def __str__(self):
        return self.body[:20]