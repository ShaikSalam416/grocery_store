from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator
from django.utils import timezone  # Import timezone module
from decimal import Decimal

# Create your models here.

#product model
class Product(models.Model):
    name = models.CharField(max_length=255)
    Retail_price = models.DecimalField(max_digits=10, decimal_places=2,blank=True)
    Bulk_price = models.DecimalField(max_digits=10, decimal_places=2,blank=True)
    mrp = models.DecimalField(max_digits=10, decimal_places=2, blank=True,default=0)  # New MRP field
    # stock_quantity = models.IntegerField()
    stock_quantity = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))  # Change to DecimalField
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name
    
    def is_in_stock(self, quantity):
        return self.stock_quantity >= quantity

class JournalBook(models.Model):
    today_payment = models.CharField(max_length=1000)
    online_payment = models.CharField(max_length=1000)
    previous_amount = models.CharField(max_length=1000)
    date = models.DateField(default=timezone.now)

    # def __str__(self):
        # return f"Payment: Today - {self.today_payment}, Online - {self.online_payment}, Previous - {self.previous_amount}, Date - {self.date}"
        
class Orders(models.Model):
    name = models.CharField(max_length=255)
    # payment = models.DecimalField(max_digits=10, decimal_places=2,blank=True, null=True)
    date = models.DateField(default=timezone.now)
    is_function = models.BooleanField(default=True)

    def __str__(self):
        return self.name
    

    @property
    def total_sale(self):
        total = 0
        order_items = OrderItems.objects.filter(orders=self)  # Fetch all related order items for this order
        for item in order_items:
            total += item.total_price  # Sum the total price for each item in the order
        return total
    
    @property
    def function_total_sale(self):
        total = 0
        function_order_items = OrderItems.objects.filter(orders=self)  # Fetch all related function order items for this order
        for item in function_order_items:
            total += item.function_total_price  # Sum the total price for each function order item
        return total




class OrderItems(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, null=True)
    orders = models.ForeignKey(Orders, on_delete=models.CASCADE, null=True)
    quantity = models.DecimalField(max_digits=10, decimal_places=3, default=0)  
    # price = models.DecimalField(max_digits=10, decimal_places=2, default=0)  

    
    @property
    def total_price(self):
        # return Decimal(self.quantity * self.product.Retail_price)
        total = Decimal(self.quantity) * Decimal(self.product.Retail_price)
        return total.quantize(Decimal('0.00'))
    
    @property
    def function_total_price(self):
        # return Decimal(self.quantity * self.product.Bulk_price)
        total = Decimal(self.quantity) * Decimal(self.product.Bulk_price)
        return total.quantize(Decimal('0.00'))
        # return round(total)
    
    @property
    def mrp_price(self):
        return int(self.quantity * self.product.mrp)
    

class Payment(models.Model):
    # function_order_id = models.ForeignKey(FunctionOrders, on_delete=models.CASCADE, null=True)
    order_id = models.ForeignKey(Orders, on_delete=models.CASCADE, null=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    date = models.DateField(default=timezone.now)

class FlatsDebtCustomer(models.Model):
    name = models.CharField(max_length=100)
    due_amount = models.IntegerField()
    date = models.DateField(default=timezone.now)

    def __str__(self):
        return self.name
