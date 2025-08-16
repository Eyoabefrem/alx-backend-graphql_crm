
import django_filters
from .models import Customer, Product, Order

class CustomerFilter(django_filters.FilterSet):
    name = django_filters.CharFilter(field_name="name", lookup_expr="icontains")
    email = django_filters.CharFilter(field_name="email", lookup_expr="icontains")
    createdAtGte = django_filters.DateFilter(field_name="created_at", lookup_expr="gte")
    createdAtLte = django_filters.DateFilter(field_name="created_at", lookup_expr="lte")
    phonePattern = django_filters.CharFilter(field_name="phone", lookup_expr="startswith")

    class Meta:
        model = Customer
        fields = ['name', 'email', 'createdAtGte', 'createdAtLte', 'phonePattern']

class ProductFilter(django_filters.FilterSet):
    price_gte = django_filters.NumberFilter(field_name="price", lookup_expr='gte')
    price_lte = django_filters.NumberFilter(field_name="price", lookup_expr='lte')
    stock_gte = django_filters.NumberFilter(field_name="stock", lookup_expr='gte')
    stock_lte = django_filters.NumberFilter(field_name="stock", lookup_expr='lte')

    class Meta:
        model = Product
        fields = ['name', 'price_gte', 'price_lte', 'stock_gte', 'stock_lte']

class OrderFilter(django_filters.FilterSet):
    total_amount_gte = django_filters.NumberFilter(field_name="total_amount", lookup_expr='gte')
    total_amount_lte = django_filters.NumberFilter(field_name="total_amount", lookup_expr='lte')
    order_date_gte = django_filters.DateFilter(field_name="order_date", lookup_expr='gte')
    order_date_lte = django_filters.DateFilter(field_name="order_date", lookup_expr='lte')
    customer_name = django_filters.CharFilter(field_name="customer__name", lookup_expr='icontains')
    product_name = django_filters.CharFilter(field_name="products__name", lookup_expr='icontains')

    class Meta:
        model = Order
        fields = ['total_amount_gte', 'total_amount_lte', 'order_date_gte', 'order_date_lte', 'customer_name', 'product_name']
