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

from datetime import date, datetime
from sqlalchemy import desc

import argparse

"""
Delete sample data
"""

STATUS="EYE"
EARL = settings.INFORMIX_EARL

# set up command-line options
description = """
Optional --test argument to display sample data
"""

parser = argparse.ArgumentParser(description=description)

parser.add_argument(
    "--test",
    action='store_true',
    help="Dry run?",
    dest="test"
)

def main():
    """
    main function
    """

    print EARL
    session = get_session(EARL)

    count = 1
    if test:
        cheques = session.query(Cheque).filter_by(jbstatus=STATUS).\
                order_by(desc(Cheque.jbseqno))
        for c in cheques:
            print "{}) {}".format(count, c.__dict__)
            count += 1
    else:
        rows = session.query(Cheque).filter_by(jbstatus=STATUS).\
            delete(synchronize_session="fetch")
        session.commit()
        print "{} cheques deleted".format(rows)

    # query
    session.close()


######################
# shell command line
######################

if __name__ == "__main__":
    args = parser.parse_args()
    test = args.test
    sys.exit(main())
