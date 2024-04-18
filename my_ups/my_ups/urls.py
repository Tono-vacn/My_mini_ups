from django.conf.urls import include
from django.contrib import admin
from django.urls import path,include
from myups import views
urlpatterns = [
    path('admin/', admin.site.urls),
    # path('login_user/', v.login_user, name = 'login_user'),
    path('',include('myups.urls')),
    path('index/',views.show_index_page,name='index'),
    # path('edit_dest/',views.edit_dest,name='edit_dest')
    
]