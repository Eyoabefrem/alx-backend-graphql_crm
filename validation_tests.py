
#!/usr/bin/env python3
"""
Validation tests for GraphQL mutations
This script tests edge cases and validation requirements.
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

def test_duplicate_email_validation():
    """Test that duplicate email validation works"""
    print("Testing duplicate email validation...")
    
    # First create a customer
    query1 = """
    mutation {
      createCustomer(input: { name: "Test User", email: "test@duplicate.com" }) {
        customer {
          id
          email
        }
        message
      }
    }
    """
    
    result1 = send_graphql_request(query1)
    
    # Try to create another with same email
    query2 = """
    mutation {
      createCustomer(input: { name: "Another User", email: "test@duplicate.com" }) {
        customer {
          id
          email
        }
        message
      }
    }
    """
    
    result2 = send_graphql_request(query2)
    print(f"Duplicate email test result: {json.dumps(result2, indent=2)}")
    
    if 'errors' in result2 and 'Email already exists' in str(result2['errors']):
        print("✅ Duplicate email validation works")
        return True
    else:
        print("❌ Duplicate email validation failed")
        return False

def test_phone_format_validation():
    """Test phone format validation"""
    print("\nTesting phone format validation...")
    
    # Test with invalid phone format
    query = """
    mutation {
      createCustomer(input: { name: "Test User", email: "test@phone.com", phone: "invalid-phone" }) {
        customer {
          id
        }
        message
      }
    }
    """
    
    result = send_graphql_request(query)
    print(f"Invalid phone test result: {json.dumps(result, indent=2)}")
    
    if 'errors' in result and 'Invalid phone number format' in str(result['errors']):
        print("✅ Phone format validation works")
        return True
    else:
        print("❌ Phone format validation failed")
        return False

def test_product_price_validation():
    """Test product price validation"""
    print("\nTesting product price validation...")
    
    # Test with negative price
    query = """
    mutation {
      createProduct(input: { name: "Invalid Product", price: -10.0 }) {
        product {
          id
        }
      }
    }
    """
    
    result = send_graphql_request(query)
    print(f"Negative price test result: {json.dumps(result, indent=2)}")
    
    if 'errors' in result and 'Price must be positive' in str(result['errors']):
        print("✅ Price validation works")
        return True
    else:
        print("❌ Price validation failed")
        return False

def test_product_stock_validation():
    """Test product stock validation"""
    print("\nTesting product stock validation...")
    
    # Test with negative stock
    query = """
    mutation {
      createProduct(input: { name: "Invalid Stock Product", price: 10.0, stock: -5 }) {
        product {
          id
        }
      }
    }
    """
    
    result = send_graphql_request(query)
    print(f"Negative stock test result: {json.dumps(result, indent=2)}")
    
    if 'errors' in result and 'Stock cannot be negative' in str(result['errors']):
        print("✅ Stock validation works")
        return True
    else:
        print("❌ Stock validation failed")
        return False

def test_order_invalid_customer():
    """Test order creation with invalid customer ID"""
    print("\nTesting order with invalid customer ID...")
    
    query = """
    mutation {
      createOrder(input: { customerId: "999999", productIds: ["1"] }) {
        order {
          id
        }
      }
    }
    """
    
    result = send_graphql_request(query)
    print(f"Invalid customer ID test result: {json.dumps(result, indent=2)}")
    
    if 'errors' in result and 'Invalid customer ID' in str(result['errors']):
        print("✅ Invalid customer ID validation works")
        return True
    else:
        print("❌ Invalid customer ID validation failed")
        return False

def test_order_empty_products():
    """Test order creation with empty product list"""
    print("\nTesting order with empty product list...")
    
    query = """
    mutation {
      createOrder(input: { customerId: "1", productIds: [] }) {
        order {
          id
        }
      }
    }
    """
    
    result = send_graphql_request(query)
    print(f"Empty products test result: {json.dumps(result, indent=2)}")
    
    if 'errors' in result and 'At least one product must be selected' in str(result['errors']):
        print("✅ Empty products validation works")
        return True
    else:
        print("❌ Empty products validation failed")
        return False

def test_bulk_create_partial_success():
    """Test bulk create with partial success (some valid, some invalid)"""
    print("\nTesting bulk create partial success...")
    
    import random
    valid_email = f"valid{random.randint(1000,9999)}@example.com"
    
    query = f"""
    mutation {{
      bulkCreateCustomers(input: [
        {{ name: "Valid User", email: "{valid_email}" }},
        {{ name: "Invalid User", email: "duplicate@test.com", phone: "invalid-phone" }}
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
    print(f"Bulk create partial success result: {json.dumps(result, indent=2)}")
    
    data = result.get('data', {}).get('bulkCreateCustomers', {})
    if len(data.get('customers', [])) > 0 and len(data.get('errors', [])) > 0:
        print("✅ Bulk create partial success works")
        return True
    else:
        print("❌ Bulk create partial success failed")
        return False

if __name__ == "__main__":
    print("Starting GraphQL validation tests...")
    print("=" * 60)
    
    # Test all validations
    tests = [
        test_duplicate_email_validation,
        test_phone_format_validation,
        test_product_price_validation,
        test_product_stock_validation,
        test_order_invalid_customer,
        test_order_empty_products,
        test_bulk_create_partial_success
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        try:
            if test():
                passed += 1
        except Exception as e:
            print(f"❌ Test failed with exception: {e}")
    
    print("\n" + "=" * 60)
    print(f"Validation tests completed: {passed}/{total} passed")
    
    if passed == total:
        print("🎉 All validation tests passed! Your GraphQL mutations handle edge cases correctly.")
    else:
        print("⚠️  Some validation tests failed. Please check the implementation.")
