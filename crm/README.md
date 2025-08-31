Install Redis

Run python manage.py migrate

Start worker: celery -A crm worker -l info

Start beat: celery -A crm beat -l info

Logs: /tmp/crm_report_log.txt