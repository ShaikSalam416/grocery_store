from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login as auth_login, logout as auth_logout
from .forms import CustomAuthenticationForm
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, JsonResponse
# from .forms import ProductForm, CustomerForm, PriceVariationForm, SaleForm, SaleItemForm, CustomUserCreationForm
# from .models import Product, Customer, PriceVariation, Sale, SaleItem
from django.core.paginator import Paginator
# from .forms import CustomUserCreationForm, ProductSearchForm, OrdersForm, ProductForm,JournalBookForm, OrderItemsForm,FunctionOrdersForm, FunctionOrderItemsForm,PaymentForm
# from .models import Product, JournalBook, Orders, OrderItems, FunctionOrders, FunctionOrderItems, Payment
from .models import Product, JournalBook, Orders, OrderItems, Payment
from .forms import CustomUserCreationForm, ProductSearchForm, OrdersForm, ProductForm,JournalBookForm, OrderItemsForm,PaymentForm

from django.urls import reverse_lazy
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views import generic
import json
from datetime import date
from decimal import Decimal
from django.db.models import Sum
from django.db import connection
from datetime import datetime
from django.utils import timezone  # Import timezone module
from collections import defaultdict




def signup(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            auth_login(request, user)
            return redirect('login')
    else:
        form = CustomUserCreationForm()    
    return render(request, 'signup.html', {'form': form})

def login(request):
    if request.method == 'POST':
        form = CustomAuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            auth_login(request, user)
            return redirect('home')
    else:
        form = CustomAuthenticationForm()
    return render(request, 'login.html', {'form': form})

def logout(request):
    auth_logout(request)
    return redirect('login')
    
@login_required
def home(request):
    return render(request, 'home.html')


# View to list all products

def product_list(request):
    form = ProductSearchForm(request.GET or None)  # Initialize the form with GET data
    query = request.GET.get('q', '')  # Get the search query from GET parameters

    if query:
        product_list = Product.objects.filter(name__icontains=query).order_by('name')  # Filter by query
    else:
        product_list = Product.objects.all().order_by('name')  # Get all products if no query

    # Set up pagination
    paginator = Paginator(product_list, 100)  # Show 10 products per page
    page_number = request.GET.get('page')  # Get the current page number from GET parameters
    page_obj = paginator.get_page(page_number)  # Get the products for the current page

    return render(request, 'product_list.html', {'form': form, 'page_obj': page_obj, 'query': query})

# View to create a new product
def product_create(request):
    if request.method == 'POST':
        form = ProductForm(request.POST)
        if form.is_valid():
            product = form.save(commit=False)
            product.Retail_price = product.Retail_price or Decimal('0.00')
            product.Bulk_price = product.Bulk_price or Decimal('0.00')
            form.save()
            return redirect('product_list')
    else:
        form = ProductForm()
    return render(request, 'product_form.html', {'form': form})

# View to update an existing product
def product_update(request, pk):
    product = get_object_or_404(Product, pk=pk)
    if request.method == 'POST':
        form = ProductForm(request.POST, instance=product)
        if form.is_valid():
            form.save()
            return redirect('product_list')
    else:
        form = ProductForm(instance=product)
    return render(request, 'product_form.html', {'form': form})

# View to delete a product
def product_delete(request, pk):
    product = get_object_or_404(Product, pk=pk)
    if request.method == 'POST':
        product.delete()
        return redirect('product_list')
    return render(request, 'product_confirm_delete.html', {'product': product})

#View to show out of stock products from product model 
def out_of_stock_products(request):
    osp = Product.objects.filter(stock_quantity = 0)
    context = {'out_of_stock_products': osp}
    return render(request, 'out_of_stock_products.html', context)

# View For Function Debt Customers
def function_debt_customer_list(request):
     # Get date parameters from the request
    from_date_str  = request.GET.get('from_date')
    to_date_str  = request.GET.get('to_date')

    debt_cust = get_orders_with_pending_balance(request,is_function = True)

     # Prepare formatted debt customer data for processing
    formatted_debt_cust = []

    for row in debt_cust:
        date = row[2]
        debt_customer_data = {
            'order_id': row[0],
            'pending_amount': int(row[1]),
            'date': date,
            'name': row[3],
        }
        formatted_debt_cust.append(debt_customer_data)

  

      # Convert from_date and to_date to datetime.date objects if they exist
    from_date = datetime.strptime(from_date_str, '%Y-%m-%d').date() if from_date_str else None
    to_date = datetime.strptime(to_date_str , '%Y-%m-%d').date() if to_date_str  else None

    
    if from_date:
        formatted_debt_cust = [
            customer for customer in formatted_debt_cust if customer['date'] >= from_date
        ]
    if to_date:
        formatted_debt_cust = [
            customer for customer in formatted_debt_cust if customer['date'] <= to_date
        ]

     # Pass the formatted data to the template
    context = {
        'debt_customers': formatted_debt_cust,  # List of dicts for easy template access
        'from_date': from_date_str,
        'to_date': to_date_str
    }
    return render(request, 'list_debt_customers.html', context)



# View For Daily Debt Customers
def daily_debt_customer_list(request):
     # Get date parameters from the request
    from_date_str  = request.GET.get('from_date')
    to_date_str  = request.GET.get('to_date')

    debt_cust = daily_get_orders_with_pending_balance(request,is_function = False)

     # Prepare formatted debt customer data for processing
    formatted_debt_cust = []

    for row in debt_cust:
        date = row[2]
        debt_customer_data = {
            'order_id': row[0],
            'pending_amount': int(row[1]),
            'date': date,
            'name': row[3],
        }
        formatted_debt_cust.append(debt_customer_data)

  

      # Convert from_date and to_date to datetime.date objects if they exist
    from_date = datetime.strptime(from_date_str, '%Y-%m-%d').date() if from_date_str else None
    to_date = datetime.strptime(to_date_str , '%Y-%m-%d').date() if to_date_str  else None

    
    if from_date:
        formatted_debt_cust = [
            customer for customer in formatted_debt_cust if customer['date'] >= from_date
        ]
    if to_date:
        formatted_debt_cust = [
            customer for customer in formatted_debt_cust if customer['date'] <= to_date
        ]

     # Pass the formatted data to the template
    context = {
        'debt_customers': formatted_debt_cust,  # List of dicts for easy template access
        'from_date': from_date_str,
        'to_date': to_date_str
    }
    return render(request, 'daily_list_debt_customers.html', context)



def orders_list_with_items(request, pk):
    payment = get_object_or_404(Orders, pk=pk)
    order_items = OrderItems.objects.filter(orders=payment)

    return render(request, 'orders_ordersitems.html', {
        'Orders': payment,
        'orderItems': order_items,
    })


def save_order_items(edit,selected_id,p_name,quan,mrp,r_price,t_price):
      
        if edit is not None:
            try:        
                foi = OrderItems.objects.get(id=selected_id)  # Get the existing item
                foi.product.name = p_name
                if quan == '' or quan is None:
                    # quan = t_price/b_price
                    quan = (Decimal(t_price) / Decimal(r_price))  # Calculate quantity based on total price and bulk price
                    # OrderItems.total_price = int(t_price)
                else:
                    # quan = 1
                    foi.quantity = quan

                foi.quantity = quan
                foi.product.mrp = Decimal(mrp)
                foi.product.Retail_price = Decimal(r_price)
                foi.save()
            except OrderItems.DoesNotExist:
                pass

def orders_list(request):
    orders = Orders.objects.filter(is_function=False).order_by('-date')  # '-' before 'date' indicates descending order
    return render(request, 'orders_list.html', {'orders': orders})

def orders_create(request):
    edit = get_form_data(request,'edit')
    selected_id = get_form_data(request,'item_id')
    # p_name = get_form_data(request,'product_name')
    # quan = get_form_data(request,'quantity')
    # b_price = get_form_data(request,'bulk_price')
    # t_price = get_form_data(request,'total_price')
    p_name = request.GET.get('product_name')
    quan = request.GET.get('quantity')
    mrp = request.GET.get('mrp')
    r_price = request.GET.get('retail_price')
    t_price = request.GET.get('total_price')

    is_func = request.GET.get('is_function') == 'true' 
    if is_func:
        save_order_items(edit,selected_id,p_name,quan,mrp,r_price,t_price)

    form = ProductSearchForm(request.GET or None)  # Initialize the form with GET data
    query = request.GET.get('q', '')  # Get the search query from GET parameters

    if query:
        product_list = Product.objects.filter(name__icontains=query).order_by('name')  # Filter by query
    else:
        product_list = Product.objects.all().order_by('name')  # Get all products if no query
    
    product = Product.objects.all()
    base_name = 'Name'
    
    # Create or get the order
    order, created = Orders.objects.get_or_create(name=f"{base_name} (temp)", 
            date=date.today(),
            is_function=is_func  # Set is_function field to the value retrieved from the URL
    )
    
    order_items = OrderItems.objects.filter(orders=order)
    total_price = round(sum(item.total_price for item in order_items))  

    # Update the order's name with its ID
    order.name = f"{base_name} {order.id}"
    order.save()  # Save the updated name to the database

    if request.method == 'POST':
        # Handle OrderItems creation
        item_form = OrderItemsForm(request.POST)
        if item_form.is_valid():
            new_order_item = item_form.save(commit=False)  # Prevent immediate save
            new_order_item.orders = order  # Link the order item to the created order
            new_order_item.save()
            return redirect('orders_list')  # Redirect to order list or relevant page
    else:
        item_form = OrderItemsForm()
    if edit != None:
        selected_id=None

    return render(request, 'orders_ordersitems.html', {
        
        'item_form': item_form,
        'product': product,
        'Orders': order,
        'query': query,
        'form' : form,
        'productList': product_list,
        'total_price' : total_price,
        'orderItems' : order_items,
        'selected_id' : selected_id,
    })


def orders_update(request, pk):
    order = get_object_or_404(Orders, pk=pk)
    if request.method == 'POST':
        form = OrdersForm(request.POST, instance=order)
        if form.is_valid():
            form.save()
            return redirect('orders_list')
    else:
        form = OrdersForm(instance=order)
        print(form.errors)
    return render(request, 'ordersitems_form.html', {'form': form})

def orders_delete(request, pk):
    order = get_object_or_404(Orders, pk=pk)
    if request.method == 'POST':
        order.delete()
        return redirect('orders_list')
    return render(request, 'orders_confirm_delete.html', {'order': order})


def orders_detail(request, pk):
    edit = get_form_data(request,'edit')
    selected_id = get_form_data(request,'item_id')
    # p_name = get_form_data(request,'product_name')
    # quan = get_form_data(request,'quantity')
    # b_price = get_form_data(request,'bulk_price')
    # t_price = get_form_data(request,'total_price')
    p_name = request.GET.get('product_name')
    quan = request.GET.get('quantity')
    mrp = request.GET.get('mrp')
    r_price = request.GET.get('retail_price')
    t_price = request.GET.get('total_price')

    save_order_items(edit,selected_id,p_name,quan,mrp,r_price,t_price)

    form = ProductSearchForm(request.GET or None)  # Initialize the form with GET data
    query = request.GET.get('q', '')  # Get the search query from GET parameters

    if query:
        product_list = Product.objects.filter(name__icontains=query).order_by('name')  # Filter by query
    else:
        product_list = Product.objects.all().order_by('name')  # Get all products if no query

    order = get_object_or_404(Orders, pk=pk)
    product = Product.objects.all()
    order_items = OrderItems.objects.filter(orders=order)
    total_price = sum(item.total_price for item in order_items)

    if request.method == 'POST':
        form = OrderItemsForm(request.POST)
        if form.is_valid():
            new_item = form.save(commit=False)
            new_item.orders = order  # Link the item to the current order
            new_item.save()
            return redirect('orders_detail', pk=order.pk)  # Redirect to the same detail page to show updated items
    else:
        form = OrderItemsForm()
    if edit != None:
        selected_id=None

    return render(request, 'orders_detail.html', {
        'form': form,
        'total_price' : total_price,
        'Orders': order,
        'orderItems': order_items,
        'product' : product,
        'productList'  : product_list,
        'query' : query,
        'selected_id' : selected_id,
    })


def orders_detail_update(request, pk):
   order_item = get_object_or_404(OrderItems, id=pk)
    
   if request.method == 'POST':
        quantity = Decimal(request.POST.get('quantity', order_item.quantity))
        order_item.quantity = quantity
        order_item.save()
        return redirect('orders_detail', pk=order_item.orders.pk)  # Redirect to order detail after editing

   return render(request, 'orders_detail_update.html', {'order_item': order_item})

def orders_detail_delete(request, pk):
    order_item = get_object_or_404(OrderItems, pk=pk)
    
    if request.method == 'GET':
        order_item.delete()
        return redirect('orders_detail', pk=order_item.orders.pk)  # Redirect to order detail after deleting

    return redirect('orders_detail', pk=order_item.orders.pk)  # Redirect to order detail after deleting


def add_item_using_search(request, pk, pk1):
    order = get_object_or_404(Orders, pk=pk)
    p = get_object_or_404(Product, pk=pk1)
    daily_get_orders_with_pending_balance(request,is_function=False)
    if request.method == 'GET':
        quantity = Decimal(request.POST.get('quantity', 1))  # Default to 1 if not provided
        oi = OrderItems()
        oi.product = p
        oi.orders = order
        oi.quantity = quantity
        oi.save()
        return redirect(f"/orders/detail/{order.pk}/?item_id={oi.id}")
    
    return redirect('orders_detail', pk=pk)



#Views for Fucntion orders
def function_orders_list(request):
    orders = Orders.objects.filter(is_function=True).order_by('-date')  # '-' before 'date' indicates descending order
    return render(request, 'function_orders_list.html', {'orders': orders})

#For clicking on edit button
def get_form_data(request,id):
    try:
        selected_id = int(request.GET[id])
        return selected_id
    except Exception as e:
        return None
    
def save_items(edit,selected_id,p_name,quan,b_price,t_price):
      
        if edit is not None:
            try:        
                foi = OrderItems.objects.get(id=selected_id)  # Get the existing item
                foi.product.name = p_name
                if quan == '' or quan is None:
                    # quan = t_price/b_price
                    quan = (Decimal(t_price) / Decimal(b_price))  # Calculate quantity based on total price and bulk price
                    # FunctionOrderItems.total_price = int(t_price)
                else:
                    # quan = 1
                    foi.quantity = quan

                foi.quantity = quan
                foi.product.Bulk_price = b_price
                foi.save()
            except OrderItems.DoesNotExist:
                pass

def function_orders_detail(request, pk):
    edit = get_form_data(request,'edit')
    selected_id = get_form_data(request,'item_id')
    # p_name = get_form_data(request,'product_name')
    # quan = get_form_data(request,'quantity')
    # b_price = get_form_data(request,'bulk_price')
    # t_price = get_form_data(request,'total_price')
    p_name = request.GET.get('product_name')
    quan = request.GET.get('quantity')
    b_price = request.GET.get('bulk_price')
    t_price = request.GET.get('total_price')

    
    save_items(edit,selected_id,p_name,quan,b_price,t_price)

    form = ProductSearchForm(request.GET or None)  # Initialize the form with GET data
    query = request.GET.get('q', '')  # Get the search query from GET parameters

    if query:
        product_list = Product.objects.filter(name__icontains=query).order_by('name')  # Filter by query
    else:
        product_list = Product.objects.all().order_by('name')  # Get all products if no query

    order = get_object_or_404(Orders, pk=pk)
    product = Product.objects.all()
    order_items = OrderItems.objects.filter(orders=order)
    total_price = round(sum(item.function_total_price for item in order_items))  


    if request.method == 'POST':
        form = OrderItemsForm(request.POST)
        if form.is_valid():
            new_item = form.save(commit=False)
            new_item.orders = order  # Link the item to the current order
            new_item.save()
            return redirect('function_orders_detail', pk=order.pk)  # Redirect to the same detail page to show updated items
    else:
        form = OrderItemsForm()
    if edit != None:
        selected_id=None

    return render(request, 'function_orders_detail.html', {
        'form': form,
        'total_price' : total_price,
        'Orders': order,
        'orderItems': order_items,
        'product' : product,
        'productList'  : product_list,
        'query' : query,
        'selected_id' : selected_id,
    })


def function_orders_create(request):
    edit = get_form_data(request,'edit')
    selected_id = get_form_data(request,'item_id')
    # p_name = get_form_data(request,'product_name')
    # quan = get_form_data(request,'quantity')
    # b_price = get_form_data(request,'bulk_price')
    # t_price = get_form_data(request,'total_price')
    p_name = request.GET.get('product_name')
    quan = request.GET.get('quantity')
    b_price = request.GET.get('bulk_price')
    t_price = request.GET.get('function_total_price')

    is_func = request.GET.get('is_function') == 'true'
    if is_func:
        save_items(edit,selected_id,p_name,quan,b_price,t_price)

    form = ProductSearchForm(request.GET or None)  # Initialize the form with GET data
    query = request.GET.get('q', '')  # Get the search query from GET parameters

    if query:
        product_list = Product.objects.filter(name__icontains=query).order_by('name')  # Filter by query
    else:
        product_list = Product.objects.all().order_by('name')  # Get all products if no query
    
    # order = get_object_or_404(FunctionOrders, pk=pk)
    product = Product.objects.all()
      
    base_name = 'Name'
    
    # Create or get the order
    order, created = Orders.objects.get_or_create(name=f"{base_name} (temp)", 
            date=date.today(),
            is_function=is_func  # Set is_function field to the value retrieved from the URL
    )

    order_items = OrderItems.objects.filter(orders=order)
    total_price = round(sum(item.function_total_price for item in order_items))  
    # Update the order's name with its ID
    order.name = f"{base_name} {order.id}"
    order.save()  # Save the updated name to the database

    if request.method == 'POST':
        # Handle OrderItems creation
        item_form = OrderItemsForm(request.POST)
        if item_form.is_valid():
            new_order_item = item_form.save(commit=False)  # Prevent immediate save
            new_order_item.orders = order  # Link the order item to the created order
            new_order_item.save()
            return redirect('function_orders_list')  # Redirect to order list or relevant page
    else:
        item_form = OrderItemsForm()
    if edit != None:
        selected_id=None

    return render(request, 'function_orders_ordersitems.html', {
        
        'item_form': item_form,
        'product': product,
        'Orders': order,
        'query': query,
        'productList': product_list,
        'form' : form,
        'total_price' : total_price,
        'orderItems' : order_items,
        'selected_id' : selected_id,
    })


def function_orders_update(request, pk):
    order = get_object_or_404(Orders, pk=pk)
    if request.method == 'POST':
        form = OrdersForm(request.POST, instance=order)
        if form.is_valid():
            form.save()
            return redirect('function_orders_list')
    else:
        form = OrdersForm(instance=order)
        print(form.errors)
    return render(request, 'function_ordersitems_form.html', {'form': form})

def function_orders_delete(request, pk):
    order = get_object_or_404(Orders, pk=pk)
    if request.method == 'POST':
        order.delete()
        return redirect('function_orders_list')
    return render(request, 'function_orders_confirm_delete.html', {'order': order})


def function_add_item_using_search(request, pk, pk1):
    order = get_object_or_404(Orders, pk=pk)
    p = get_object_or_404(Product, pk=pk1)
    
    if request.method == 'GET':
        quantity = Decimal(request.POST.get('quantity', 1))  # Default to 1 if not provided
        oi = OrderItems()
        oi.product = p
        oi.orders = order
        oi.quantity = quantity
        oi.save()
        # return redirect('function_orders_detail', pk=order.pk)
        return redirect(f"/orders/function/detail/{order.pk}/?item_id={oi.id}")

    
    return redirect('function_orders_detail', pk=pk)


def function_orders_detail_update(request, pk):
   order_item = get_object_or_404(OrderItems, id=pk)
    
   if request.method == 'POST':
        quantity = Decimal(request.POST.get('quantity', order_item.quantity))
        order_item.quantity = quantity
        order_item.save()
        return redirect('function_orders_detail', pk=order_item.orders.pk)  # Redirect to order detail after editing

   return render(request, 'function_orders_detail_update.html', {'order_item': order_item})

def function_orders_detail_delete(request, pk):
    order_item = get_object_or_404(OrderItems, pk=pk)
    
    if request.method == 'GET':
        order_item.delete()
        return redirect('function_orders_detail', pk=order_item.orders.pk)  # Redirect to order detail after deleting

    return redirect('function_orders_detail', pk=order_item.orders.pk)  # Redirect to order detail after deleting


def add_function_product_manually(request,pk,product_name,quantity,price):
    order=get_object_or_404(Orders, id=pk)
    Quantity=Decimal(quantity)
    Price=Decimal(price)
    if request.method == 'GET':
        # Create a new Product instance and save it
        product = Product(name=product_name, Retail_price=0, Bulk_price=Price, mrp=0, stock_quantity=Quantity)  # Adjust field names as necessary
        product.save()

        # Create a new FunctionOrderItems instance and link it to the order and the new product
        oi = OrderItems()
        oi.product = product
        oi.orders = order
        oi.quantity = Decimal(quantity)
        # oi.price = price  # Ensure this field exists in your model
        oi.save()

        # Redirect to the order details page after saving
        return redirect('function_orders_detail', pk=pk)
    
    return redirect('function_orders_detail', pk=pk)
    
    
def add_product_manually(request,pk,product_name,quantity,mrp,price):
    order=get_object_or_404(Orders,pk=pk)
    Quantity = Decimal(quantity)
    Mrp = Decimal(mrp)
    RetailPrice = Decimal(price)
    if request.method == 'GET':
        p = Product(name = product_name, mrp = Mrp, Retail_price = RetailPrice, stock_quantity = Quantity ,Bulk_price = 0)
        p.save()

        f = OrderItems()
        f.product = p
        f.orders = order
        f.quantity = Quantity
        f.save()

        return redirect(orders_detail,pk=pk)
    
    return redirect(orders_detail,pk=pk)

def change_function_order_name(request,pk):
    fo = get_object_or_404(Orders,pk=pk)
    if request.method == 'POST':
        form = OrdersForm(request.POST, instance=fo)
        if form.is_valid():
            form.save()
            return redirect('function_orders_detail',pk=pk)
    else:
        form = OrdersForm(instance=fo)
    return render(request, 'function_order_change_name_form.html', {'form': form})


def change_order_name(request,pk):
    fo = get_object_or_404(Orders,pk=pk)
    if request.method == 'POST':
        form = OrdersForm(request.POST, instance=fo)
        if form.is_valid():
            form.save()
            return redirect('orders_detail',pk=pk)
    else:
        form = OrdersForm(instance=fo)
    return render(request, 'order_change_name_form.html', {'form': form})

    
def total_cash_recieved(id,cash_recieved1):
    with connection.cursor() as cursor:
        cursor.execute(""" 
            SELECT order_id_id, SUM(amount) AS paid_amount
                    FROM accounts_payment
					WHERE order_id_id = %s
                    GROUP BY order_id_id;
            """,[id])
        
        rows = cursor.fetchall()
     # If rows are not empty, get the paid_amount, otherwise set it to 0
    if rows:
        paid_amount = rows[0][1]  # The paid amount is at index 1 in the result
    else:
        paid_amount = 0  # No payments found, set paid amount to 0
    return paid_amount + cash_recieved1


def orders_print_bill(request,pk,cashReceived):
    cash_recieved = int(cashReceived)
    order = get_object_or_404(Orders,pk=pk)
    order_items = OrderItems.objects.filter(orders=order)
    subtotal = sum(item.total_price for item in order_items)
    total = int(round(subtotal))  # Total after rounding
    due_amount = int(round(total - cash_recieved))
    # saved_amount = (sum(item.mrp_price for item in order_items))-total
    saved_amount = sum(
        item.mrp_price - item.total_price for item in order_items if item.mrp_price > 0
    )
    order_id = order.id
    cash_recieved1 = total_cash_recieved(order_id,cash_recieved)
    due_amount = int(round(total - cash_recieved1))
    out_of_stock_items = []

    
    # Check stock for each item and collect out-of-stock items
    for item in order_items:
        product = item.product  # Assuming FunctionOrderItems has a ForeignKey to Product
        if not product.is_in_stock(item.quantity):
            out_of_stock_items.append(item)

    # If there are out-of-stock items, redirect to the out-of-stock view
    if out_of_stock_items:
        return redirect('daily_any_item_out_of_stock', pk=pk, cash_received=cashReceived)

    
    
    # Get the current date to track the bill number
    # today = timezone.now().date()
    today = datetime.now()
    date = datetime.now().date()
    # Check if the session already has the bill number for today
    if 'bill_number_date' in request.session and request.session['bill_number_date'] == str(date):
        # Increment the bill number for today
        bill_number = request.session.get('bill_number', 0) + 1
    else:
        # If the session doesn't have today's bill number, reset it to 1
        bill_number = 1

    # Update session data for the bill number and date
    request.session['bill_number_date'] = str(date)
    request.session['bill_number'] = bill_number


    context = {
        'Orders': order,
        'orderItems': order_items,
        'total': total,
        'cash' : cash_recieved,
        'due' : due_amount,
        'saved_amount' : saved_amount,
        'billnumber' : bill_number,
        # 'total_in_words': total_in_words,
        'current_date' : today,  # Format current date as needed
    }

    Payment.objects.create(
            amount = cash_recieved,
            order_id = order,
            date = timezone.now()
        )

      # Update stock quantities for each order item
    for item in order_items:
        product = item.product  # Assuming FunctionOrderItems has a ForeignKey to Product
        if product.is_in_stock(item.quantity):
            product.stock_quantity -= item.quantity
            product.save()
        # else:
        #     # Handle the case where there's insufficient stock
        #     # You can raise an error or log it, for now, we'll just print a message
        #     print(f"Insufficient stock for product: {product.name}")


    # Render the template
    return render(request, 'printBill.html', context)  # Replace with your actual template name


def function_orders_print_bill(request,pk,cashReceived):
    cash_recieved = int(cashReceived)
    order = get_object_or_404(Orders,pk=pk)
    order_items = OrderItems.objects.filter(orders = order)
    subtotal = sum(item.function_total_price for item in order_items)
    total = int(round(subtotal))  # Total after rounding
    # due_amount = int(round(total - cash_recieved))
    weight = float(sum(item.quantity for item in order_items))

    order_id = order.id
    cash_recieved1 = total_cash_recieved(order_id,cash_recieved)
    due_amount = int(round(total - cash_recieved1))
    out_of_stock_items = []

    # Check stock for each item and collect out-of-stock items
    for item in order_items:
        product = item.product  # Assuming FunctionOrderItems has a ForeignKey to Product
        if not product.is_in_stock(item.quantity):
            out_of_stock_items.append(item)

    # If there are out-of-stock items, redirect to the out-of-stock view
    if out_of_stock_items:
        return redirect('function_any_item_out_of_stock', pk=pk, cash_received=cashReceived)
    

    # Get the current date to track the bill number
    # today = timezone.now().date()
    today =  datetime.now()    
    date = datetime.now().date()
    # Check if the session already has the bill number for today
    if 'bill_number_date' in request.session and request.session['bill_number_date'] == str(date):
        # Increment the bill number for today
        bill_number = request.session.get('bill_number', 0) + 1
    else:
        # If the session doesn't have today's bill number, reset it to 1
        bill_number = 1

    # Update session data for the bill number and date
    request.session['bill_number_date'] = str(date)
    request.session['bill_number'] = bill_number

    Payment.objects.create(
            amount = cash_recieved,
            order_id = order,
            date = timezone.now()
        )

      # Update stock quantities for each order item
    for item in order_items:
        product = item.product  # Assuming FunctionOrderItems has a ForeignKey to Product
        if product.is_in_stock(item.quantity):
            product.stock_quantity -= item.quantity
            product.save()
        # else:
        #     # Handle the case where there's insufficient stock
        #     # You can raise an error or log it, for now, we'll just print a message
        #     print(f"Insufficient stock for product: {product.name}")

    context = {
        'Orders': order,
        'orderItems': order_items,
        'total': total,
        'cash' : cash_recieved1,
        'due' : due_amount,
        'weight' : weight,
        'billnumber' : bill_number,
        # 'total_in_words': total_in_words,
        'current_date': today,  # Format current date as needed
    }
    # Render the template
    return render(request, 'function_printBill.html', context)  # Replace with your actual template name


def get_orders_with_pending_balance(obj,is_function=True):
  with connection.cursor() as cursor:
    cursor.execute("""
      SELECT e.*, f.date, f.name
FROM (
    SELECT c.orders_id, IFNULL(d.paid_amount, 0) - c.order_amount AS pending_amount
    FROM (
        SELECT a.orders_id, SUM(a.quantity * b.Bulk_price) AS order_amount
        FROM accounts_orderitems a
        JOIN accounts_product b ON a.product_id = b.id
        GROUP BY a.orders_id
    ) c
    LEFT JOIN (
        SELECT order_id_id, SUM(amount) AS paid_amount
        FROM accounts_payment
        GROUP BY order_id_id
    ) d ON c.orders_id = d.order_id_id
) e
JOIN accounts_orders f ON e.orders_id = f.id
WHERE e.pending_amount < 0
AND f.is_function = %s;
    """, [is_function])
    rows = cursor.fetchall()
     
    return rows


def daily_get_orders_with_pending_balance(obj,is_function=False):
  with connection.cursor() as cursor:
    cursor.execute("""
      SELECT e.*, f.date, f.name
FROM (
    SELECT c.orders_id, IFNULL(d.paid_amount, 0) - c.order_amount AS pending_amount
    FROM (
        SELECT a.orders_id, SUM(a.quantity * b.Retail_price) AS order_amount
        FROM accounts_orderitems a
        JOIN accounts_product b ON a.product_id = b.id
        GROUP BY a.orders_id
    ) c
    LEFT JOIN (
        SELECT order_id_id, SUM(amount) AS paid_amount
        FROM accounts_payment
        GROUP BY order_id_id
    ) d ON c.orders_id = d.order_id_id
) e
JOIN accounts_orders f ON e.orders_id = f.id
WHERE e.pending_amount < 0
AND f.is_function = %s;
    """,[is_function])
    rows = cursor.fetchall()
     
    return rows





def journal_list(request):
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')

    if start_date and end_date:
        # Filter entries based on the selected date range
        journal_entries = JournalBook.objects.filter(date__range=[start_date, end_date])
    else:
        journal_entries = JournalBook.objects.all()  # Show all entries if no filter is applied
    # journal_entries = JournalBook.objects.all()
    return render(request, 'journal_list.html', {'journal_entries': journal_entries})


# Create a new journal entry
def journal_create(request):
    if request.method == 'POST':
        form = JournalBookForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('journal_list')
    else:
        form = JournalBookForm()
    return render(request, 'journal_form.html', {'form': form})

# Update an existing journal entry
def journal_update(request, pk):
    journal_entry = get_object_or_404(JournalBook, pk=pk)
    if request.method == 'POST':
        form = JournalBookForm(request.POST, instance=journal_entry)
        if form.is_valid():
            form.save()
            return redirect('journal_list')
    else:
        form = JournalBookForm(instance=journal_entry)
    return render(request, 'journal_form.html', {'form': form})

# Delete a journal entry
def journal_delete(request, pk):
    journal_entry = get_object_or_404(JournalBook, pk=pk)
    if request.method == 'POST':
        journal_entry.delete()
        return redirect('journal_list')
    return render(request, 'journal_confirm_delete.html', {'journal_entry': journal_entry})


def function_any_item_out_of_stock(request, pk, cash_received):
    order = get_object_or_404(Orders, pk=pk)
    order_items = OrderItems.objects.filter(orders=order)
    
    out_of_stock_items = []

    # Check stock for each item
    for item in order_items:
        product = item.product  # Assuming FunctionOrderItems has a ForeignKey to Product
        if not product.is_in_stock(item.quantity):
            out_of_stock_items.append(item)  # Add to out-of-stock list

    context = {
        'Orders': order,
        'out_of_stock_items': out_of_stock_items,
        'current_date': timezone.now().strftime('%d/%m/%Y'),
        'cash_received': cash_received,  # Ensure this is passed
    }

    # Render the template
    return render(request, 'functionoutofstock.html', context)  # Replace with your actual template name


def daily_any_item_out_of_stock(request, pk, cash_received):
    order = get_object_or_404(Orders, pk=pk)
    order_items = OrderItems.objects.filter(orders=order)
    
    out_of_stock_items = []

    # Check stock for each item
    for item in order_items:
        product = item.product  # Assuming FunctionOrderItems has a ForeignKey to Product
        if not product.is_in_stock(item.quantity):
            out_of_stock_items.append(item)  # Add to out-of-stock list

    context = {
        'Orders': order,
        'out_of_stock_items': out_of_stock_items,
        'current_date': timezone.now().strftime('%d/%m/%Y'),
        'cash_received': cash_received,  # Ensure this is passed
    }

    # Render the template
    return render(request, 'dailyoutofstock.html', context)  # Replace with your actual template name


def sales_summary(request):
    # Get date parameters from the request (if any)
    from_date_str = request.GET.get('from_date')
    to_date_str = request.GET.get('to_date')

    # Convert the date strings to datetime objects if they are provided
    from_date = datetime.strptime(from_date_str, '%Y-%m-%d').date() if from_date_str else None
    to_date = datetime.strptime(to_date_str, '%Y-%m-%d').date() if to_date_str else None

    # Fetch Orders and FunctionOrders
    orders = Orders.objects.filter(is_function=False)
    function_orders = Orders.objects.filter(is_function=True)

    # If no date filter is provided, show sales only for today (current date)
    if not from_date and not to_date:
        today = timezone.now().date()
        orders = orders.filter(date=today)
        function_orders = function_orders.filter(date=today)
    else:
        # Apply filters if the dates are provided
        if from_date:
            orders = orders.filter(date__gte=from_date)  # Filter orders from the 'from_date'
            function_orders = function_orders.filter(date__gte=from_date)  # Filter function orders from the 'from_date'

        if to_date:
            orders = orders.filter(date__lte=to_date)  # Filter orders until the 'to_date'
            function_orders = function_orders.filter(date__lte=to_date)  # Filter function orders until the 'to_date'

    # Prepare the sales data, grouping by date
    sales_data = defaultdict(float)  # Using defaultdict to sum sales by date

    # Accumulate total sales for regular Orders by date
    for order in orders:
        sales_data[order.date] += order.total_sale  # Add the order's total sale to its corresponding date

    # Accumulate total sales for Function Orders by date
    for function_order in function_orders:
        sales_data[function_order.date] += function_order.function_total_sale  # Add the function order's total sale to its corresponding date

    # Prepare the final summary data
    sales_summary = []
    for date, total_sales in sales_data.items():
        sales_summary.append({
            'date': date,
            'total_sales': total_sales
        })

    # Pass data to the template
    context = {
        'sales_summary': sales_summary,
        'from_date': from_date_str,
        'to_date': to_date_str,
    }

    return render(request, 'sales_summary.html', context)