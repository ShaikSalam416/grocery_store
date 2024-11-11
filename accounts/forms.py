
from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User
from .models import Product, Orders, OrderItems, JournalBook, Payment, FlatsDebtCustomer

from datetime import date



class CustomUserCreationForm(UserCreationForm):
    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        if commit:
            user.save()
        return user    

class CustomAuthenticationForm(AuthenticationForm):
    class Meta:
        model = User
        fields = ['username', 'password']


class ProductSearchForm(forms.Form):
    query = forms.CharField(label='Search', max_length=255, required=False)

class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['name', 'mrp', 'Retail_price', 'Bulk_price', 'stock_quantity']



class OrderForm(forms.Form):
    quantity = forms.IntegerField(
        min_value=1,
        error_messages={
            'required': 'Please enter a quantity.',
            'min_value': 'Quantity must be at least 1.'
        }
    )

    def clean_quantity(self):
        quantity = self.cleaned_data.get('quantity')
        if quantity <= 0:
            raise forms.ValidationError("Quantity must be greater than zero.")
        return quantity


class OrderForm(forms.Form):
    product = forms.ModelChoiceField(queryset=Product.objects.all(), empty_label="Select a product")
    quantity = forms.IntegerField(min_value=1, initial=1)


class JournalBookForm(forms.ModelForm):
    class Meta:
        model = JournalBook
        fields = ['today_payment', 'online_payment', 'previous_amount', 'date']


class OrdersForm(forms.ModelForm):
    class Meta:
        model = Orders
        fields = ['name', 'date', 'is_function']

    def __init__(self, *args, **kwargs):
        super(OrdersForm, self).__init__(*args, **kwargs)
        # You can set initial values if necessary
        self.fields['name'].initial = 'Name'  # Set a default name if required
        self.fields['date'].initial = date.today()  # Set today's date as the default


class OrderItemsForm(forms.ModelForm):
    class Meta:
        model = OrderItems
        # fields = ['product', 'orders', 'quantity']
        fields = ['product', 'quantity']


class PaymentForm(forms.ModelForm):
    class Meta:
        model = Payment
        fields = ['order_id', 'amount', 'date']


class FlatDebtCustomerForm(forms.ModelForm):
    class Meta:
        model = FlatsDebtCustomer
        fields = ['name', 'due_amount', 'date']