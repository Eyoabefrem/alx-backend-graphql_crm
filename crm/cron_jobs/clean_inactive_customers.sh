#!/bin/bash

# Navigate to Django project root (adjust if needed)
cd "$(dirname "$0")/../.."

# Run Django shell command to delete inactive customers
deleted_count=$(python3 manage.py shell -c "
from crm.models import Customer
from django.utils import timezone
from datetime import timedelta
one_year_ago = timezone.now() - timedelta(days=365)
qs = Customer.objects.filter(order__isnull=True, created_at__lt=one_year_ago)
count = qs.count()
qs.delete()
print(count)
")

# Log with timestamp
echo \"$(date '+%Y-%m-%d %H:%M:%S') - Deleted \$deleted_count customers\" >> /tmp/customer_cleanup_log.txt