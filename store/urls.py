from django.urls import path
from . import views
from .views import product_detail

urlpatterns = [
    path('', views.home, name='home'),
    path('home/', views.home, name='home'),
    path('store/', views.store, name='store'),
    path('cart/', views.cart, name='cart'),
    path('product_detail/<int:id>', views.product_detail, name='product_detail'),
    path('checkout/', views.checkout, name='checkout'),
    path('enquiry/', views.enquiry, name='enquiry'),
    path('update_item/', views.updateItem, name='update_item'),
    path('process_order/', views.processOrder, name='process_order'),
    path('register/', views.register_request, name='register'),
    path('login/', views.login_request, name='login'),
    path('logout/', views.logout_request, name= 'logout'),
    
]