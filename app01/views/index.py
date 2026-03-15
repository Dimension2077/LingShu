from django.shortcuts import render, redirect


def entrance(request):
    """项目入口/欢迎页"""
    return redirect('/index/')


def index(request):
    """首页"""
    return render(request, 'app01/index.html')
