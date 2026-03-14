from django.db import models
from django.contrib.auth.models import User
from apps.products.models import Product, Location


class StockLedger(models.Model):

    MOVE_TYPE_CHOICES = [
        ('in',         'Stock In'),
        ('out',        'Stock Out'),
        ('adjustment', 'Adjustment'),
        ('transfer',   'Internal Transfer'),
    ]

    product        = models.ForeignKey(
                        Product,
                        on_delete=models.PROTECT,
                        related_name='ledger_entries'
                     )
    move_type      = models.CharField(
                        max_length=15,
                        choices=MOVE_TYPE_CHOICES
                     )
    quantity       = models.IntegerField()
    from_location  = models.ForeignKey(
                        Location,
                        on_delete=models.SET_NULL,
                        null=True, blank=True,
                        related_name='outgoing_moves'
                     )
    to_location    = models.ForeignKey(
                        Location,
                        on_delete=models.SET_NULL,
                        null=True, blank=True,
                        related_name='incoming_moves'
                     )
    reference      = models.CharField(max_length=50, blank=True)
    contact        = models.CharField(max_length=200, blank=True)
    stock_before   = models.IntegerField()
    stock_after    = models.IntegerField()
    performed_by   = models.ForeignKey(
                        User,
                        on_delete=models.SET_NULL,
                        null=True, blank=True
                     )
    created_at     = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Stock Ledger Entry'
        verbose_name_plural = 'Stock Ledger'

    def __str__(self):
        return f"{self.reference} | {self.product.name} | {self.move_type} | {self.quantity}"