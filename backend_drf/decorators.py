from functools import wraps
from django.http import HttpResponseForbidden
from django.shortcuts import get_object_or_404
from .models import *


def access_control(view_func):
    @wraps(view_func)
    def wrapper(self, request, *args, **kwargs):
        user = request.user
        if user.is_authenticated:
            article = get_object_or_404(Article, pk=kwargs['pk'])
            article_author = article.authorID
            if user == article_author:
                return view_func(self, request, *args, **kwargs)

            user_role = user.role
            article_access = article.access

            if user_role in article_access:
                return view_func(self, request, *args, **kwargs)

        return HttpResponseForbidden("У вас нет доступа к этой статье.")
    return wrapper