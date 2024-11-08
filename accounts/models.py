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


# class SalesReport(models.Model):
#     date = models.DateField(default=timezone.now)
#     total_sales = models.DecimalField(max_digits=10, decimal_places=2, default=0)
#     total_quantity_sold = models.DecimalField(max_digits=10, decimal_places=2, default=0)

#     def __str__(self):
#         return f"Sales Report for {self.date} - Total Sales: {self.total_sales}"

class JournalBook(models.Model):
    today_payment = models.CharField(max_length=1000)
    online_payment = models.CharField(max_length=1000)
    previous_amount = models.CharField(max_length=1000)
    date = models.DateField(default=timezone.now)

    def __str__(self):
        return f"Payment: Today - {self.today_payment}, Online - {self.online_payment}, Previous - {self.previous_amount}, Date - {self.date}"
    
# #Model for storing due customers of fuction orders
# class FunctionDebtCustomer(models.Model):
#     name = models.CharField(max_length=255)
#     # phone_number = models.CharField(max_length=15)  # Adjust length as needed
#     date = models.DateField(default=timezone.now)
#     amount_due = models.DecimalField(max_digits=10, decimal_places=2, default=0)

#     def __str__(self):
#         return f"{self.name} - Amount Due: {self.amount_due}"

#     def update_amount(self, new_amount):
#         """Update the amount due."""
#         self.amount_due = new_amount
#         self.save()

class Orders(models.Model):
    name = models.CharField(max_length=255)
    # payment = models.DecimalField(max_digits=10, decimal_places=2,blank=True, null=True)
    date = models.DateField(default=timezone.now)

    def __str__(self):
        return self.name
    

    @property
    def total_sale(self):
        total = 0
        order_items = OrderItems.objects.filter(orders=self)  # Fetch all related order items for this order
        for item in order_items:
            total += item.total_price  # Sum the total price for each item in the order
        return total




class OrderItems(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, null=True)
    orders = models.ForeignKey(Orders, on_delete=models.CASCADE, null=True)
    quantity = models.DecimalField(max_digits=10, decimal_places=3, default=0)  
    # price = models.DecimalField(max_digits=10, decimal_places=2, default=0)  

    
    @property
    def total_price(self):
        return int(self.quantity * self.product.Retail_price)
    
    @property
    def mrp_price(self):
        return int(self.quantity * self.product.mrp)



class FunctionOrders(models.Model):
    name = models.CharField(max_length=255)
    # payment = models.DecimalField(max_digits=10, decimal_places=2,blank=True, null=True)
    date = models.DateField(default=timezone.now)

    def __str__(self):
        return self.name
    

    @property
    def total_sale(self):
        total = 0
        function_order_items = FunctionOrderItems.objects.filter(orders=self)  # Fetch all related function order items for this order
        for item in function_order_items:
            total += item.total_price  # Sum the total price for each function order item
        return total


class FunctionOrderItems(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, null=True)
    orders = models.ForeignKey(FunctionOrders, on_delete=models.CASCADE, null=True)
    quantity = models.DecimalField(max_digits=10, decimal_places=3, default=0)  
    # price = models.DecimalField(max_digits=10, decimal_places=2, default=0)  

    
    @property
    def total_price(self):
        return int(self.quantity * self.product.Bulk_price)
    

class Payment(models.Model):
    function_order_id = models.ForeignKey(FunctionOrders, on_delete=models.CASCADE, null=True)
    daily_order_id = models.ForeignKey(Orders, on_delete=models.CASCADE, null=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    date = models.DateField(default=timezone.now)

