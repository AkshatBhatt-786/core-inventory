from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('apps.accounts.urls')),
    path('dashboard/', include('apps.dashboard.urls')),
    path('products/', include('apps.products.urls')),
    path('operations/', include('apps.operations.urls')),
    path('ledger/', include('apps.ledger.urls')),

    # Redirect root to dashboard
    path('', include('apps.dashboard.urls')),
]