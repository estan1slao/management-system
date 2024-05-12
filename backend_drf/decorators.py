from functools import wraps
from django.http import HttpResponseForbidden


def access_control(view_func):
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        user = request.user
        if user.is_authenticated:
            article_author = view_func.__self__.get_object().authorID
            if user == article_author:
                return view_func(request, *args, **kwargs)

            user_role = user.role

            article_access = view_func.__self__.get_object().access

            if user_role in article_access:
                return view_func(request, *args, **kwargs)

        return HttpResponseForbidden("У вас нет доступа к этой статье.")
    return wrapper