from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db import transaction
from .models import Receipt, ReceiptItem, Delivery, DeliveryItem, Adjustment
from apps.products.models import Product, Warehouse, Location
from apps.ledger.models import StockLedger


# ── RECEIPTS ──────────────────────────────────────────

@login_required
def receipt_list(request):
    receipts = Receipt.objects.select_related(
        'responsible', 'warehouse'
    ).all()
    status = request.GET.get('status')
    if status:
        receipts = receipts.filter(status=status)
    return render(request, 'operations/receipts/list.html', {
        'receipts': receipts
    })


@login_required
def receipt_create(request):
    products   = Product.objects.filter(is_active=True)
    warehouses = Warehouse.objects.all()
    if request.method == 'POST':
        supplier      = request.POST.get('supplier', '').strip()
        receive_from  = request.POST.get('receive_from', '').strip()
        warehouse_id  = request.POST.get('warehouse')
        schedule_date = request.POST.get('schedule_date')
        notes         = request.POST.get('notes', '').strip()

        product_ids   = request.POST.getlist('product_id')
        quantities    = request.POST.getlist('quantity')

        if not product_ids:
            messages.error(request, 'Add at least one product.')
            return render(request, 'operations/receipts/create.html', {
                'products': products,
                'warehouses': warehouses
            })

        with transaction.atomic():
            receipt = Receipt.objects.create(
                supplier=supplier,
                receive_from=receive_from,
                warehouse_id=warehouse_id if warehouse_id else None,
                schedule_date=schedule_date if schedule_date else None,
                notes=notes,
                responsible=request.user,
                status='draft',
            )
            for pid, qty in zip(product_ids, quantities):
                if pid and qty:
                    ReceiptItem.objects.create(
                        receipt=receipt,
                        product_id=int(pid),
                        quantity=int(qty)
                    )

        messages.success(
            request, f'Receipt {receipt.reference} created.'
        )
        return redirect('operations:receipt_detail', pk=receipt.pk)

    return render(request, 'operations/receipts/create.html', {
        'products': products,
        'warehouses': warehouses
    })


@login_required
def receipt_detail(request, pk):
    receipt = get_object_or_404(
        Receipt.objects.prefetch_related('items__product'), pk=pk
    )
    return render(request, 'operations/receipts/detail.html', {
        'receipt': receipt
    })


@login_required
def receipt_validate(request, pk):
    receipt = get_object_or_404(Receipt, pk=pk)
    if receipt.status == 'done':
        messages.warning(request, 'Already validated.')
        return redirect('operations:receipt_detail', pk=pk)
    if receipt.status == 'cancel':
        messages.error(request, 'Cannot validate a cancelled receipt.')
        return redirect('operations:receipt_detail', pk=pk)
    if not receipt.items.exists():
        messages.error(request, 'No products in this receipt.')
        return redirect('operations:receipt_detail', pk=pk)

    with transaction.atomic():
        for item in receipt.items.all():
            product      = item.product
            stock_before = product.current_stock
            product.current_stock += item.quantity
            product.save()
            StockLedger.objects.create(
                product=product,
                move_type='in',
                quantity=item.quantity,
                reference=receipt.reference,
                contact=receipt.supplier,
                stock_before=stock_before,
                stock_after=product.current_stock,
                performed_by=request.user,
            )
        receipt.status = 'done'
        receipt.save()

    messages.success(
        request, f'{receipt.reference} validated. Stock updated.'
    )
    return redirect('operations:receipt_detail', pk=pk)


@login_required
def receipt_cancel(request, pk):
    receipt = get_object_or_404(Receipt, pk=pk)
    if receipt.status == 'done':
        messages.error(request, 'Cannot cancel a validated receipt.')
        return redirect('operations:receipt_detail', pk=pk)
    receipt.status = 'cancel'
    receipt.save()
    messages.info(request, f'{receipt.reference} cancelled.')
    return redirect('operations:receipt_list')


# ── DELIVERIES ────────────────────────────────────────

@login_required
def delivery_list(request):
    deliveries = Delivery.objects.select_related(
        'responsible', 'warehouse'
    ).all()
    status = request.GET.get('status')
    if status:
        deliveries = deliveries.filter(status=status)
    return render(request, 'operations/deliveries/list.html', {
        'deliveries': deliveries
    })


@login_required
def delivery_create(request):
    products   = Product.objects.filter(is_active=True)
    warehouses = Warehouse.objects.all()
    if request.method == 'POST':
        delivery_address = request.POST.get('delivery_address', '').strip()
        warehouse_id     = request.POST.get('warehouse')
        schedule_date    = request.POST.get('schedule_date')
        operation_type   = request.POST.get('operation_type', '').strip()
        notes            = request.POST.get('notes', '').strip()
        product_ids      = request.POST.getlist('product_id')
        quantities       = request.POST.getlist('quantity')

        if not product_ids:
            messages.error(request, 'Add at least one product.')
            return render(request, 'operations/deliveries/create.html', {
                'products': products,
                'warehouses': warehouses
            })

        with transaction.atomic():
            delivery = Delivery.objects.create(
                delivery_address=delivery_address,
                warehouse_id=warehouse_id if warehouse_id else None,
                schedule_date=schedule_date if schedule_date else None,
                operation_type=operation_type,
                notes=notes,
                responsible=request.user,
                status='draft',
            )
            for pid, qty in zip(product_ids, quantities):
                if pid and qty:
                    DeliveryItem.objects.create(
                        delivery=delivery,
                        product_id=int(pid),
                        quantity=int(qty)
                    )

        messages.success(
            request, f'Delivery {delivery.reference} created.'
        )
        return redirect('operations:delivery_detail', pk=delivery.pk)

    return render(request, 'operations/deliveries/create.html', {
        'products': products,
        'warehouses': warehouses
    })


@login_required
def delivery_detail(request, pk):
    delivery = get_object_or_404(
        Delivery.objects.prefetch_related('items__product'), pk=pk
    )
    return render(request, 'operations/deliveries/detail.html', {
        'delivery': delivery
    })


@login_required
def delivery_validate(request, pk):
    delivery = get_object_or_404(Delivery, pk=pk)
    if delivery.status == 'done':
        messages.warning(request, 'Already validated.')
        return redirect('operations:delivery_detail', pk=pk)
    if delivery.status == 'cancel':
        messages.error(request, 'Cannot validate a cancelled delivery.')
        return redirect('operations:delivery_detail', pk=pk)
    if not delivery.items.exists():
        messages.error(request, 'No products in this delivery.')
        return redirect('operations:delivery_detail', pk=pk)

    # Stock check first
    for item in delivery.items.all():
        if item.product.current_stock < item.quantity:
            messages.error(
                request,
                f'Insufficient stock for "{item.product.name}". '
                f'Available: {item.product.current_stock}, '
                f'Required: {item.quantity}.'
            )
            return redirect('operations:delivery_detail', pk=pk)

    with transaction.atomic():
        for item in delivery.items.all():
            product      = item.product
            stock_before = product.current_stock
            product.current_stock -= item.quantity
            product.save()
            StockLedger.objects.create(
                product=product,
                move_type='out',
                quantity=item.quantity,
                reference=delivery.reference,
                contact=delivery.delivery_address,
                stock_before=stock_before,
                stock_after=product.current_stock,
                performed_by=request.user,
            )
        delivery.status = 'done'
        delivery.save()

    messages.success(
        request, f'{delivery.reference} validated. Stock updated.'
    )
    return redirect('operations:delivery_detail', pk=pk)


@login_required
def delivery_cancel(request, pk):
    delivery = get_object_or_404(Delivery, pk=pk)
    if delivery.status == 'done':
        messages.error(request, 'Cannot cancel a validated delivery.')
        return redirect('operations:delivery_detail', pk=pk)
    delivery.status = 'cancel'
    delivery.save()
    messages.info(request, f'{delivery.reference} cancelled.')
    return redirect('operations:delivery_list')


# ── ADJUSTMENTS ───────────────────────────────────────

@login_required
def adjustment_list(request):
    adjustments = Adjustment.objects.select_related(
        'product', 'responsible'
    ).all()
    return render(request, 'operations/adjustments/list.html', {
        'adjustments': adjustments
    })


@login_required
def adjustment_create(request):
    products  = Product.objects.filter(is_active=True)
    locations = Location.objects.select_related('warehouse').all()
    if request.method == 'POST':
        product_id  = request.POST.get('product')
        location_id = request.POST.get('location')
        counted_qty = request.POST.get('counted_qty')
        reason      = request.POST.get('reason', 'correction')
        notes       = request.POST.get('notes', '').strip()

        if not product_id or counted_qty is None:
            messages.error(request, 'Product and counted quantity are required.')
            return render(request, 'operations/adjustments/create.html', {
                'products': products,
                'locations': locations
            })

        with transaction.atomic():
            product      = get_object_or_404(Product, pk=product_id)
            stock_before = product.current_stock
            counted      = int(counted_qty)
            diff         = counted - stock_before

            adj = Adjustment.objects.create(
                product=product,
                location_id=location_id if location_id else None,
                counted_qty=counted,
                previous_qty=stock_before,
                difference=diff,
                reason=reason,
                notes=notes,
                responsible=request.user,
            )
            product.current_stock = counted
            product.save()

            StockLedger.objects.create(
                product=product,
                move_type='adjustment',
                quantity=abs(diff),
                reference=adj.reference,
                contact=f'Adjustment: {adj.get_reason_display()}',
                stock_before=stock_before,
                stock_after=product.current_stock,
                performed_by=request.user,
            )

        messages.success(
            request,
            f'Adjustment {adj.reference} applied. '
            f'Stock changed from {stock_before} to {counted}.'
        )
        return redirect('operations:adjustment_list')

    return render(request, 'operations/adjustments/create.html', {
        'products': products,
        'locations': locations
    })