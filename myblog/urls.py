"""
URL configuration for myblog project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.0/topics/http/urls/
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
from django.urls import path
from blog import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path("",views.index_view),
    path('article/<slug:slug>/', views.article_detail, name='article_detail'),
    path('archive/', views.archive_view, name='archive'),
    path('tags/',views.tags_view,name='tags'),
    path('tag/<slug:slug>/',views.tag_detail_view, name='tag_detail'),
    path('about/',views.about_view),
    path("404",views.fault_view),
]

handler404 = views.fault_view
