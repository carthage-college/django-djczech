# -*- coding: utf-8 -*-
import os, sys

# env
sys.path.append('/usr/lib/python2.7/dist-packages/')
sys.path.append('/usr/lib/python2.7/')
sys.path.append('/usr/local/lib/python2.7/dist-packages/')
sys.path.append('/data2/django_1.7/')
sys.path.append('/data2/django_projects/')
sys.path.append('/data2/django_third/')
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "djczech.settings")

from django.conf import settings

from djczech.reconciliation.data.models import Cheque
from djzbar.utils.informix import get_session
from djtools.fields import TODAY

from datetime import datetime

"""
simple select
"""

EARL = settings.INFORMIX_EARL

import_date = datetime.combine(
    TODAY, datetime.min.time()
)

def main():
    """
    main function
    """

    sql = """
        SELECT
            jbseqno, Min(ccreconjb_rec.jbimprt_date) AS crrntbatchdate
        FROM
            ccreconjb_rec
        WHERE
            jbimprt_date >= '{}'
        GROUP BY jbseqno
    """.format(import_date)

    print EARL
    session = get_session(EARL)
    count = 1
    objs = session.execute(sql)
    for o in objs:
        print "{}) {} {}".format(count, o.jbseqno, o.crrntbatchdate)
        count += 1
    # query
    session.close()


######################
# shell command line
######################

if __name__ == "__main__":
    sys.exit(main())
