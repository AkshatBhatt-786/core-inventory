from django.contrib import admin
from django.urls import path, include
from django.views.generic import RedirectView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', RedirectView.as_view(url='/dashboard/', permanent=False)),
    path('accounts/',   include('apps.accounts.urls')),
    path('dashboard/',  include('apps.dashboard.urls')),
    path('products/',   include('apps.products.urls')),
    path('operations/', include('apps.operations.urls')),
    path('ledger/',     include('apps.ledger.urls')),
]