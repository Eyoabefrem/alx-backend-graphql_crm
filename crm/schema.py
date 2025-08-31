
import graphene
from graphene_django import DjangoObjectType
from .models import Customer, Product, Order
from django.db import transaction
from django.core.exceptions import ValidationError
import re
from graphene_django.filter import DjangoFilterConnectionField
from .filters import CustomerFilter, ProductFilter, OrderFilter
from crm.models import Product


# ==== TYPES ====
class CustomerType(DjangoObjectType):
    class Meta:
        model = Customer

class ProductType(DjangoObjectType):
    class Meta:
        model = Product

class OrderType(DjangoObjectType):
    class Meta:
        model = Order

# ==== INPUTS ====
class CustomerInput(graphene.InputObjectType):
    name = graphene.String(required=True)
    email = graphene.String(required=True)
    phone = graphene.String()

class ProductInput(graphene.InputObjectType):
    name = graphene.String(required=True)
    price = graphene.Float(required=True)
    stock = graphene.Int()

class OrderInput(graphene.InputObjectType):
    customer_id = graphene.ID(required=True)
    product_ids = graphene.List(graphene.ID, required=True)

# ==== MUTATIONS ====
class CreateCustomer(graphene.Mutation):
    class Arguments:
        input = CustomerInput(required=True)

    customer = graphene.Field(CustomerType)
    message = graphene.String()

    def mutate(self, info, input):
        if Customer.objects.filter(email=input.email).exists():
            raise Exception("Email already exists")
        if input.phone and not re.match(r'^(\+?\d{10,15}|\d{3}-\d{3}-\d{4})$', input.phone):
            raise Exception("Invalid phone format")
        customer = Customer.objects.create(**input)
        return CreateCustomer(customer=customer, message="Customer created successfully")

class BulkCreateCustomers(graphene.Mutation):
    class Arguments:
        input = graphene.List(CustomerInput, required=True)

    customers = graphene.List(CustomerType)
    errors = graphene.List(graphene.String)

    def mutate(self, info, input):
        customers, errors = [], []
        with transaction.atomic():
            for data in input:
                try:
                    if Customer.objects.filter(email=data.email).exists():
                        raise Exception(f"Email already exists: {data.email}")
                    customer = Customer.objects.create(**data)
                    customers.append(customer)
                except Exception as e:
                    errors.append(str(e))
        return BulkCreateCustomers(customers=customers, errors=errors)

class CreateProduct(graphene.Mutation):
    class Arguments:
        input = ProductInput(required=True)

    product = graphene.Field(ProductType)

    def mutate(self, info, input):
        if input.price <= 0:
            raise Exception("Price must be positive")
        if input.stock is not None and input.stock < 0:
            raise Exception("Stock cannot be negative")
        product = Product.objects.create(**input)
        return CreateProduct(product=product)

class CreateOrder(graphene.Mutation):
    class Arguments:
        input = OrderInput(required=True)

    order = graphene.Field(OrderType)

    def mutate(self, info, input):
        try:
            customer = Customer.objects.get(pk=input.customer_id)
        except Customer.DoesNotExist:
            raise Exception("Invalid customer ID")
        products = Product.objects.filter(pk__in=input.product_ids)
        if not products.exists():
            raise Exception("No valid products found")
        total_amount = sum([p.price for p in products])
        order = Order.objects.create(customer=customer, total_amount=total_amount)
        order.products.set(products)
        return CreateOrder(order=order)

# ==== QUERIES ====
class Query(graphene.ObjectType):
    all_customers = DjangoFilterConnectionField(CustomerType, filterset_class=CustomerFilter, order_by=graphene.List(of_type=graphene.String))
    all_products = DjangoFilterConnectionField(ProductType, filterset_class=ProductFilter, order_by=graphene.List(of_type=graphene.String))
    all_orders = DjangoFilterConnectionField(OrderType, filterset_class=OrderFilter, order_by=graphene.List(of_type=graphene.String))
    
    customers = graphene.List(CustomerType)
    products = graphene.List(ProductType)
    orders = graphene.List(OrderType)

    def resolve_all_customers(self, info): return Customer.objects.all()
    def resolve_all_products(self, info): return Product.objects.all()
    def resolve_all_orders(self, info): return Order.objects.all()

# ==== ROOT MUTATION ====
class Mutation(graphene.ObjectType):
    create_customer = CreateCustomer.Field()
    bulk_create_customers = BulkCreateCustomers.Field()
    create_product = CreateProduct.Field()
    create_order = CreateOrder.Field()

    createCustomer = CreateCustomer.Field()
    bulkCreateCustomers = BulkCreateCustomers.Field()
    createProduct = CreateProduct.Field()
    createOrder = CreateOrder.Field()


class Query(graphene.ObjectType):
    hello = graphene.String(default_value = "Hello, GraphQL!")

schema = graphene.Schema(query=Query)


class ProductType(graphene.ObjectType):
    id = graphene.ID()
    name = graphene.String()
    stock = graphene.Int()

class UpdateLowStockProducts(graphene.Mutation):
    success = graphene.String()
    updated_products = graphene.List(ProductType)

    def mutate(self, info):
        low_stock = Product.objects.filter(stock__lt=10)
        updated = []
        for p in low_stock:
            p.stock += 10
            p.save()
            updated.append(p)
        return UpdateLowStockProducts(success="Restocked successfully", updated_products=updated)

class Mutation(graphene.ObjectType):
    update_low_stock_products = UpdateLowStockProducts.Field()
