from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse, HttpResponseRedirect

from djczech.reconciliation.data.models import Cheque

from djzbar.utils.informix import get_session
from djtools.utils.convert import str_to_class

from datetime import datetime

EARL = settings.INFORMIX_EARL

