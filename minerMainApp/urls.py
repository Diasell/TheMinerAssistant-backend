"""minerMainApp URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.0/topics/http/urls/
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
from django.conf.urls import url
from django.contrib import admin
from django.conf import settings
from django.conf.urls.static import static

from mainApp.api.v1.auth import (
    RegisterAPIView,
    AddChatIdView,
    LoginAPIView,
    OnLoginView
)

from mainApp.api.v1.nanopool import (
    GetPools,
    SavePoolStats,
)


urlpatterns = [
    url(r'^api/v1/admin/', admin.site.urls),
    url(r'^api/v1/register/$', RegisterAPIView.as_view()),
    url(r'^api/v1/add_chat_id/$', AddChatIdView.as_view()),
    url(r'^api/v1/login/$', LoginAPIView.as_view()),
    url(r'^api/v1/onlogin/$', OnLoginView.as_view()),

    url(r'^nanopool/get_pools/$', GetPools.as_view()),
    url(r'^nanopool/save_pool_stats/$', SavePoolStats.as_view())
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)