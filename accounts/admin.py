
from django.contrib import admin

# Register your models here.
from .models import *


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'Retail_price', 'Bulk_price', 'mrp', 'stock_quantity', 'created_at', 'updated_at')
    search_fields = ('name',)
    list_filter = ('created_at', 'updated_at')
    ordering = ('name',)

@admin.register(JournalBook)
class JournalBookAdmin(admin.ModelAdmin):
    list_display = ['today_payment', 'online_payment', 'previous_amount', 'date']
    search_fields = ['today_payment', 'online_payment', 'previous_amount', 'date']



@admin.register(Orders)
class OrdersAdmin(admin.ModelAdmin):
    list_display = ('id', 'name','date')  # Fields to display in the list view
    search_fields = ('name',)  # Fields to search


@admin.register(OrderItems)
class OrderItemsAdmin(admin.ModelAdmin):
    list_display = ('id', 'product', 'orders', 'quantity')  # Fields to display
    search_fields = ('orders',)  # Fields to search
    list_filter = ('orders',)  # Filter by orders



@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ('id' ,'order_id','amount','date')  # Fields to display in the list view
    search_fields = ('order_id',)  # Fields to search


@admin.register(FlatsDebtCustomer)
class FlatsDebtCustomerAdmin(admin.ModelAdmin):
    list_display = ('id','name','due_amount','date')
    search_fields = ('name',)
