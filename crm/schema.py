import re
import graphene
from graphene_django import DjangoObjectType
from .models import Customer, Product, Order
from django.core.exceptions import ValidationError
from django.db import transaction
from decimal import Decimal
from datetime import datetime
from django.utils import timezone
from .filters import CustomerFilter, ProductFilter, OrderFilter
from graphene_django.filter import DjangoFilterConnectionField

class CustomerType(DjangoObjectType):
    class Meta:
        model = Customer
        interfaces = (graphene.relay.Node,)  # Relay node for DjangoFilterConnectionField

class ProductType(DjangoObjectType):
    price = graphene.Float()  # Override to use Float instead of Decimal
    
    class Meta:
        model = Product
        interfaces = (graphene.relay.Node,)
        
    def resolve_price(self, info):
        return float(self.price)

class OrderType(DjangoObjectType):
    totalAmount = graphene.Float()
    orderDate = graphene.DateTime()
    products = graphene.List(ProductType)  # Override the default connection
    
    class Meta:
        model = Order
        # Remove relay interface to avoid connection issues
        # interfaces = (graphene.relay.Node,)
        
    def resolve_totalAmount(self, info):
        return float(self.total_amount)
        
    def resolve_orderDate(self, info):
        return self.order_date
        
    def resolve_products(self, info):
        return self.products.all()


# Define input types
class CustomerInput(graphene.InputObjectType):
    name = graphene.String(required=True)
    email = graphene.String(required=True)
    phone = graphene.String()

class CreateCustomerInput(graphene.InputObjectType):
    name = graphene.String(required=True)
    email = graphene.String(required=True)
    phone = graphene.String()

class CreateProductInput(graphene.InputObjectType):
    name = graphene.String(required=True)
    price = graphene.Float(required=True)
    stock = graphene.Int()

class CreateOrderInput(graphene.InputObjectType):
    customerId = graphene.ID(required=True)
    productIds = graphene.List(graphene.ID, required=True)
    orderDate = graphene.DateTime()


# CreateCustomer Mutation
class CreateCustomer(graphene.Mutation):
    class Arguments:
        input = CreateCustomerInput(required=True)

    customer = graphene.Field(CustomerType)
    message = graphene.String()

    def mutate(self, info, input):
        if Customer.objects.filter(email=input.email).exists():
            raise ValidationError("Email already exists")

        if input.phone and not re.match(r'^(\+\d{10,15}|\d{3}-\d{3}-\d{4})$', input.phone):
            raise ValidationError("Invalid phone number format")

        customer = Customer.objects.create(
            name=input.name,
            email=input.email,
            phone=input.phone
        )
        return CreateCustomer(customer=customer, message="Customer created successfully")


# BulkCreateCustomers Mutation
class BulkCreateCustomers(graphene.Mutation):
    class Arguments:
        input = graphene.List(graphene.NonNull(CustomerInput), required=True)

    customers = graphene.List(CustomerType)
    errors = graphene.List(graphene.String)

    def mutate(self, info, input):
        created_customers = []
        errors = []

        # Process each customer individually to support partial success
        for i, data in enumerate(input):
            try:
                # Check for duplicate email
                if Customer.objects.filter(email=data.email).exists():
                    errors.append(f"Customer {i+1}: Email already exists: {data.email}")
                    continue

                # Validate phone format
                if data.phone and not re.match(r'^(\+\d{10,15}|\d{3}-\d{3}-\d{4})$', data.phone):
                    errors.append(f"Customer {i+1}: Invalid phone format: {data.phone}")
                    continue

                # Create customer
                customer = Customer.objects.create(
                    name=data.name,
                    email=data.email,
                    phone=data.phone
                )
                created_customers.append(customer)

            except Exception as e:
                errors.append(f"Customer {i+1}: {str(e)}")

        return BulkCreateCustomers(customers=created_customers, errors=errors)


# CreateProduct Mutation
class CreateProduct(graphene.Mutation):
    class Arguments:
        input = CreateProductInput(required=True)

    product = graphene.Field(ProductType)

    def mutate(self, info, input):
        if Decimal(input.price) <= 0:
            raise ValidationError("Price must be positive")
        if input.stock is not None and input.stock < 0:
            raise ValidationError("Stock cannot be negative")

        product = Product.objects.create(
            name=input.name,
            price=input.price,
            stock=input.stock if input.stock is not None else 0
        )
        return CreateProduct(product=product)


# CreateOrder Mutation
class CreateOrder(graphene.Mutation):
    class Arguments:
        input = CreateOrderInput(required=True)

    order = graphene.Field(OrderType)

    def mutate(self, info, input):
        # Helper function to extract database ID from Node ID
        def get_database_id(node_id):
            try:
                # Try to decode as Node ID first
                from graphql_relay import from_global_id
                _, db_id = from_global_id(node_id)
                return int(db_id)
            except:
                # If that fails, assume it's already a database ID
                try:
                    return int(node_id)
                except ValueError:
                    raise ValidationError(f"Invalid ID format: {node_id}")
        
        # Validate customer ID
        try:
            customer_db_id = get_database_id(input.customerId)
            customer = Customer.objects.get(id=customer_db_id)
        except Customer.DoesNotExist:
            raise ValidationError("Invalid customer ID")
        except Exception as e:
            raise ValidationError(f"Invalid customer ID format: {str(e)}")

        # Validate product IDs
        if not input.productIds:
            raise ValidationError("At least one product must be selected")
        
        try:
            product_db_ids = [get_database_id(pid) for pid in input.productIds]
        except Exception as e:
            raise ValidationError(f"Invalid product ID format: {str(e)}")
            
        products = Product.objects.filter(id__in=product_db_ids)
        if not products.exists():
            raise ValidationError("No valid products found")
        if products.count() != len(input.productIds):
            raise ValidationError("Some product IDs are invalid")

        # Calculate total amount accurately
        total_amount = sum(p.price for p in products)

        # Create order with proper datetime handling
        order = Order.objects.create(
            customer=customer,
            total_amount=total_amount,
            order_date=input.orderDate or timezone.now()
        )
        order.products.set(products)

        return CreateOrder(order=order)


# Query
class Query(graphene.ObjectType):
    all_customers = DjangoFilterConnectionField(CustomerType, filterset_class=CustomerFilter)
    all_products = DjangoFilterConnectionField(ProductType, filterset_class=ProductFilter)
    # Remove all_orders from connection field since OrderType doesn't have relay interface
    # all_orders = DjangoFilterConnectionField(OrderType, filterset_class=OrderFilter)

    # Keep your old simple lists as well if you want
    customers = graphene.List(CustomerType)
    products = graphene.List(ProductType)
    orders = graphene.List(OrderType)

    def resolve_customers(self, info):
        return Customer.objects.all()

    def resolve_products(self, info):
        return Product.objects.all()

    def resolve_orders(self, info):
        return Order.objects.all()

# Mutation
class Mutation(graphene.ObjectType):
    create_customer = CreateCustomer.Field()
    bulk_create_customers = BulkCreateCustomers.Field() 
    create_product = CreateProduct.Field()
    create_order = CreateOrder.Field()
    
    # Also provide camelCase aliases for GraphQL compatibility
    createCustomer = CreateCustomer.Field()
    bulkCreateCustomers = BulkCreateCustomers.Field()
    createProduct = CreateProduct.Field()
    createOrder = CreateOrder.Field()
