from django.db import models
from django.contrib.auth.models import User
from apps.products.models import Product, Warehouse, Location


class Receipt(models.Model):

    STATUS_CHOICES = [
        ('draft',   'Draft'),
        ('ready',   'Ready'),
        ('done',    'Done'),
        ('cancel',  'Cancelled'),
    ]

    reference     = models.CharField(max_length=50, unique=True, blank=True)
    supplier      = models.CharField(max_length=200, blank=True)
    receive_from  = models.CharField(max_length=200, blank=True)
    warehouse     = models.ForeignKey(
                        Warehouse,
                        on_delete=models.SET_NULL,
                        null=True, blank=True
                    )
    schedule_date = models.DateField(null=True, blank=True)
    responsible   = models.ForeignKey(
                        User,
                        on_delete=models.SET_NULL,
                        null=True, blank=True
                    )
    status        = models.CharField(
                        max_length=10,
                        choices=STATUS_CHOICES,
                        default='draft'
                    )
    notes         = models.TextField(blank=True)
    created_at    = models.DateTimeField(auto_now_add=True)
    updated_at    = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.reference

    def save(self, *args, **kwargs):
        # Auto-generate reference like WH/IN/0001
        if not self.reference:
            count = Receipt.objects.count() + 1
            self.reference = f"WH/IN/{str(count).zfill(4)}"
        super().save(*args, **kwargs)


class ReceiptItem(models.Model):
    receipt  = models.ForeignKey(
                    Receipt,
                    on_delete=models.CASCADE,
                    related_name='items'
                )
    product  = models.ForeignKey(
                    Product,
                    on_delete=models.PROTECT,
                    related_name='receipt_items'
                )
    quantity = models.PositiveIntegerField(default=1)

    def __str__(self):
        return f"{self.receipt.reference} - {self.product.name}"


class Delivery(models.Model):

    STATUS_CHOICES = [
        ('draft',    'Draft'),
        ('waiting',  'Waiting'),
        ('ready',    'Ready'),
        ('done',     'Done'),
        ('cancel',   'Cancelled'),
    ]

    reference        = models.CharField(max_length=50, unique=True, blank=True)
    delivery_address = models.TextField(blank=True)
    warehouse        = models.ForeignKey(
                            Warehouse,
                            on_delete=models.SET_NULL,
                            null=True, blank=True
                        )
    schedule_date    = models.DateField(null=True, blank=True)
    responsible      = models.ForeignKey(
                            User,
                            on_delete=models.SET_NULL,
                            null=True, blank=True
                        )
    operation_type   = models.CharField(max_length=100, blank=True)
    status           = models.CharField(
                            max_length=10,
                            choices=STATUS_CHOICES,
                            default='draft'
                        )
    notes            = models.TextField(blank=True)
    created_at       = models.DateTimeField(auto_now_add=True)
    updated_at       = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name_plural = 'Deliveries'

    def __str__(self):
        return self.reference

    def save(self, *args, **kwargs):
        if not self.reference:
            count = Delivery.objects.count() + 1
            self.reference = f"WH/OUT/{str(count).zfill(4)}"
        super().save(*args, **kwargs)


class DeliveryItem(models.Model):
    delivery = models.ForeignKey(
                    Delivery,
                    on_delete=models.CASCADE,
                    related_name='items'
                )
    product  = models.ForeignKey(
                    Product,
                    on_delete=models.PROTECT,
                    related_name='delivery_items'
                )
    quantity = models.PositiveIntegerField(default=1)

    def __str__(self):
        return f"{self.delivery.reference} - {self.product.name}"


class Adjustment(models.Model):

    REASON_CHOICES = [
        ('damaged',   'Damaged'),
        ('lost',      'Lost'),
        ('found',     'Found'),
        ('correction','Correction'),
        ('other',     'Other'),
    ]

    reference      = models.CharField(max_length=50, unique=True, blank=True)
    product        = models.ForeignKey(
                        Product,
                        on_delete=models.PROTECT,
                        related_name='adjustments'
                     )
    location       = models.ForeignKey(
                        Location,
                        on_delete=models.SET_NULL,
                        null=True, blank=True
                     )
    counted_qty    = models.IntegerField()
    previous_qty   = models.IntegerField()
    difference     = models.IntegerField()
    reason         = models.CharField(
                        max_length=20,
                        choices=REASON_CHOICES,
                        default='correction'
                     )
    responsible    = models.ForeignKey(
                        User,
                        on_delete=models.SET_NULL,
                        null=True, blank=True
                     )
    notes          = models.TextField(blank=True)
    created_at     = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.reference

    def save(self, *args, **kwargs):
        if not self.reference:
            count = Adjustment.objects.count() + 1
            self.reference = f"WH/ADJ/{str(count).zfill(4)}"
        # Auto calculate difference
        self.difference = self.counted_qty - self.previous_qty
        super().save(*args, **kwargs)