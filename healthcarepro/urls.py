from django.urls import path
from django.contrib import admin
from healthcarepro import views

urlpatterns = [ 
    path('admin/', admin.site.urls),
    path('api/auth/register', views.register),
    path('api/auth/login', views.login),
    path('api/auth/me', views.get_current_user),
    path('', views.index),
]
