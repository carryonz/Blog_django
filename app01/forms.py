from .models import UserInfo, Article, Profile
from django import forms
from django.core.exceptions import ValidationError


class RegForm(forms.ModelForm):
    password = forms.CharField()
    re_password = forms.CharField()

    class Meta:
        model = UserInfo
        fields = ('username', 'email', 'phone')

    # 重写username字段的局部钩子
    def clean_username(self):
        username = self.cleaned_data.get("username")
        is_exist = UserInfo.objects.filter(username=username)
        if is_exist:
            # 表示用户名已注册
            self.add_error("username", ValidationError("用户名已存在"))
        else:
            return username

    # 重写email字段的局部钩子
    def clean_email(self):
        email = self.cleaned_data.get("email")
        is_exist = UserInfo.objects.filter(email=email)
        if is_exist:
            # 表示邮箱已注册
            self.add_error("email", ValidationError("邮箱已被注册"))
        else:
            return email

    # 重写全局的钩子函数，对确认密码做校验
    def clean(self):
        password = self.cleaned_data.get("password")
        re_password = self.cleaned_data.get("re_password")

        if re_password and re_password != password:
            self.add_error("re_password", ValidationError("两次密码不一致"))

        else:
            return self.cleaned_data


# 写文章的表单类
class ArticlePostForm(forms.ModelForm):
    class Meta:
        # 指明数据模型来源
        model = Article
        # 定义表单包含的字段
        fields = ('title', 'body','tags','avatar')


class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ('avatar', 'bio')