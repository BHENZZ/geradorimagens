web: gunicorn app:app --bind 0.0.0.0:$PORT --workers 1 --threads 1 --timeout 600 --max-requests 50 --worker-class sync --preload --log-level info --access-logfile - --error-logfile -
