from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db import transaction
from .models import Receipt, ReceiptItem, Delivery, DeliveryItem, Adjustment
from apps.products.models import Product, Warehouse, Location
from apps.ledger.models import StockLedger


# ── HELPERS ───────────────────────────────────────────

def parse_items(product_ids, quantities):
    """
    Zip product_ids and quantities, remove empty/zero rows,
    return list of (pid_str, qty_int) tuples.
    """
    items = []
    for pid, qty in zip(product_ids, quantities):
        try:
            if pid and int(qty) > 0:
                items.append((pid, int(qty)))
        except (ValueError, TypeError):
            continue
    return items


def check_duplicates(items):
    """
    Return the first duplicate product id found, or None.
    """
    seen = []
    for pid, _ in items:
        if pid in seen:
            return pid
        seen.append(pid)
    return None


def write_ledger(product, move_type, quantity, reference, contact, user):
    """
    Write a single StockLedger entry.
    Assumes product.current_stock is already updated before calling.
    """
    StockLedger.objects.create(
        product=product,
        move_type=move_type,
        quantity=quantity,
        reference=reference,
        contact=contact,
        stock_before=product.current_stock - quantity
        if move_type == 'in'
        else product.current_stock + quantity,
        stock_after=product.current_stock,
        performed_by=user,
    )


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
    products   = Product.objects.filter(is_active=True).order_by('name')
    warehouses = Warehouse.objects.all()

    if request.method != 'POST':
        return render(request, 'operations/receipts/create.html', {
            'products': products, 'warehouses': warehouses
        })

    # Parse items
    items = parse_items(
        request.POST.getlist('product_id'),
        request.POST.getlist('quantity')
    )

    if not items:
        messages.error(request, 'Add at least one product with a valid quantity.')
        return render(request, 'operations/receipts/create.html', {
            'products': products, 'warehouses': warehouses
        })

    # Duplicate check
    dup_id = check_duplicates(items)
    if dup_id:
        dup_name = Product.objects.get(pk=dup_id).name
        messages.error(
            request,
            f'"{dup_name}" appears more than once. Combine into one row.'
        )
        return render(request, 'operations/receipts/create.html', {
            'products': products, 'warehouses': warehouses
        })

    warehouse_id  = request.POST.get('warehouse') or None
    schedule_date = request.POST.get('schedule_date') or None

    with transaction.atomic():
        receipt = Receipt.objects.create(
            supplier      = request.POST.get('supplier', '').strip(),
            receive_from  = request.POST.get('receive_from', '').strip(),
            warehouse_id  = warehouse_id,
            schedule_date = schedule_date,
            notes         = request.POST.get('notes', '').strip(),
            responsible   = request.user,
            status        = 'draft',
        )
        ReceiptItem.objects.bulk_create([
            ReceiptItem(receipt=receipt, product_id=int(pid), quantity=qty)
            for pid, qty in items
        ])

    messages.success(request, f'Receipt {receipt.reference} created as Draft.')
    return redirect('operations:receipt_detail', pk=receipt.pk)


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
    if request.method != 'POST':
        return redirect('operations:receipt_detail', pk=pk)

    receipt = get_object_or_404(Receipt, pk=pk)

    if receipt.status == 'done':
        messages.warning(request, 'This receipt is already validated.')
        return redirect('operations:receipt_detail', pk=pk)

    if receipt.status == 'cancel':
        messages.error(request, 'Cannot validate a cancelled receipt.')
        return redirect('operations:receipt_detail', pk=pk)

    items = list(receipt.items.select_related('product').all())

    if not items:
        messages.error(request, 'Cannot validate a receipt with no products.')
        return redirect('operations:receipt_detail', pk=pk)

    with transaction.atomic():
        for item in items:
            product = item.product
            product.current_stock += item.quantity
            product.save(update_fields=['current_stock', 'updated_at'])
            write_ledger(
                product   = product,
                move_type = 'in',
                quantity  = item.quantity,
                reference = receipt.reference,
                contact   = receipt.supplier or '',
                user      = request.user,
            )
        receipt.status = 'done'
        receipt.save(update_fields=['status', 'updated_at'])

    messages.success(
        request,
        f'{receipt.reference} validated successfully. '
        f'Stock updated for {len(items)} product(s).'
    )
    return redirect('operations:receipt_detail', pk=pk)


@login_required
def receipt_cancel(request, pk):
    if request.method != 'POST':
        return redirect('operations:receipt_detail', pk=pk)

    receipt = get_object_or_404(Receipt, pk=pk)

    if receipt.status == 'done':
        messages.error(request, 'Cannot cancel a validated receipt.')
        return redirect('operations:receipt_detail', pk=pk)

    receipt.status = 'cancel'
    receipt.save(update_fields=['status', 'updated_at'])
    messages.info(request, f'{receipt.reference} has been cancelled.')
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
    products   = Product.objects.filter(is_active=True).order_by('name')
    warehouses = Warehouse.objects.all()

    if request.method != 'POST':
        return render(request, 'operations/deliveries/create.html', {
            'products': products, 'warehouses': warehouses
        })

    items = parse_items(
        request.POST.getlist('product_id'),
        request.POST.getlist('quantity')
    )

    if not items:
        messages.error(request, 'Add at least one product with a valid quantity.')
        return render(request, 'operations/deliveries/create.html', {
            'products': products, 'warehouses': warehouses
        })

    # Duplicate check
    dup_id = check_duplicates(items)
    if dup_id:
        dup_name = Product.objects.get(pk=dup_id).name
        messages.error(
            request,
            f'"{dup_name}" appears more than once. Combine into one row.'
        )
        return render(request, 'operations/deliveries/create.html', {
            'products': products, 'warehouses': warehouses
        })

    # Stock availability check
    for pid, qty in items:
        product = get_object_or_404(Product, pk=pid)
        if product.current_stock < qty:
            messages.error(
                request,
                f'Insufficient stock for "{product.name}". '
                f'Available: {product.current_stock}, Requested: {qty}.'
            )
            return render(request, 'operations/deliveries/create.html', {
                'products': products, 'warehouses': warehouses
            })

    warehouse_id  = request.POST.get('warehouse') or None
    schedule_date = request.POST.get('schedule_date') or None

    with transaction.atomic():
        delivery = Delivery.objects.create(
            delivery_address = request.POST.get('delivery_address', '').strip(),
            warehouse_id     = warehouse_id,
            schedule_date    = schedule_date,
            operation_type   = request.POST.get('operation_type', '').strip(),
            notes            = request.POST.get('notes', '').strip(),
            responsible      = request.user,
            status           = 'draft',
        )
        DeliveryItem.objects.bulk_create([
            DeliveryItem(delivery=delivery, product_id=int(pid), quantity=qty)
            for pid, qty in items
        ])

    messages.success(request, f'Delivery {delivery.reference} created as Draft.')
    return redirect('operations:delivery_detail', pk=delivery.pk)


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
    if request.method != 'POST':
        return redirect('operations:delivery_detail', pk=pk)

    delivery = get_object_or_404(Delivery, pk=pk)

    if delivery.status == 'done':
        messages.warning(request, 'This delivery is already validated.')
        return redirect('operations:delivery_detail', pk=pk)

    if delivery.status == 'cancel':
        messages.error(request, 'Cannot validate a cancelled delivery.')
        return redirect('operations:delivery_detail', pk=pk)

    items = list(delivery.items.select_related('product').all())

    if not items:
        messages.error(request, 'Cannot validate a delivery with no products.')
        return redirect('operations:delivery_detail', pk=pk)

    # Stock check — must pass for ALL items before touching anything
    for item in items:
        if item.product.current_stock < item.quantity:
            messages.error(
                request,
                f'Insufficient stock for "{item.product.name}". '
                f'Available: {item.product.current_stock}, '
                f'Required: {item.quantity}.'
            )
            return redirect('operations:delivery_detail', pk=pk)

    with transaction.atomic():
        for item in items:
            product = item.product
            product.current_stock -= item.quantity
            product.save(update_fields=['current_stock', 'updated_at'])
            write_ledger(
                product   = product,
                move_type = 'out',
                quantity  = item.quantity,
                reference = delivery.reference,
                contact   = delivery.delivery_address or '',
                user      = request.user,
            )
        delivery.status = 'done'
        delivery.save(update_fields=['status', 'updated_at'])

    messages.success(
        request,
        f'{delivery.reference} validated successfully. '
        f'Stock reduced for {len(items)} product(s).'
    )
    return redirect('operations:delivery_detail', pk=pk)


@login_required
def delivery_cancel(request, pk):
    if request.method != 'POST':
        return redirect('operations:delivery_detail', pk=pk)

    delivery = get_object_or_404(Delivery, pk=pk)

    if delivery.status == 'done':
        messages.error(request, 'Cannot cancel a validated delivery.')
        return redirect('operations:delivery_detail', pk=pk)

    delivery.status = 'cancel'
    delivery.save(update_fields=['status', 'updated_at'])
    messages.info(request, f'{delivery.reference} has been cancelled.')
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
    products  = Product.objects.filter(is_active=True).order_by('name')
    locations = Location.objects.select_related('warehouse').all()

    if request.method != 'POST':
        return render(request, 'operations/adjustments/create.html', {
            'products': products, 'locations': locations
        })

    product_id  = request.POST.get('product')
    counted_qty = request.POST.get('counted_qty', '').strip()
    location_id = request.POST.get('location') or None
    reason      = request.POST.get('reason', 'correction')
    notes       = request.POST.get('notes', '').strip()

    # Validate inputs
    if not product_id:
        messages.error(request, 'Please select a product.')
        return render(request, 'operations/adjustments/create.html', {
            'products': products, 'locations': locations
        })

    if not counted_qty:
        messages.error(request, 'Counted quantity is required.')
        return render(request, 'operations/adjustments/create.html', {
            'products': products, 'locations': locations
        })

    try:
        counted = int(counted_qty)
        if counted < 0:
            raise ValueError
    except ValueError:
        messages.error(request, 'Counted quantity must be a positive number.')
        return render(request, 'operations/adjustments/create.html', {
            'products': products, 'locations': locations
        })

    with transaction.atomic():
        product      = get_object_or_404(Product, pk=product_id)
        stock_before = product.current_stock
        diff         = counted - stock_before

        if diff == 0:
            messages.info(
                request,
                f'No change needed — "{product.name}" already has '
                f'{counted} units recorded.'
            )
            return redirect('operations:adjustment_list')

        adj = Adjustment.objects.create(
            product     = product,
            location_id = location_id,
            counted_qty = counted,
            previous_qty= stock_before,
            difference  = diff,
            reason      = reason,
            notes       = notes,
            responsible = request.user,
        )

        product.current_stock = counted
        product.save(update_fields=['current_stock', 'updated_at'])

        StockLedger.objects.create(
            product      = product,
            move_type    = 'adjustment',
            quantity     = abs(diff),
            reference    = adj.reference,
            contact      = f'Adjustment: {adj.get_reason_display()}',
            stock_before = stock_before,
            stock_after  = counted,
            performed_by = request.user,
        )

    direction = f'+{diff}' if diff > 0 else str(diff)
    messages.success(
        request,
        f'Adjustment {adj.reference} applied. '
        f'"{product.name}" stock: {stock_before} → {counted} ({direction}).'
    )
    return redirect('operations:adjustment_list')