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

from django.urls import re_path
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi

from backend_drf.views import *

schema_view = get_schema_view(
   openapi.Info(
      title="Snippets API",
      default_version='v1',
      description="Test description",
      terms_of_service="https://www.google.com/policies/terms/",
      contact=openapi.Contact(email="contact@snippets.local"),
      license=openapi.License(name="BSD License"),
   ),
   public=True,
   permission_classes=(permissions.AllowAny,),
)

# Статьи
router = routers.DefaultRouter()
router.register(r'articles', ArticleViewSet, basename='article')

urlpatterns = [
    # Документация
    path('swagger<format>/', schema_view.without_ui(cache_timeout=0), name='schema-json'),
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),

    # Для администратора
    path('admin/', admin.site.urls),

    # Авторизация
    path('api/login/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/login/token-refresh/', TokenRefreshView.as_view(), name='token_refresh'),

    # Профиль
    path('api/me/profile/', getProfile, name='profile'),

    # Роутинг статей и статьи
    path('api/', include(router.urls)),
    path('api/archive-articles/', ArchiveArticlesView.as_view(), name='archive-articles'),
    path('api/past-articles/<int:version_id>/', VersionDocumentsArticlesView.as_view(), name='version-documents-articles'),
    path('api/restore-article/<int:pk>/', RestoreArticleAPIView.as_view(), name='restore-article'),

    # Папки
    path('api/folders/', FolderView.as_view(), name='folder-list'),
    path('api/folders/<int:id_folder>/', FolderView.as_view(), name='folder-detail'),

    # Формулы
    path('api/formula/', FormulaView.as_view(), name='formula-list'),
    path('api/formula/<int:id_formula>/', FormulaView.as_view(), name='formula-detail'),

    # Поиск по статьям
    path('api/search/<str:title>/', search_articles, name='search_articles'),

    # Информация по сотрудникам
    path('api/employee-profiles/', ProfileAPIView.as_view(), name='profile-list'),
]
