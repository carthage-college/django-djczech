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

from djczech.reconciliation.sql import *

from djzbar.utils.informix import get_session
from djtools.fields import TODAY

from datetime import date, datetime

import argparse

"""
Reconcile cheque data
"""

EARL = settings.INFORMIX_EARL

# set up command-line options
desc = """
Optional --test argument
"""

parser = argparse.ArgumentParser(description=desc)

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
    import_date = datetime.combine(
        TODAY, datetime.min.time()
    )

    # create database connection
    print EARL
    session = get_session(EARL)
    # drop temp tables, just in case
    try:
        session.execute("DROP TABLE tmp_voida")
        print "tmp_voida dropped"
    except:
        print "no temp table: tmp_voida"
    try:
        session.execute("DROP TABLE tmp_voidb")
        print "tmp_voidb dropped"
    except:
        print "no temp table: tmp_voidb"

    # Populate void temp table A
    voida = session.execute(TMP_VOID_A)
    print "void a status: {}".format(voida.__dict__)

    # Populate void temp table B
    voidb = session.execute(TMP_VOID_B)
    print "void b status: {}".format(voidb.__dict__)

    # TEST voida temp table
    # remove later
    objs = session.execute(SELECT_VOID_A)
    print "select tmp_voida"
    for o in objs:
        print o.__dict__

    # select * from temp table B and send the data to the business office
    objs = session.execute(SELECT_VOID_B)

    # TEST: print voidb data
    for o in objs:
        print o.__dict__

    # Find the duplicate check numbers and update as 's'uspicious

    # first, drop the temp tables, just in case
    try:
        session.execute("DROP TABLE tmp_maxbtchdate")
        print "tmp_maxbtchdate dropped"
    except:
        print "no temp table: tmp_maxbtchdate"
    try:
        session.execute("DROP TABLE tmp_DupCkNos")
        print "tmp_DupCkNos dropped"
    except:
        print "no temp table: tmp_DupCkNos"
    try:
        session.execute("DROP TABLE tmp_4updtstatus")
        print "tmp_4updtstatus dropped"
    except:
        print "no temp table: tmp_4updtstatus"

    # obtain the import date in a very weird manner
    # we don't need this chapuza.
    sql = """
        SELECT
            Min(ccreconjb_rec.jbimprt_date) AS crrntbatchdate
        FROM
            ccreconjb_rec
        WHERE
            jbimprt_date >= '{}'
        INTO TEMP
            tmp_maxbtchdate
        WITH NO LOG
    """.format(import_date)

    max_batch_date = session.execute(sql)

    # select the duplicates
    sql = """
        SELECT
            ccreconjb_rec.jbchkno, tmp_maxbtchdate.crrntbatchdate,
            Max(ccreconjb_rec.jbimprt_date) AS maxbatchdate,
            Min(ccreconjb_rec.jbimprt_date) AS minbatchdate,
            Count(ccreconjb_rec.jbseqno) AS countofjbseqno
        FROM
            ccreconjb_rec, tmp_maxbtchdate
        WHERE
            ccreconjb_rec.jbimprt_date >= '{}'
        GROUP BY
            ccreconjb_rec.jbchkno, tmp_maxbtchdate.crrntbatchdate
        HAVING
            Count(ccreconjb_rec.jbseqno) > 1
        INTO TEMP
            tmp_dupcknos
        WITH NO LOG
    """.format(import_date)

    duplicate_check_numbers = session.execute(sql)

    sql = """
        SELECT
            ccreconjb_rec.jbseqno, ccreconjb_rec.jbchkno,
            ccreconjb_rec.jbchknolnk, ccreconjb_rec.jbimprt_date,
            ccreconjb_rec.jbstatus, ccreconjb_rec.jbaction,
            ccreconjb_rec.jbaccount, ccreconjb_rec.jbamount,
            ccreconjb_rec.jbamountlnk, ccreconjb_rec.jbstatus_date,
            tmp_dupcknos.crrntbatchdate, tmp_dupcknos.maxbatchdate,
            tmp_dupcknos.minbatchdate, tmp_dupcknos.countofjbseqno
        FROM
            ccreconjb_rec, tmp_dupcknos
        WHERE
            ccreconjb_rec.jbimprt_date >= '{}'
        AND
            ccreconjb_rec.jbchkno = tmp_dupcknos.jbchkno
        AND
            ccreconjb_rec.jbstatus = 'I'
        ORDER BY
            ccreconjb_rec.jbchkno, ccreconjb_rec.jbseqno
        INTO TEMP
            tmp_4updtstatus
        WITH NO LOG
    """.format(import_date)

    for_update_status = session.execute(sql)

    # execute the update statement
    update_status = session.execute(UPDATE_STATUS)

    # send the records selected to be updated to the business office
    objs = session.execute(SELECT_RECORDS_FOR_UPDATE)

    # send duplicate records to the business office


    try:
        session.execute("DROP TABLE tmp_reconupdta")
        print "tmp_reconupdta dropped"
    except:
        print "no temp table: tmp_reconupdta"

    # Find the cleared Check Numbers
    sql = """
        AND
            ccreconjb_rec.jbimprt_date >= '{}'
        ORDER BY
            gle_rec.doc_no
        INTO TEMP
            tmp_reconupdta
        WITH NO LOG
    """.format(SELECT_CLEARED_CHEQUES, import_date)

    select_reconciled = session.execute(sql)
    # set gltr_rec as 'r'econciled
    update_reconciled = session.execute(UPDATE_RECONCILED)
    # set ccreconjb_rec as 'ar' (auto-reconciled)
    update_status = session.execute(UPDATE_STATUS)

    # send the results to business office
    objs = session.execute(SELECT_RECONCILIATED)

    session.close()


######################
# shell command line
######################

if __name__ == "__main__":
    args = parser.parse_args()
    test = args.test

    sys.exit(main())
