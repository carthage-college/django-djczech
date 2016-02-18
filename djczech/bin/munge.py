# -*- coding: utf-8 -*-
import os
import sys
import argparse

# env
sys.path.append('/usr/lib/python2.7/dist-packages/')
sys.path.append('/usr/lib/python2.7/')
sys.path.append('/usr/local/lib/python2.7/dist-packages/')
sys.path.append('/data2/django_1.8/')
sys.path.append('/data2/django_projects/')
sys.path.append('/data2/django_third/')
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "djczech.settings")

from django.conf import settings

from djczech.reconciliation.data.models import Cheque
from djzbar.utils.informix import get_session
from djtools.fields import TODAY

from datetime import date, datetime
from itertools import islice

from sqlalchemy import exc


"""
Shell script that munges CSV data
"""

import csv

EARL = settings.INFORMIX_EARL

# set up command-line options
desc = """
Accepts as input a CSV file
"""

parser = argparse.ArgumentParser(description=desc)

parser.add_argument(
    "-f", "--file",
    help="File name.",
    dest="phile"
)
parser.add_argument(
    "-d", "--date",
    help="Import date format: 1891-05-01",
    dest="date"
)
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

    # convert date to datetime
    import_date = datetime.strptime(date, "%Y-%m-%d")
    print "import_date = {}".format(import_date)

    # for some reason we set jbpayee equal to the import date
    # plus user info
    jbpayee = "{}_{}".format(
        TODAY, settings.ADMINS[0][0]
    )
    # CSV headers
    fieldnames = (
        "jbstatus_date", "jbstatus", "jbamount",
        "jbaccount", "jbchkno", "jbpayee"
    )

    # remove all lines up to and including the headers line
    with open(phile, "r") as f:
        n = 0
        for line in f.readlines():
            n += 1
            if 'As of date' in line: # line in which field names was found
                break
        f.close()
        f = islice(open(phile, "r"), n, None)

        # read the CSV file
        reader = csv.DictReader(f, fieldnames, delimiter=',')

    # create database session
    if test:
        print EARL
        print settings.IMPORT_STATUS

    session = get_session(EARL)
    session.autoflush = False
    x = 0
    for r in reader:
        # convert amount from string to float and strip dollar sign
        try:
            jbamount = float(r["jbamount"][1:].replace(',',''))
        except:
            jbamount = 0

        # status date
        try:
            jbstatus_date = datetime.strptime(
                r["jbstatus_date"], "%m/%d/%Y"
            )
        except:
            jbstatus_date = None

        # check number
        try:
            cheque_number = int(r["jbchkno"])
        except:
            cheque_number = 0

        # create a Cheque object
        cheque = Cheque(
            jbimprt_date=import_date,
            jbstatus_date=jbstatus_date,
            jbchkno=cheque_number, jbchknolnk=cheque_number,
            jbstatus=settings.IMPORT_STATUS, jbaction="",
            jbaccount=r["jbaccount"], jbamount=jbamount,
            jbamountlnk=jbamount, jbpayee=jbpayee
        )
        # missing fields: jbissue_date, jbpostd_dat

        if test:
            print "{}) {}".format(x, cheque.__dict__)
        else:
            # insert the data
            try:
                session.add(cheque)
                session.flush()
            except exc.SQLAlchemyError as e:
                print e
                print "Bad data: {}".format(cheque.__dict__)
                session.rollback()
        x += 1

    if not test:
        session.commit()

    # fin

    print "Checks processed: {}".format(x)
    session.close()


######################
# shell command line
######################

if __name__ == "__main__":
    args = parser.parse_args()
    phile = args.phile
    date = args.date
    test = args.test

    if not phile or not date:
        print "mandatory options are missing: file name and date\n"
        parser.print_help()
        exit(-1)
    sys.exit(main())

