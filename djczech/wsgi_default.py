import os
import time
import traceback
import signal
import sys

# python
sys.path.append('/data2/python_venv/2.7/djczech/lib/python2.7/')
sys.path.append('/data2/python_venv/2.7/djczech/lib/python2.7/site-packages/')
sys.path.append('/data2/python_venv/2.7/djczech/lib/django_projects/')
sys.path.append('/data2/python_venv/2.7/djczech/lib/django-djczech/')
# django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'djczech.settings')
os.environ.setdefault('PYTHON_EGG_CACHE', '')
os.environ.setdefault('TZ', 'America/Chicago')
# informix
os.environ['INFORMIXSERVER'] = ''
os.environ['DBSERVERNAME'] = ''
os.environ['INFORMIXDIR'] = ''
os.environ['ODBCINI'] = ''
os.environ['ONCONFIG'] = ''
os.environ['INFORMIXSQLHOSTS'] = ''
os.environ['LD_LIBRARY_PATH'] = '$INFORMIXDIR/lib:$INFORMIXDIR/lib/esql:$INFORMIXDIR/lib/tools:/usr/lib/apache2/modules:$INFORMIXDIR/lib/cli'
os.environ['LD_RUN_PATH'] = '$INFORMIXDIR/lib:$INFORMIXDIR/lib/esql:$INFORMIXDIR/lib/tools:/usr/lib/apache2/modules'
# wsgi
from django.core.wsgi import get_wsgi_application

# NOTE: remove the try/except in production
#application = get_wsgi_application()
try:
    application = get_wsgi_application()
except Exception:
    # Error loading applications
    if 'mod_wsgi' in sys.modules:
        traceback.print_exc()
        os.kill(os.getpid(), signal.SIGINT)
        time.sleep(2.5)
    exit(-1)
