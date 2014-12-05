import os, sys
# python
sys.path.append('/usr/lib/python2.7/')
sys.path.append('/usr/lib/python2.7/dist-packages/')
sys.path.append('/data2/django_1.7/')
sys.path.append('/data2/django_projects/')
sys.path.append('/data2/django_third/')
# django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "djczech.settings")
os.environ.setdefault("PYTHON_EGG_CACHE", "/var/cache/python/.python-eggs")
os.environ.setdefault("TZ", "America/Chicago")
# informix
os.environ['INFORMIXSERVER'] = 'wilson'
os.environ['DBSERVERNAME'] = 'wilson'
os.environ['INFORMIXDIR'] = '/opt/ibm/informix'
os.environ['ODBCINI'] = '/etc/odbc.ini'
os.environ['ONCONFIG'] = 'onconf.carstrain'
os.environ['INFORMIXSQLHOSTS'] = '/opt/ibm/informix/etc/sqlhosts'
os.environ['LD_LIBRARY_PATH'] = '$INFORMIXDIR/lib:$INFORMIXDIR/lib/esql:$INFORMIXDIR/lib/tools:/usr/lib/apache2/modules:$INFORMIXDIR/lib/cli'
os.environ['LD_RUN_PATH'] = '/opt/ibm/informix/lib:/opt/ibm/informix/lib/esql:/opt/ibm/informix/lib/tools:/usr/lib/apache2/modules'
# wsgi
from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()

