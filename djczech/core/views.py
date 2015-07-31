from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, HttpResponseRedirect

from djczech.reconciliation.data.models import Cheque

from djzbar.utils.informix import get_session

from djtools.utils.convert import str_to_class

from datetime import datetime

EARL = settings.INFORMIX_EARL

@csrf_exempt
@login_required
def set_val(request):
    """
    Ajax POST for to set a single name/value pair, used mostly for
    jquery xeditable and ajax updates

    Requires via POST:

    pk (primary key of object to be updated)
    name (database field)
    value
    model
    """

    message = "success"
    # name/value pair
    name = request.POST.get("name")
    value = request.POST.get("value")
    # check for date fields
    if name[-4:] == "date":
        value = datetime.strptime(value, "%Y-%m-%d %H:%M:%S")
    # primary key
    pk = request.POST.get("pk")
    # create our dictionary to hold name/value pairs
    dic = { name: value }
    try:
        model = str_to_class(
            "djczech.reconciliation.data.models", request.POST.get("model")
        )
        # database connection
        session = get_session(EARL)
        obj = session.query(model).filter_by(jbchkno=pk).first()
        if not obj:
            message = "No object found with primary key: {}".format(pk)
        else:
            # update existing object
            for key, value in dic.iteritems():
                setattr(obj, key, value)
            session.commit()
    except Exception, e:
        message = e

    session.close()

    return HttpResponse(
        message, content_type="text/plain; charset=utf-8"
    )

@csrf_exempt
def xeditable(request):
    field = request.POST.get("name")
    value = request.POST.get("value")
    cid = request.POST.get("cid")
    table = request.POST.get("table")
    dic = {field:value}
    #put_data( dic, table, cid )

    return HttpResponse(dic, content_type="text/plain; charset=utf-8")
