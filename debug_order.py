#!/usr/bin/env python3
"""
Debug script for CreateOrder mutation
"""

import requests
import json
import os
import sys
import random

# Add the project root directory to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'alx_backend_graphql.settings')

import django
django.setup()

def send_graphql_request(query, variables=None):
    """Send a GraphQL request to the server"""
    url = 'http://127.0.0.1:8000/graphql'
    payload = {
        'query': query,
        'variables': variables or {}
    }
    
    headers = {
        'Content-Type': 'application/json',
    }
    
    response = requests.post(url, json=payload, headers=headers)
    return response.json()

def debug_create_order():
    """Debug CreateOrder mutation step by step"""
    print("🔧 Debugging CreateOrder mutation...")
    
    # Step 1: Create customer
    order_email = f"debug_order{random.randint(1000,9999)}@test.com"
    print(f"Creating customer with email: {order_email}")
    
    customer_query = f"""
    mutation {{
      createCustomer(input: {{ name: "Debug Order Customer", email: "{order_email}" }}) {{
        customer {{
          id
          name
          email
        }}
        message
      }}
    }}
    """
    
    customer_result = send_graphql_request(customer_query)
    print(f"Customer creation result: {json.dumps(customer_result, indent=2)}")
    
    if 'errors' in customer_result:
        print("❌ Failed to create customer")
        return False
    
    customer_data = customer_result.get('data', {}).get('createCustomer', {})
    if not customer_data:
        print("❌ No customer data in response")
        return False
        
    customer_obj = customer_data.get('customer', {})
    if not customer_obj:
        print("❌ No customer object in response")
        return False
        
    customer_id = customer_obj.get('id')
    print(f"✅ Customer created with ID: {customer_id}")
    
    # Step 2: Create product
    print("Creating product...")
    
    product_query = f"""
    mutation {{
      createProduct(input: {{ name: "Debug Order Product", price: 149.99, stock: 5 }}) {{
        product {{
          id
          name
          price
          stock
        }}
      }}
    }}
    """
    
    product_result = send_graphql_request(product_query)
    print(f"Product creation result: {json.dumps(product_result, indent=2)}")
    
    if 'errors' in product_result:
        print("❌ Failed to create product")
        return False
    
    product_data = product_result.get('data', {}).get('createProduct', {})
    if not product_data:
        print("❌ No product data in response")
        return False
        
    product_obj = product_data.get('product', {})
    if not product_obj:
        print("❌ No product object in response")
        return False
        
    product_id = product_obj.get('id')
    print(f"✅ Product created with ID: {product_id}")
    
    # Step 3: Create order
    print(f"Creating order with customer ID: {customer_id}, product ID: {product_id}")
    
    order_query = f"""
    mutation {{
      createOrder(input: {{ customerId: "{customer_id}", productIds: ["{product_id}"] }}) {{
        order {{
          id
          customer {{
            name
            email
          }}
          products {{
            name
            price
          }}
          totalAmount
          orderDate
        }}
      }}
    }}
    """
    
    order_result = send_graphql_request(order_query)
    print(f"Order creation result: {json.dumps(order_result, indent=2)}")
    
    if 'errors' in order_result:
        print("❌ Failed to create order")
        return False
    
    order_data = order_result.get('data', {}).get('createOrder', {})
    if not order_data:
        print("❌ No order data in response")
        return False
        
    order_obj = order_data.get('order', {})
    if not order_obj:
        print("❌ No order object in response")
        return False
    
    print("✅ Order created successfully!")
    print(f"Order details: {json.dumps(order_obj, indent=2)}")
    
    return True

if __name__ == "__main__":
    # Start server
    import subprocess
    import time
    
    print("Starting Django server for debugging...")
    server_process = subprocess.Popen(
        ['python', 'manage.py', 'runserver', '--noreload'],
        cwd='/home/minab/Desktop/alx-backend-graphql_crm',
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )
    
    time.sleep(5)  # Wait for server to start
    
    try:
        success = debug_create_order()
        if success:
            print("\n🎉 CreateOrder debugging completed successfully!")
        else:
            print("\n❌ CreateOrder debugging failed!")
    finally:
        # Kill the server
        server_process.terminate()
        server_process.wait()