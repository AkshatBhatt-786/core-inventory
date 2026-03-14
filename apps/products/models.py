from django.db import models
from django.contrib.auth.models import User


class Category(models.Model):
    name        = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    created_at  = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = 'Categories'
        ordering = ['name']

    def __str__(self):
        return self.name


class Warehouse(models.Model):
    name       = models.CharField(max_length=100, unique=True)
    short_code = models.CharField(max_length=10, unique=True)
    address    = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} ({self.short_code})"


class Location(models.Model):
    name       = models.CharField(max_length=100)
    short_code = models.CharField(max_length=10)
    warehouse  = models.ForeignKey(
                    Warehouse,
                    on_delete=models.CASCADE,
                    related_name='locations'
                 )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('short_code', 'warehouse')

    def __str__(self):
        return f"{self.warehouse.short_code}/{self.short_code}"


class Product(models.Model):

    UNIT_CHOICES = [
        ('pcs',  'Pieces'),
        ('kg',   'Kilograms'),
        ('g',    'Grams'),
        ('l',    'Litres'),
        ('ml',   'Millilitres'),
        ('m',    'Metres'),
        ('box',  'Box'),
        ('pack', 'Pack'),
    ]

    name            = models.CharField(max_length=200)
    sku             = models.CharField(max_length=50, unique=True)
    category        = models.ForeignKey(
                        Category,
                        on_delete=models.SET_NULL,
                        null=True, blank=True,
                        related_name='products'
                      )
    unit_of_measure = models.CharField(
                        max_length=10,
                        choices=UNIT_CHOICES,
                        default='pcs'
                      )
    cost_price      = models.DecimalField(
                        max_digits=10,
                        decimal_places=2,
                        default=0.00
                      )
    reorder_level   = models.PositiveIntegerField(default=0)
    initial_stock   = models.PositiveIntegerField(default=0)
    current_stock   = models.IntegerField(default=0)
    warehouse       = models.ForeignKey(
                        Warehouse,
                        on_delete=models.SET_NULL,
                        null=True, blank=True,
                        related_name='products'
                      )
    is_active       = models.BooleanField(default=True)
    created_at      = models.DateTimeField(auto_now_add=True)
    updated_at      = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return f"{self.name} ({self.sku})"

    @property
    def is_low_stock(self):
        return self.current_stock <= self.reorder_level

    @property
    def is_out_of_stock(self):
        return self.current_stock <= 0

    def save(self, *args, **kwargs):
        # On first save, set current_stock from initial_stock
        if not self.pk:
            self.current_stock = self.initial_stock
        super().save(*args, **kwargs)