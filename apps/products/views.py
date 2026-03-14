from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q, F
from .models import Product, Category, Warehouse, Location
from apps.ledger.models import StockLedger


@login_required
def product_list(request):
    products = Product.objects.select_related(
        'category', 'warehouse'
    ).filter(is_active=True)
    q = request.GET.get('q')
    if q:
        products = products.filter(
            Q(name__icontains=q) | Q(sku__icontains=q)
        )
    filter_by = request.GET.get('filter')
    if filter_by == 'low_stock':
        products = products.filter(
            current_stock__lte=F('reorder_level'),
            current_stock__gt=0
        )
    elif filter_by == 'out_of_stock':
        products = products.filter(current_stock__lte=0)
    return render(request, 'products/list.html', {
        'products': products
    })


@login_required
def product_create(request):
    categories = Category.objects.all()
    warehouses = Warehouse.objects.all()
    if request.method == 'POST':
        name            = request.POST.get('name', '').strip()
        sku             = request.POST.get('sku', '').strip().upper()
        category_id     = request.POST.get('category')
        unit_of_measure = request.POST.get('unit_of_measure', 'pcs')
        cost_price      = request.POST.get('cost_price', 0)
        initial_stock   = request.POST.get('initial_stock', 0)
        reorder_level   = request.POST.get('reorder_level', 0)
        warehouse_id    = request.POST.get('warehouse')

        # Validation
        if not name:
            messages.error(request, 'Product name is required.')
            return render(request, 'products/create.html', {
                'categories': categories,
                'warehouses': warehouses
            })
        if not sku:
            messages.error(request, 'SKU is required.')
            return render(request, 'products/create.html', {
                'categories': categories,
                'warehouses': warehouses
            })
        if Product.objects.filter(sku=sku).exists():
            messages.error(request, f'SKU {sku} already exists.')
            return render(request, 'products/create.html', {
                'categories': categories,
                'warehouses': warehouses
            })

        product = Product.objects.create(
            name=name,
            sku=sku,
            category_id=category_id if category_id else None,
            unit_of_measure=unit_of_measure,
            cost_price=cost_price,
            initial_stock=int(initial_stock),
            reorder_level=int(reorder_level),
            warehouse_id=warehouse_id if warehouse_id else None,
            is_active=True,
        )
        messages.success(request, f'Product "{product.name}" created.')
        return redirect('products:list')

    return render(request, 'products/create.html', {
        'categories': categories,
        'warehouses': warehouses
    })


@login_required
def product_detail(request, pk):
    product = get_object_or_404(Product, pk=pk)
    ledger_entries = StockLedger.objects.filter(
        product=product
    ).order_by('-created_at')[:20]
    return render(request, 'products/detail.html', {
        'product': product,
        'ledger_entries': ledger_entries,
    })


@login_required
def product_edit(request, pk):
    product    = get_object_or_404(Product, pk=pk)
    categories = Category.objects.all()
    warehouses = Warehouse.objects.all()
    if request.method == 'POST':
        product.name            = request.POST.get('name', '').strip()
        product.unit_of_measure = request.POST.get('unit_of_measure', 'pcs')
        product.cost_price      = request.POST.get('cost_price', 0)
        product.reorder_level   = request.POST.get('reorder_level', 0)
        category_id             = request.POST.get('category')
        warehouse_id            = request.POST.get('warehouse')
        product.category_id     = category_id if category_id else None
        product.warehouse_id    = warehouse_id if warehouse_id else None
        product.save()
        messages.success(request, f'Product "{product.name}" updated.')
        return redirect('products:detail', pk=product.pk)
    return render(request, 'products/edit.html', {
        'product':    product,
        'categories': categories,
        'warehouses': warehouses
    })


@login_required
def warehouse_list(request):
    warehouses = Warehouse.objects.prefetch_related('locations').all()
    return render(request, 'products/warehouse_list.html', {
        'warehouses': warehouses
    })


@login_required
def warehouse_create(request):
    if request.method == 'POST':
        name       = request.POST.get('name', '').strip()
        short_code = request.POST.get('short_code', '').strip().upper()
        address    = request.POST.get('address', '').strip()
        if not name or not short_code:
            messages.error(request, 'Name and short code are required.')
        elif Warehouse.objects.filter(short_code=short_code).exists():
            messages.error(request, f'Short code {short_code} already exists.')
        else:
            Warehouse.objects.create(
                name=name, short_code=short_code, address=address
            )
            messages.success(request, f'Warehouse "{name}" created.')
            return redirect('products:warehouse_list')
    return render(request, 'products/warehouse_form.html', {
        'title': 'New Warehouse'
    })


@login_required
def category_list(request):
    categories = Category.objects.all()
    return render(request, 'products/category_list.html', {
        'categories': categories
    })


@login_required
def category_create(request):
    if request.method == 'POST':
        name        = request.POST.get('name', '').strip()
        description = request.POST.get('description', '').strip()
        if not name:
            messages.error(request, 'Category name is required.')
        elif Category.objects.filter(name=name).exists():
            messages.error(request, f'Category "{name}" already exists.')
        else:
            Category.objects.create(name=name, description=description)
            messages.success(request, f'Category "{name}" created.')
            return redirect('products:category_list')
    return render(request, 'products/category_form.html', {
        'title': 'New Category'
    })