from django.urls import path
from django.contrib import admin
from . import views
from .views import cart_view
urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.home),
    path('cart/', cart_view, name='cart')
    
]
