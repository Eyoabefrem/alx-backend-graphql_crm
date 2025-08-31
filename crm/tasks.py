import datetime, requests
from celery import shared_task
from datetime import datetime
import requests


@shared_task
def generate_crm_report():
    query = """
    query {
      totalCustomers
      totalOrders
      totalRevenue
    }
    """
    resp = requests.post("http://localhost:8000/graphql", json={"query": query})
    data = resp.json()["data"]

    with open("/tmp/crm_report_log.txt", "a") as f:
        f.write(f"{datetime.datetime.now()} - Report: {data['totalCustomers']} customers, {data['totalOrders']} orders, {data['totalRevenue']} revenue\n")
    with open("/tmp/crm_report_log.txt", "a") as f:
        f.write(f"{datetime.now()} - Report: ...\n")