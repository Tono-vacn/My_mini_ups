"""
URL configuration for my_ups project.

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
from django.urls import path
from . import views
# from django.conf.urls import include,url 
urlpatterns = [
    # path('admin/', admin.site.urls),
    path('',views.show_index_page, name='index'),
    path('register/', views.user_register, name='user_register'),
    path('login/', views.user_login, name='user_login'),
    path('logout/', views.user_logout, name='user_logout'),
    path('pkg/', views.check_package, name='pkg'),
    path('pkg/<str:user_id>/', views.check_all_packages, name='pkg_all'),
    path('change_email/', views.change_email, name='change_email'),
    path('change_dest/<str:pkg_id>/', views.change_dest, name='change_dest'),
    path('save_new_dest', views.save_new_dest, name='save_new_dest'),
    path('load_pkg/', views.load_pkg, name='load_pkg'),
    path('pkup_pkg/', views.pkup_pkg, name='pkup_pkg'),
    path('delivered_pkg/', views.delivered_pkg, name='delivered_pkg'),
    path('deliver_pkg/', views.deliver_pkg, name='deliver_pkg'),
    # url(r'^$',views.index),
]
