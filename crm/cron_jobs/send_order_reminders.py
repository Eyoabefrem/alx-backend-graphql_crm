
#!/usr/bin/env python3
import requests, datetime
from gql import gql, Client
from gql.transport.requests import RequestsHTTPTransport

transport = RequestsHTTPTransport(
    url="http://localhost:8000/graphql",
    verify=True,
    retries=3,
)

client = Client(transport=transport, fetch_schema_from_transport=True)
query = """
query RecentOrders {
  orders(orderDate_Gte: "%s") {
    id
    customer {
      email
    }
  }
}
""" % ( (datetime.datetime.now() - datetime.timedelta(days=7)).date() )

resp = requests.post(
    "http://localhost:8000/graphql",
    json={"query": query}
)

orders = resp.json().get("data", {}).get("orders", [])

with open("/tmp/order_reminders_log.txt", "a") as f:
    for o in orders:
        f.write(f"{datetime.datetime.now()} - Order {o['id']} for {o['customer']['email']}\n")

print("Order reminders processed!")
