# ALX Backend GraphQL CRM

A Customer Relationship Management (CRM) system built with **Django** and **GraphQL** using **graphene-django**.  
This project demonstrates building a flexible API with GraphQL, supporting queries, mutations, filtering, and nested relationships for customers, products, and orders.

---

## Table of Contents

- [Features](#features)
- [Tech Stack](#tech-stack)
- [Setup](#setup)
- [Running the Server](#running-the-server)
- [GraphQL Endpoint](#graphql-endpoint)
- [Available Mutations](#available-mutations)
- [Available Queries](#available-queries)
- [Filtering](#filtering)
- [License](#license)

---

## Features

- GraphQL API with a single endpoint
- CRUD operations for Customers, Products, and Orders
- Bulk customer creation
- Nested order creation with multiple products
- Input validation and error handling
- Filtering and pagination using Django filters and Relay
- Relay-style connections (`edges { node { ... } }`) for all lists

---

## Tech Stack

- Python 3.12
- Django 5.2
- graphene-django
- django-filter
- SQLite (default, can use PostgreSQL)
- GraphiQL for API testing

---

## Setup

1. Clone the repository:

```bash
git clone https://github.com/your-username/alx-backend-graphql_crm.git
cd alx-backend-graphql_crm
````

2. Create a virtual environment:

```bash
python -m venv venv
```

3. Activate the virtual environment:

* Windows:

```bash
venv\Scripts\activate
```

* macOS/Linux:

```bash
source venv/bin/activate
```

4. Install dependencies:

```bash
pip install -r requirements.txt
```

5. Apply migrations:

```bash
python manage.py migrate
```

---

## Running the Server

```bash
python manage.py runserver
```

The server will run at: `http://127.0.0.1:8000/`

---

## GraphQL Endpoint

Access the GraphQL playground (GraphiQL) at:

```
http://127.0.0.1:8000/graphql
```

---

## Available Mutations

### Create a Single Customer

```graphql
mutation {
  createCustomer(input: { name: "Alice", email: "alice@example.com", phone: "+1234567890" }) {
    customer {
      id
      name
      email
      phone
    }
    message
  }
}
```

### Bulk Create Customers

```graphql
mutation {
  bulkCreateCustomers(customers: [
    { name: "Bob", email: "bob@example.com", phone: "123-456-7890" },
    { name: "Carol", email: "carol@example.com" }
  ]) {
    customers {
      id
      name
      email
    }
    errors
  }
}
```

### Create a Product

```graphql
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
```

### Create an Order

```graphql
mutation {
  createOrder(input: { customerId: "1", productIds: ["1", "2"] }) {
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
```

---

## Available Queries

### List All Customers

```graphql
query {
  allCustomers {
    edges {
      node {
        id
        name
        email
        phone
      }
    }
  }
}
```

### List All Products

```graphql
query {
  allProducts {
    edges {
      node {
        id
        name
        price
        stock
      }
    }
  }
}
```

### List All Orders

```graphql
query {
  allOrders {
    edges {
      node {
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
}
```

---

## Filtering

Filters are available on all list queries using DjangoFilterConnectionField.

Example: Filter customers by name and creation date:

```graphql
query {
  allCustomers(name: "Alice", createdAtGte: "2025-01-01") {
    edges {
      node {
        id
        name
        email
        createdAt
      }
    }
  }
}
```

Filters are **camelCase** in GraphQL.

---