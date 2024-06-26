from django.urls import path
from django.contrib import admin
from . import views
from .views import signup,login, add_product , update_inventory, home


urlpatterns = [
    path('admin/', admin.site.urls),
    path('login/',login , name = 'login'),
    path('signup/' ,signup , name = 'signup'),
    path('addproduct/' ,add_product , name = 'addproduct' ),
    path('update_invnetory/' , update_inventory, name = 'inventory_update'),
    path('home', home, name = 'home')
]
