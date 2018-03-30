rm service.log gunicorn.log flask_slow_fast_call.txt
gunicorn --log-level=debug --access-logfile gunicorn.log --access-logformat '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s" %(D)s' -t 4  -b :8000 -w 2 -k gthread --threads=10 flask_slow_fast_call:app >> service.log 2>&1
