#!/usr/bin/env python3
"""
Task 2 Verification: Complex GraphQL Mutations for CRM
This script verifies all requirements from Task 2 are met.
"""

import requests
import json
import os
import sys

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

def verify_create_customer():
    """Verify CreateCustomer mutation meets all requirements"""
    print("🔍 Verifying CreateCustomer mutation...")
    
    import random
    email = f"customer{random.randint(1000,9999)}@example.com"
    
    # Test with all required fields and optional phone
    query = f"""
    mutation {{
      createCustomer(input: {{ name: "John Doe", email: "{email}", phone: "+1234567890" }}) {{
        customer {{
          id
          name
          email
          phone
        }}
        message
      }}
    }}
    """
    
    result = send_graphql_request(query)
    
    success = True
    issues = []
    
    # Check if mutation exists and works
    if 'errors' in result:
        success = False
        issues.append("CreateCustomer mutation failed")
    
    # Check return structure
    data = result.get('data', {}).get('createCustomer', {})
    if not data.get('customer'):
        success = False
        issues.append("Missing customer object in response")
    
    if not data.get('message'):
        success = False
        issues.append("Missing success message in response")
    
    # Verify customer fields
    customer = data.get('customer', {})
    if not all([customer.get('id'), customer.get('name'), customer.get('email')]):
        success = False
        issues.append("Missing required customer fields")
    
    print(f"Result: {json.dumps(result, indent=2)}")
    
    if success:
        print("✅ CreateCustomer meets requirements")
    else:
        print(f"❌ CreateCustomer issues: {', '.join(issues)}")
    
    return success

def verify_bulk_create_customers():
    """Verify BulkCreateCustomers mutation meets all requirements"""
    print("\n🔍 Verifying BulkCreateCustomers mutation...")
    
    import random
    email1 = f"bulk1_{random.randint(1000,9999)}@example.com"
    email2 = f"bulk2_{random.randint(1000,9999)}@example.com"
    
    # Test bulk creation with partial success scenario
    query = f"""
    mutation {{
      bulkCreateCustomers(input: [
        {{ name: "Valid Customer 1", email: "{email1}", phone: "+1234567890" }},
        {{ name: "Valid Customer 2", email: "{email2}" }},
        {{ name: "Invalid Customer", email: "invalid@test.com", phone: "bad-phone" }}
      ]) {{
        customers {{
          id
          name
          email
          phone
        }}
        errors
      }}
    }}
    """
    
    result = send_graphql_request(query)
    
    success = True
    issues = []
    
    # Check if mutation exists and works
    if 'errors' in result:
        success = False
        issues.append("BulkCreateCustomers mutation failed")
    
    # Check return structure
    data = result.get('data', {}).get('bulkCreateCustomers', {})
    if not isinstance(data.get('customers'), list):
        success = False
        issues.append("Missing customers list in response")
    
    if not isinstance(data.get('errors'), list):
        success = False
        issues.append("Missing errors list in response")
    
    # Check partial success (some customers created, some errors)
    customers = data.get('customers', [])
    errors = data.get('errors', [])
    
    if len(customers) < 2:
        success = False
        issues.append("Partial success not working - should create valid customers")
    
    if len(errors) == 0:
        success = False
        issues.append("Error handling not working - should report invalid phone")
    
    print(f"Result: {json.dumps(result, indent=2)}")
    
    if success:
        print("✅ BulkCreateCustomers meets requirements (partial success working)")
    else:
        print(f"❌ BulkCreateCustomers issues: {', '.join(issues)}")
    
    return success

def verify_create_product():
    """Verify CreateProduct mutation meets all requirements"""
    print("\n🔍 Verifying CreateProduct mutation...")
    
    import random
    product_name = f"Product_{random.randint(1000,9999)}"
    
    # Test with all fields including default stock
    query = f"""
    mutation {{
      createProduct(input: {{ name: "{product_name}", price: 299.99, stock: 50 }}) {{
        product {{
          id
          name
          price
          stock
        }}
      }}
    }}
    """
    
    result = send_graphql_request(query)
    
    success = True
    issues = []
    
    # Check if mutation exists and works
    if 'errors' in result:
        success = False
        issues.append("CreateProduct mutation failed")
    
    # Check return structure
    data = result.get('data', {}).get('createProduct', {})
    if not data.get('product'):
        success = False
        issues.append("Missing product object in response")
    
    # Verify product fields
    product = data.get('product', {})
    if not all([product.get('id'), product.get('name'), product.get('price') is not None]):
        success = False
        issues.append("Missing required product fields")
    
    # Test default stock behavior
    query_default_stock = f"""
    mutation {{
      createProduct(input: {{ name: "DefaultStock_{random.randint(1000,9999)}", price: 199.99 }}) {{
        product {{
          id
          name
          price
          stock
        }}
      }}
    }}
    """
    
    result_default = send_graphql_request(query_default_stock)
    default_product = result_default.get('data', {}).get('createProduct', {}).get('product', {})
    
    if default_product.get('stock') != 0:
        success = False
        issues.append("Default stock should be 0")
    
    print(f"Result: {json.dumps(result, indent=2)}")
    print(f"Default stock test: {json.dumps(result_default, indent=2)}")
    
    if success:
        print("✅ CreateProduct meets requirements")
    else:
        print(f"❌ CreateProduct issues: {', '.join(issues)}")
    
    return success

def verify_create_order():
    """Verify CreateOrder mutation meets all requirements"""
    print("\n🔍 Verifying CreateOrder mutation...")
    
    # First, ensure we have a customer and product
    import random
    order_email = f"order{random.randint(1000,9999)}@test.com"
    
    customer_query = f"""
    mutation {{
      createCustomer(input: {{ name: "Order Customer", email: "{order_email}" }}) {{
        customer {{
          id
        }}
      }}
    }}
    """
    
    product_query = f"""
    mutation {{
      createProduct(input: {{ name: "Order Product", price: 99.99, stock: 10 }}) {{
        product {{
          id
        }}
      }}
    }}
    """
    
    customer_result = send_graphql_request(customer_query)
    product_result = send_graphql_request(product_query)
    
    # Check if results are valid before accessing
    if 'errors' in customer_result or 'errors' in product_result:
        print(f"Error creating customer or product: {customer_result}, {product_result}")
        return False
        
    customer_data = customer_result.get('data', {}).get('createCustomer', {})
    product_data = product_result.get('data', {}).get('createProduct', {})
    
    if not customer_data or not product_data:
        print("Failed to create customer or product for order test")
        return False
    
    customer_obj = customer_data.get('customer', {})
    product_obj = product_data.get('product', {})
    
    if not customer_obj or not product_obj:
        print("Invalid customer or product data for order test")
        return False
        
    customer_id = customer_obj['id']
    product_id = product_obj['id']
    
    # Now test order creation
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
    
    result = send_graphql_request(order_query)
    
    success = True
    issues = []
    
    # Check if mutation exists and works
    if 'errors' in result:
        success = False
        issues.append("CreateOrder mutation failed")
    
    # Check return structure
    data = result.get('data', {}).get('createOrder', {})
    if not data.get('order'):
        success = False
        issues.append("Missing order object in response")
    
    # Verify nested customer and product data
    order = data.get('order', {})
    customer = order.get('customer', {})
    products = order.get('products', [])
    
    if not customer.get('name') or not customer.get('email'):
        success = False
        issues.append("Missing nested customer details")
    
    if not products or not products[0].get('name') or products[0].get('price') is None:
        success = False
        issues.append("Missing nested product details")
    
    # Verify total amount calculation
    if order.get('totalAmount') != 99.99:
        success = False
        issues.append("Total amount calculation incorrect")
    
    # Verify order date is present
    if not order.get('orderDate'):
        success = False
        issues.append("Missing order date")
    
    print(f"Result: {json.dumps(result, indent=2)}")
    
    if success:
        print("✅ CreateOrder meets requirements (nested objects, total calculation)")
    else:
        print(f"❌ CreateOrder issues: {', '.join(issues)}")
    
    return success

def verify_error_handling():
    """Verify error handling meets requirements"""
    print("\n🔍 Verifying error handling...")
    
    success = True
    issues = []
    
    # Test duplicate email error
    email = "duplicate@error-test.com"
    
    # Create first customer
    create_query = f"""
    mutation {{
      createCustomer(input: {{ name: "First", email: "{email}" }}) {{
        customer {{ id }}
      }}
    }}
    """
    send_graphql_request(create_query)
    
    # Try duplicate
    duplicate_query = f"""
    mutation {{
      createCustomer(input: {{ name: "Duplicate", email: "{email}" }}) {{
        customer {{ id }}
      }}
    }}
    """
    
    duplicate_result = send_graphql_request(duplicate_query)
    
    if not ('errors' in duplicate_result and 'Email already exists' in str(duplicate_result['errors'])):
        success = False
        issues.append("Email uniqueness validation not working")
    
    # Test invalid product ID in order
    invalid_order_query = """
    mutation {
      createOrder(input: { customerId: "999999", productIds: ["999999"] }) {
        order { id }
      }
    }
    """
    
    invalid_result = send_graphql_request(invalid_order_query)
    
    if not ('errors' in invalid_result and 'Invalid' in str(invalid_result['errors'])):
        success = False
        issues.append("Invalid ID validation not working")
    
    print("Error handling tests completed")
    
    if success:
        print("✅ Error handling meets requirements (user-friendly messages)")
    else:
        print(f"❌ Error handling issues: {', '.join(issues)}")
    
    return success

def verify_schema_integration():
    """Verify schema integration meets requirements"""
    print("\n🔍 Verifying schema integration...")
    
    # Test introspection to verify all mutations are available
    introspection_query = """
    query {
      __schema {
        mutationType {
          fields {
            name
          }
        }
      }
    }
    """
    
    result = send_graphql_request(introspection_query)
    
    success = True
    issues = []
    
    if 'errors' in result:
        success = False
        issues.append("Schema introspection failed")
        return success
    
    mutation_fields = [field['name'] for field in result['data']['__schema']['mutationType']['fields']]
    
    # GraphQL convention uses camelCase, but we also have snake_case versions
    required_mutations = ['createCustomer', 'bulkCreateCustomers', 'createProduct', 'createOrder']
    
    for mutation in required_mutations:
        if mutation not in mutation_fields:
            success = False
            issues.append(f"Missing mutation: {mutation}")
    
    print(f"Available mutations: {mutation_fields}")
    
    if success:
        print("✅ Schema integration meets requirements (all mutations available)")
    else:
        print(f"❌ Schema integration issues: {', '.join(issues)}")
    
    return success

def main():
    """Run all Task 2 verification tests"""
    print("=" * 80)
    print("TASK 2 VERIFICATION: Complex GraphQL Mutations for CRM")
    print("=" * 80)
    
    # Start server for testing
    import subprocess
    import time
    import signal
    
    print("Starting Django server for testing...")
    server_process = subprocess.Popen(
        ['python', 'manage.py', 'runserver', '--noreload'],
        cwd='/home/minab/Desktop/alx-backend-graphql_crm',
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )
    
    time.sleep(5)  # Wait for server to start
    
    try:
        tests = [
            verify_schema_integration,
            verify_create_customer,
            verify_bulk_create_customers, 
            verify_create_product,
            verify_create_order,
            verify_error_handling
        ]
        
        passed = 0
        total = len(tests)
        
        for test in tests:
            try:
                if test():
                    passed += 1
            except Exception as e:
                print(f"❌ Test failed with exception: {e}")
        
        print("\n" + "=" * 80)
        print(f"TASK 2 VERIFICATION RESULTS: {passed}/{total} passed")
        
        if passed == total:
            print("🎉 ALL REQUIREMENTS MET! Your CRM GraphQL mutations are fully compliant with Task 2.")
            print("\nImplemented features:")
            print("✅ CreateCustomer with validation and success message")
            print("✅ BulkCreateCustomers with partial success support")
            print("✅ CreateProduct with price/stock validation")
            print("✅ CreateOrder with nested objects and total calculation")
            print("✅ Comprehensive error handling with user-friendly messages")
            print("✅ Proper schema integration in main GraphQL schema")
        else:
            print("⚠️  Some requirements not fully met. Please review the issues above.")
    
    finally:
        # Kill the server
        server_process.terminate()
        server_process.wait()

if __name__ == "__main__":
    import random
    main()