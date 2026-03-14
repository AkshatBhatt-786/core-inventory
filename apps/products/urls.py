from django.urls import path
from . import views

app_name = 'products'

urlpatterns = [
    # products
    path('',                views.product_list,    name='list'),
    path('create/',         views.product_create,  name='create'),
    path('<int:pk>/',       views.product_detail,  name='detail'),
    path('<int:pk>/edit/',  views.product_edit,    name='edit'),

    # Warehouses
    path('warehouses/',         views.warehouse_list,   name='warehouse_list'),
    path('warehouses/create/',  views.warehouse_create, name='warehouse_create'),

    # Categories
    path('categories/',         views.category_list,   name='category_list'),
    path('categories/create/',  views.category_create, name='category_create'),
]