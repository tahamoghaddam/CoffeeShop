from django.urls import path
from django.contrib import admin
from . import views
from .views import signup,login, add_product , shoppingcart , inventory_list , update_inventory


urlpatterns = [
    path('admin/', admin.site.urls),
    path('login/',login , name = 'login'),
    path('signup/' ,signup , name = 'signup'),
    path('shoppingcart/', shoppingcart, name ='shoppingcart'),
    path('addproduct/' ,add_product , name = 'addproduct' ),
    path('inventory/' , inventory_list , name = 'inventory'),
    path('update_invnetory/' , update_inventory, name = 'inventory_update'),
]
