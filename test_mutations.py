
#!/usr/bin/env python3
"""
Test script for GraphQL mutations
This script tests all the required mutations from the checkpoint examples.
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

def test_create_customer():
    """Test creating a single customer"""
    print("Testing CreateCustomer mutation...")
    
    import random
    email = f"alice{random.randint(1000,9999)}@example.com"
    
    query = f"""
    mutation {{
      createCustomer(input: {{ name: "Alice", email: "{email}", phone: "+1234567890" }}) {{
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
    print(f"Result: {json.dumps(result, indent=2)}")
    
    if 'errors' in result:
        print("❌ CreateCustomer failed")
        return False
    else:
        print("✅ CreateCustomer succeeded")
        return True

def test_bulk_create_customers():
    """Test bulk creating customers"""
    print("\nTesting BulkCreateCustomers mutation...")
    
    import random
    email1 = f"bob{random.randint(1000,9999)}@example.com"
    email2 = f"carol{random.randint(1000,9999)}@example.com"
    
    query = f"""
    mutation {{
      bulkCreateCustomers(input: [
        {{ name: "Bob", email: "{email1}", phone: "123-456-7890" }},
        {{ name: "Carol", email: "{email2}" }}
      ]) {{
        customers {{
          id
          name
          email
        }}
        errors
      }}
    }}
    """
    
    result = send_graphql_request(query)
    print(f"Result: {json.dumps(result, indent=2)}")
    
    if 'errors' in result:
        print("❌ BulkCreateCustomers failed")
        return False
    else:
        print("✅ BulkCreateCustomers succeeded")
        return True

def test_create_product():
    """Test creating a product"""
    print("\nTesting CreateProduct mutation...")
    
    query = """
    mutation {
      createProduct(input: { name: "Laptop", price: 999.99, stock: 10 }) {
        product {
          id
          name
          price
          stock
        }
      }
    }
    """
    
    result = send_graphql_request(query)
    print(f"Result: {json.dumps(result, indent=2)}")
    
    if 'errors' in result:
        print("❌ CreateProduct failed")
        return False
    else:
        print("✅ CreateProduct succeeded")
        return True

def test_create_order():
    """Test creating an order with products"""
    print("\nTesting CreateOrder mutation...")
    
    query = """
    mutation {
      createOrder(input: { customerId: "1", productIds: ["1"] }) {
        order {
          id
          customer {
            name
          }
          products {
            name
            price
          }
          totalAmount
          orderDate
        }
      }
    }
    """
    
    result = send_graphql_request(query)
    print(f"Result: {json.dumps(result, indent=2)}")
    
    if 'errors' in result:
        print("❌ CreateOrder failed")
        return False
    else:
        print("✅ CreateOrder succeeded")
        return True

if __name__ == "__main__":
    print("Starting GraphQL mutation tests...")
    print("=" * 50)
    
    # Test all mutations
    tests = [
        test_create_customer,
        test_bulk_create_customers,
        test_create_product,
        test_create_order
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        try:
            if test():
                passed += 1
        except Exception as e:
            print(f"❌ Test failed with exception: {e}")
    
    print("\n" + "=" * 50)
    print(f"Tests completed: {passed}/{total} passed")
    
    if passed == total:
        print("🎉 All tests passed! Your GraphQL mutations are working correctly.")
    else:
        print("⚠️  Some tests failed. Please check the implementation.")
