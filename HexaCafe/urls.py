from django.urls import path
from django.contrib import admin
from . import views
from .views import signup,user_login, add_product, home, admin_view, inventory_view, add_ingredient, update_ingredient, ingredient_success,shopping_history,cart_detail


urlpatterns = [
    path('admin/', admin.site.urls),
    path('signup/', signup, name='signup'),
    path('login/', user_login, name='login'),
    path('addproduct/' ,add_product , name = 'addproduct' ),
    path('inventory/' ,inventory_view , name = 'inventory' ),
    #path('update_inventory/' , update_inventory, name = 'inventory_update'),
    path('home/', home, name='home'),
    path('shoppingcart/', cart_detail, name='shoppingcart'),
    #path('add_to_cart/', add_to_cart, name='add_to_cart'),
    path('admin_page/', admin_view, name='admin_page'),
    path('add_ingredient/', add_ingredient, name='add_ingredient'),
    path('update-ingredient/', update_ingredient, name='update_ingredient'),
    path('success/', ingredient_success, name='success'),
    path('shopping-history/',shopping_history , name = 'shopping-history'),
    path('inventory/', views.inventory_view, name='inventory_view'),
    path('add-ingredient/', views.add_ingredient, name='add_ingredient'),
    path('update-ingredient/<str:name>/', views.update_ingredient, name='update_ingredient'),
    path('success/', views.ingredient_success, name='success'),
    path('order-monitor/', views.order_monitor, name='order_monitor'),
    path('get-orders-data/', views.get_orders_data, name='get_orders_data'),
    path('product/', views.menu_view, name='product'),
]
