from django.urls import path
from django.contrib import admin
from . import views
from .views import signup,login, add_product , shoppingcart , inventory_list , update_inventory,


urlpatterns = [
    path('admin/', admin.site.urls),
    path('home/',home_view, name = 'home'),
    path('menu/',menu_view , name = 'menu'),
    path('login/',login , name = 'login'),
    path('signup/' , signup , name = 'signup'),
    path('shoppingcart/', shoppingcart, name ='shoppingcart'),
    path('finalorder/' , finalorder_view , name = 'finalorder'),
    path('shoppinghistory/', shoppinghistory_view , name = 'shoppinghistory'),
    path('addproduct/' ,add_product , name = 'addproduct' ),
    path('inventory/' , inventory_list , name = 'inventory'),
    path('update_invnetory/' , update_inventory, name = 'inventory_update'),
    path('report/' , report_view , name = 'report')

    
]
