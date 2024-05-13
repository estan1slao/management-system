"""
URL configuration for management_system project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from rest_framework import routers
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from django.urls import path, include

from backend_drf.views import *

# Статьи
router = routers.DefaultRouter()
router.register(r'articles', ArticleViewSet, basename='article')

urlpatterns = [
    # Для администратора
    path('admin/', admin.site.urls),

    # Авторизация
    path('api/login/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/login/token-refresh/', TokenRefreshView.as_view(), name='token_refresh'),

    # Роутинг статей
    path('api/', include(router.urls)),

    # Папки
    path('api/folders/', FolderView.as_view(), name='folder-list'),
    path('api/folders/<int:id_folder>/', FolderView.as_view(), name='folder-detail'),
]
