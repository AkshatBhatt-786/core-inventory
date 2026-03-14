from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from .models import StockLedger


@login_required
def history(request):
    entries = StockLedger.objects.select_related(
        'product', 'performed_by',
        'from_location', 'to_location'
    ).all()

    # Search
    q = request.GET.get('q')
    if q:
        entries = entries.filter(
            Q(reference__icontains=q) |
            Q(contact__icontains=q)   |
            Q(product__name__icontains=q)
        )

    # Filter by move type
    move_type = request.GET.get('move_type')
    if move_type:
        entries = entries.filter(move_type=move_type)

    return render(request, 'ledger/history.html', {
        'entries': entries
    })