from apps.operations.models import Receipt, Delivery
from apps.products.models import Product
from django.db.models import F


def sidebar_counts(request):
    if not request.user.is_authenticated:
        return {}
    return {
        'pending_receipts': Receipt.objects.filter(
            status__in=['draft', 'ready']
        ).count(),
        'pending_deliveries': Delivery.objects.filter(
            status__in=['draft', 'waiting', 'ready']
        ).count(),
        'low_stock_count': Product.objects.filter(
            is_active=True,
            current_stock__lte=F('reorder_level'),
            current_stock__gt=0
        ).count(),
    }