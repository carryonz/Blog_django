import random
import re

import markdown
import requests
from django.contrib.auth.hashers import check_password, make_password
from django.core.paginator import Paginator
from django.db.models import Q
from django.http import JsonResponse
from django.shortcuts import render, redirect, HttpResponse, reverse
from django.views import View
from geetest import GeetestLib

from app01.forms import ArticlePostForm, ProfileForm
from app01.send_message import send
# Create your views here.
from app01.scrapy_library import scrapy_library, get_back_table,get_borrow_table
from django.contrib import auth
from django.contrib.auth.decorators import login_required
from app01 import forms, models
from app01.models import UserInfo, Article, Profile, ArticleColumn
from comment.forms import CommentForm
from comment.models import Comment


def login(request):
    if request.method == "POST":
        ret = {"status": 0, "msg": ""}
        username = request.POST.get("username")
        pwd = request.POST.get("password")
        # 获取极验 滑动验证码相关的参数
        gt = GeetestLib(pc_geetest_id, pc_geetest_key)
        challenge = request.POST.get(gt.FN_CHALLENGE, '')
        validate = request.POST.get(gt.FN_VALIDATE, '')
        seccode = request.POST.get(gt.FN_SECCODE, '')
        status = request.session[gt.GT_STATUS_SESSION_KEY]
        user_id = request.session["user_id"]
        if status:
            result = gt.success_validate(challenge, validate, seccode, user_id)
        else:
            result = gt.failback_validate(challenge, validate, seccode)
        if result:
            print("XXX")
            # 验证码正确
            # 利用auth模块做用户名和密码的校验
            user = auth.authenticate(username=username, password=pwd)
            if user:
                # 用户名密码正确
                # 给用户做登录
                print('1111')
                auth.login(request, user)  # 将登录用户赋值给 request.user
                ret["msg"] = "/"
            else:
                ret["status"] = 1
                ret["msg"] = "用户名或密码错误！"
        else:
            ret["status"] = 2
            ret["msg"] = "验证码错误"
        return JsonResponse(ret)
    return render(request, "login.html")


@login_required
def index(request):
    print(request.user.username)
    print("=" * 120)
    ret = request.user.is_authenticated
    print(ret)
    return render(request, "index.html")


def logout(request):
    auth.logout(request)
    return redirect("/login/")


def send_msg(request):
    mobile = request.POST.get('mobile')
    user = UserInfo.objects.filter(phone=mobile)
    if len(user) == 1:
        msg = '手机号已注册！'
        return HttpResponse(msg)
    if mobile:
        # 验证是否为有效手机号
        mobile_pat = re.compile('^(13\d|14[5|7]|15\d|166|17\d|18\d)\d{8}$')
        res = re.search(mobile_pat, mobile)
        if res:
            # 生成手机验证码
            c = random.randint(1000, 9999)
            print(c)
            sms_status = send(mobile=mobile, captcha=c)
            # sms_status = True
            if sms_status:
                msg = '发送成功'
                request.session['send_msg'] = c
            else:
                msg = '发送失败'
            return HttpResponse(msg)
        else:
            msg = '请输入有效手机号码!'
            return HttpResponse(msg)
    else:
        msg = '手机号不能为空！'
        return HttpResponse(msg)


def register(request):
    if request.method == 'POST':
        ycode = request.POST.get('ycode')
        print(ycode,request.session['send_msg'])
        if int(request.session['send_msg']) != int(ycode):
            return HttpResponse('验证码错误！')
        # print("=" * 120)
        form_obj = forms.RegForm(request.POST)
        # print(form_obj)
        if form_obj.is_valid():
            new_user = form_obj.save(commit=False)
            print(new_user, form_obj)
            new_user.set_password(form_obj.cleaned_data['password'])
            new_user.save()
            return redirect(reverse('list'))
        else:
            return HttpResponse("注册表单输入有误。请重新输入~")
    return render(request, 'register.html')


def test(request):
    if request.method == 'POST':
        file_obj = request.FILES.get('files')
        # print(file_obj,type(file_obj))
        with open(file_obj.name, 'wb') as f:
            for line in file_obj.chunks():
                f.write(line)
        return HttpResponse("上传成功")

    return render(request, 'test.html')


# 请在官网申请ID使用，示例ID不可使用
pc_geetest_id = "b46d1900d0a894591916ea94ea91bd2c"
pc_geetest_key = "36fc3fe98530eea08dfc6ce76e3d24c4"


# 处理极验 获取验证码的视图
def get_geetest(request):
    user_id = 'test'
    gt = GeetestLib(pc_geetest_id, pc_geetest_key)
    status = gt.pre_process(user_id)
    request.session[gt.GT_STATUS_SESSION_KEY] = status
    request.session["user_id"] = user_id
    response_str = gt.get_response_str()
    return HttpResponse(response_str)


def list(request):
    search = request.GET.get('search')
    order = request.GET.get('order')
    column = request.GET.get('column')
    tag = request.GET.get('tag')
    article_list = Article.objects.all()# 初始化查询集
    if search:# 搜索查询集
        article_list = article_list.filter(
            Q(title__icontains=search) |
            Q(body__icontains=search)
        )
    else:
        search = ''
    if column is not None and column.isdigit():# 栏目查询集
        article_list = article_list.filter(column=column)
    if tag and tag != 'None':# 标签查询集
        article_list = article_list.filter(tags__name__in=[tag])
    if order == 'total_views':# 查询集排序
        article_list = article_list.order_by('-total_views')
    paginator = Paginator(article_list, 3)
    page = request.GET.get('page')
    articles = paginator.get_page(page)
    context = {
        'articles': articles,
        'order': order,
        'search': search,
        'column': column,
        'tag': tag,
    }
    return render(request, 'list.html', context)


def library(request):
    context = {
        'name': None,
        'borrow': None,
        'back': None,
    }
    if request.method == 'POST':
        user = request.POST.get('username')
        pw = request.POST.get('password')
        print(user, pw)
        ans = scrapy_library(user, pw)
        if ans[1]: #表示获取数据成功
            context['name'] = ans[3]
            borrow = get_borrow_table(user, pw)
            back = get_back_table(user, pw)
            context['borrow'] = borrow
            context['back'] = back
        return render(request, 'library/index.html', context=context)
    return render(request, 'library/index.html', context=context)


def lib_out(request):
    context = {
        'name': None,
        'borrow': None,
        'back': None,
    }
    # response = requests.get('http://tsgweb.jxust.edu.cn/share/Exit.asp')
    return render(request, 'library/index.html', context=context)


# 文章详情
def article_detail(request, id):
    # 取出相应的文章
    article = Article.objects.get(id=id)
    # 过滤出所有的id比当前文章小的文章
    pre_article = Article.objects.filter(id__lt=article.id).order_by('-id')
    # 过滤出id大的文章
    next_article = Article.objects.filter(id__gt=article.id).order_by('id')
    if pre_article.count() > 0: # 取出相邻前一篇文章
        pre_article = pre_article[0]
    else:
        pre_article = None
    if next_article.count() > 0: # 取出相邻后一篇文章
        next_article = next_article[0]
    else:
        next_article = None
    # 取出文章评论
    comments = Comment.objects.filter(article=id)
    # column = ArticleColumn.objects.get(article=id)
    # 浏览量 +1
    article.total_views += 1
    article.save(update_fields=['total_views'])
    # 将markdown语法渲染成html样式
    md = markdown.Markdown(article.body,
        extensions=[
            # 包含 缩写、表格等常用扩展
            'markdown.extensions.extra',
            # 语法高亮扩展
            'markdown.extensions.codehilite',
            # 目录扩展
            'markdown.extensions.toc',
       ])
    # 需要传递给模板的对象
    # 新增了md.toc对象
    article.body = md.convert(article.body)
    comment_form = CommentForm()
    context = {'article': article, 'toc': md.toc, 'comments': comments,'comment_form': comment_form,'pre_article': pre_article,
        'next_article': next_article}
    # 载入模板，并返回context对象
    return render(request, 'detail.html', context)

@login_required(login_url="login")
def article_create(request):
    # 判断用户是否提交数据
    if request.method == "POST":
        # 将提交的数据赋值到表单实例中
        article_post_form = ArticlePostForm(request.POST, request.FILES)
        # 判断提交的数据是否满足模型的要求
        if article_post_form.is_valid():
            # 保存数据，但暂时不提交到数据库中
            new_article = article_post_form.save(commit=False)
            new_article.author = UserInfo.objects.get(id=request.user.id)
            # 新增的代码
            if request.POST['column'] != 'none':
                new_article.column = ArticleColumn.objects.get(id=request.POST['column'])
            # 将新文章保存到数据库中
            new_article.save()
            article_post_form.save_m2m()
            # 完成后返回到文章列表
            return redirect("list")
        # 如果数据不合法，返回错误信息
        else:
            return HttpResponse("表单内容有误，请重新填写。")
    # 如果用户请求获取数据
    else:
        # 创建表单类实例
        article_post_form = ArticlePostForm()
        columns = ArticleColumn.objects.all()
        # 赋值上下文
        context = {'article_post_form': article_post_form,'columns': columns }
        # 返回模板
        return render(request, 'create.html', context)


# 删文章
@login_required(login_url="login")
def article_delete(request, id):
    # 根据 id 获取需要删除的文章
    article = Article.objects.get(id=id)
    if request.user != article.author:
        return HttpResponse("抱歉，你无权删除这篇文章。")
    # 调用.delete()方法删除文章
    article.delete()
    # 完成删除后返回文章列表
    return redirect("list")


# 更新文章
@login_required(login_url="login")
def article_update(request, id):
    # 获取需要修改的具体文章对象
    article = Article.objects.get(id=id)
    # 判断用户是否为 POST 提交表单数据
    if request.user != article.author:
        return HttpResponse("抱歉，你无权修改这篇文章。")
    if request.method == "POST":
        # 将提交的数据赋值到表单实例中
        old_tags = article.tags.all
        article_post_form = ArticlePostForm(data=request.POST)
        # 判断提交的数据是否满足模型的要求
        if article_post_form.is_valid():
            # 保存新写入的 title、body 数据并保存
            article.title = request.POST['title']
            article.body = request.POST['body']
            if request.FILES.get('avatar'):
                article.avatar = request.FILES.get('avatar')

            article.tags.set(*request.POST.get('tags').split(','), clear=True)
            article.save()
            if request.POST['column'] != 'none':
                article.column = ArticleColumn.objects.get(id=request.POST['column'])
            else:
                article.column = None
            article.save()
            # 完成后返回到修改后的文章中。需传入文章的 id 值
            return redirect("article_detail", id=id)
        # 如果数据不合法，返回错误信息
        else:
            return HttpResponse("表单内容有误，请重新填写。")

    # 如果用户 GET 请求获取数据
    else:
        # 创建表单类实例
        article_post_form = ArticlePostForm()
        columns = ArticleColumn.objects.all()
        context = {
            'article': article,
            'article_post_form': article_post_form,
            'columns': columns,
            'tags': ','.join([x for x in article.tags.names()]),
        }
        # 将响应返回到模板中
        return render(request, 'update.html', context)


# 编辑用户信息
@login_required(login_url='login')
def profile_edit(request,id):
    user = UserInfo.objects.get(id=id)
    if Profile.objects.filter(user_id=id).exists():
        # user_id 是 OneToOneField 自动生成的字段
        profile = Profile.objects.get(user_id=id)
    else:
        profile = Profile.objects.create(user=user)

    if request.method == 'POST':
        # 验证修改数据者，是否为用户本人
        if request.user != user:
            return HttpResponse("你没有权限修改此用户信息。")

        profile_form = ProfileForm(request.POST, request.FILES)
        if profile_form.is_valid():
            # 取得清洗后的合法数据
            profile_cd = profile_form.cleaned_data
            profile.bio = profile_cd['bio']
            # 如果 request.FILES 存在文件，则保存
            if 'avatar' in request.FILES:
                profile.avatar = profile_cd["avatar"]
            profile.save()
            # 带参数的 redirect()
            return redirect("edit", id=id)
        else:
            return HttpResponse("注册表单输入有误。请重新输入~")

    elif request.method == 'GET':
        profile_form = ProfileForm()
        context = {'profile_form': profile_form, 'profile': profile, 'user': user}
        return render(request, 'edit.html', context)
    else:
        return HttpResponse("请使用GET或POST请求数据")


class pwchange(View):
    def get(self, request):
        return render(request, 'pw_change.html')

    def post(self, request):
        opw = request.POST.get('opassword')
        pw = request.POST.get('password')
        newpw = request.POST.get('re_password')
        user = request.user
        if check_password(opw, user.password):
            if pw == newpw:
                user.password = make_password(pw)
                user.save()
                return redirect('list')
            return HttpResponse("两次密码不一致")
        return HttpResponse("旧密码不正确")