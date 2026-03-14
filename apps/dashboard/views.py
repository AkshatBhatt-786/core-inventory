from django.shortcuts import render
from django.db import models
from django.contrib.auth.decorators import login_required
from apps.products.models import Product
from apps.operations.models import Receipt, Delivery

@login_required
def index(request):
    # KPI queries
    total_products    = Product.objects.filter(is_active=True).count()
    low_stock_items   = Product.objects.filter(
                            is_active=True,
                            current_stock__lte=models.F('reorder_level'),
                            current_stock__gt=0
                        ).count()
    out_of_stock      = Product.objects.filter(
                            is_active=True,
                            current_stock__lte=0
                        ).count()
    pending_receipts  = Receipt.objects.filter(
                            status__in=['draft', 'ready']
                        ).count()
    pending_deliveries = Delivery.objects.filter(
                            status__in=['draft', 'waiting', 'ready']
                        ).count()

    # Recent operations for the table
    recent_receipts   = Receipt.objects.select_related(
                            'responsible'
                        ).order_by('-created_at')[:5]
    recent_deliveries = Delivery.objects.select_related(
                            'responsible'
                        ).order_by('-created_at')[:5]

    context = {
        'total_products':     total_products,
        'low_stock_items':    low_stock_items,
        'out_of_stock':       out_of_stock,
        'pending_receipts':   pending_receipts,
        'pending_deliveries': pending_deliveries,
        'recent_receipts':    recent_receipts,
        'recent_deliveries':  recent_deliveries,
        'low_stock_count':    low_stock_items,  # for navbar bell
    }
    return render(request, 'dashboard/index.html', context)