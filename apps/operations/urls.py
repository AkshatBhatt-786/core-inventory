from django.urls import path
from . import views

app_name = 'operations'

urlpatterns = [
    # Receipts
    path('receipts/',
         views.receipt_list,     name='receipt_list'),
    path('receipts/create/',
         views.receipt_create,   name='receipt_create'),
    path('receipts/<int:pk>/',
         views.receipt_detail,   name='receipt_detail'),
    path('receipts/<int:pk>/validate/',
         views.receipt_validate, name='receipt_validate'),
    path('receipts/<int:pk>/cancel/',
         views.receipt_cancel,   name='receipt_cancel'),

    # Deliveries
    path('deliveries/',
         views.delivery_list,     name='delivery_list'),
    path('deliveries/create/',
         views.delivery_create,   name='delivery_create'),
    path('deliveries/<int:pk>/',
         views.delivery_detail,   name='delivery_detail'),
    path('deliveries/<int:pk>/validate/',
         views.delivery_validate, name='delivery_validate'),
    path('deliveries/<int:pk>/cancel/',
         views.delivery_cancel,   name='delivery_cancel'),

    # Adjustments
    path('adjustments/',
         views.adjustment_list,   name='adjustment_list'),
    path('adjustments/create/',
         views.adjustment_create, name='adjustment_create'),
]