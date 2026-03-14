from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.db.models import F, Sum, ExpressionWrapper, DecimalField
from django.utils import timezone
from apps.products.models import Product
from apps.operations.models import Receipt, Delivery
from apps.ledger.models import StockLedger


@login_required
def index(request):
    today = timezone.now().date()

    total_products     = Product.objects.filter(is_active=True).count()
    low_stock_items    = Product.objects.filter(
                             is_active=True,
                             current_stock__lte=F('reorder_level'),
                             current_stock__gt=0
                         ).count()
    out_of_stock       = Product.objects.filter(
                             is_active=True,
                             current_stock__lte=0
                         ).count()

    # Inventory value = sum of (cost_price * current_stock)
    stock_value = Product.objects.filter(
        is_active=True
    ).aggregate(
        total=Sum(
            ExpressionWrapper(
                F('cost_price') * F('current_stock'),
                output_field=DecimalField()
            )
        )
    )['total'] or 0

    total_receipts     = Receipt.objects.count()
    completed_receipts = Receipt.objects.filter(status='done').count()
    pending_receipts   = Receipt.objects.filter(
                             status__in=['draft', 'ready']
                         ).count()

    total_deliveries     = Delivery.objects.count()
    completed_deliveries = Delivery.objects.filter(status='done').count()
    pending_deliveries   = Delivery.objects.filter(
                               status__in=['draft', 'waiting', 'ready']
                           ).count()

    today_movements    = StockLedger.objects.filter(
                             created_at__date=today
                         ).count()

    recent_receipts    = Receipt.objects.select_related(
                             'responsible'
                         ).order_by('-created_at')[:5]

    recent_deliveries  = Delivery.objects.select_related(
                             'responsible'
                         ).order_by('-created_at')[:5]

    # Low stock products for alert table
    low_stock_products = Product.objects.filter(
        is_active=True,
        current_stock__lte=F('reorder_level')
    ).select_related('category', 'warehouse').order_by('current_stock')[:5]

    context = {
        'total_products':     total_products,
        'low_stock_items':    low_stock_items,
        'out_of_stock':       out_of_stock,
        'stock_value':        stock_value,
        'total_receipts':     total_receipts,
        'completed_receipts': completed_receipts,
        'pending_receipts':   pending_receipts,
        'total_deliveries':     total_deliveries,
        'completed_deliveries': completed_deliveries,
        'pending_deliveries':   pending_deliveries,
        'today_movements':    today_movements,
        'recent_receipts':    recent_receipts,
        'recent_deliveries':  recent_deliveries,
        'low_stock_products': low_stock_products,
        'low_stock_count':    low_stock_items,
    }
    return render(request, 'dashboard/index.html', context)