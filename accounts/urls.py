from django.urls import path
from . import views  # Import views from the current package



urlpatterns = [
    path('signup/', views.signup, name='signup'),
    path('login/', views.login, name='login'),
    path('logout/', views.logout, name='logout'),
    path('', views.home, name='home'),  # Home page

    # Product URLs
    path('products/', views.product_list, name='product_list'),
    path('products/new/', views.product_create, name='product_create'),
    path('products/edit/<int:pk>/', views.product_update, name='product_update'),
    path('products/delete/<int:pk>/', views.product_delete, name='product_delete'),

    
    #URLS for daily orders
    path('orders/', views.orders_list, name='orders_list'),
    path('orders/update/<int:pk>/', views.orders_update, name='orders_update'),
    path('orders/delete/<int:pk>/', views.orders_delete, name='orders_delete'),
    path('orders/create1/', views.orders_create, name='orders_create'),
    path('orders/detail/<int:pk>/', views.orders_detail, name='orders_detail'),
    path('orders/detail/<int:pk>/add_item_using_search/<int:pk1>/', views.add_item_using_search, name='add_item_using_search'),
    path('orders/detail/update/<int:pk>/', views.orders_detail_update, name='orders_detail_update'),
    path('orders/detail/delete/<int:pk>/', views.orders_detail_delete, name='orders_detail_delete'),
    path('orders/detail/<int:pk>/add_item_manually/<str:product_name>/<str:quantity>/<str:mrp>/<str:price>/', views.add_product_manually ,name="add_product_manually"),
    path('orders/create1/<int:pk>/add_item_manually/<str:product_name>/<str:quantity>/<str:mrp>/<str:price>/', views.add_product_manually ,name="add_product_manually"),
    path('orders/create1/<int:pk>/changeName/', views.change_order_name, name='change_order_name'),
    path('orders/detail/<int:pk>/print_bill/<str:cashReceived>/', views.orders_print_bill, name='orders_print_bill'),


    #urls for function orders
    path('orders/function', views.function_orders_list, name='function_orders_list'),
    path('orders/function/detail/<int:pk>/', views.function_orders_detail, name='function_orders_detail'),
    path('orders/function/create1/', views.function_orders_create, name='function_orders_create'),
    path('orders/function/update/<int:pk>/', views.function_orders_update, name='function_orders_update'),
    path('orders/function/delete/<int:pk>/', views.function_orders_delete, name='function_orders_delete'),
    path('orders/function/detail/update/<int:pk>/', views.function_orders_detail_update, name='function_orders_detail_update'),
    path('orders/function/detail/delete/<int:pk>/', views.function_orders_detail_delete, name='function_orders_detail_delete'),
    path('orders/function/detail/<int:pk>/function_add_item_using_search/<int:pk1>/', views.function_add_item_using_search, name='function_add_item_using_search'),
    path('orders/function/create1/<int:pk>/add_item_manually/<str:product_name>/<str:quantity>/<str:price>/', views.add_function_product_manually, name='add_function_product_manually'),
    path('orders/function/detail/<int:pk>/add_item_manually/<str:product_name>/<str:quantity>/<str:price>/', views.add_function_product_manually ,name="add_function_product_manually"),
    path('orders/function/create1/<int:pk>/changeName/', views.change_function_order_name, name='change_function_order_name'),
    path('orders/function/detail/<int:pk>/print_bill/<str:cashReceived>/', views.function_orders_print_bill, name='function_orders_print_bill'),

    #URLs for journal book
    path('journal/list/', views.journal_list, name='journal_list'),
    path('journal/create/', views.journal_create, name='journal_create'),
    path('journal/<int:pk>/edit/', views.journal_update, name='journal_update'),
    path('journal/<int:pk>/delete/', views.journal_delete, name='journal_delete'),

    #URL for showing out of stock items for function orders while printing bill
    path('item/<int:pk>/function-out-of-stock/<int:cash_received>/', views.function_any_item_out_of_stock, name='function_any_item_out_of_stock'),
    
    
    #URL for showing out of stock items for Daily orders while printing bill
    path('item/<int:pk>/daily-out-of-stock/<int:cash_received>/', views.daily_any_item_out_of_stock, name='daily_any_item_out_of_stock'),


    #URL for showing list of products which are out of stock
    path('stock_out_products/list/', views.out_of_stock_products, name='out_of_stock_products'),

    #Function DebtCustomer  URLs
    path('debt/function/customers/', views.function_debt_customer_list, name='function_debt_customer_list'),
    # path('debt/customers/create/', views.create_debt_customer, name='create_debt_customer'),
    # path('debt/customers/update/<int:pk>/', views.update_debt_customer, name='update_debt_customer'),
    # path('debt/customers/delete/<int:pk>/', views.delete_debt_customer, name='delete_debt_customer'),

    #Daily DebtCustomer  URLs
    path('daily/debt/customers/', views.daily_debt_customer_list, name='daily_debt_customer_list'),

    #sales Urls
    path('overall/sales/',views.sales_summary,name='sales_summary'),
]