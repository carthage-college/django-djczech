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

# sql statements
from djczech.reconciliation import SELECT_VOID_A, SELECT_VOID_B
from djczech.reconciliation import SET_STATUS, SET_STATUS_TEST
from djczech.reconciliation import SET_RECONCILIATION_STATUS
from djczech.reconciliation import TMP_VOID_A, TMP_VOID_B
from djczech.reconciliation import UPDATE_STATUS, SELECT_RECORDS_FOR_UPDATE

from djczech.reconciliation.data.models import Cheque
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
    #print "void a status: {}".format(voida.__dict__)

    # Populate void temp table B
    voidb = session.execute(TMP_VOID_B)
    #print "void b status: {}".format(voidb.__dict__)

    if settings.DEBUG:
        print "select tmp_voida"
        objs = session.execute(SELECT_VOID_A)
        for o in objs:
            print o.__dict__

    # select * from temp table A and send the data to the business office
    objs = session.execute(SELECT_VOID_B)

    for o in objs:
        print o.__dict__

    # Find the DUP CheckNos and update as 's'uspicious

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

    # Find the cleared CheckNos and set:
    #   gltr_rec as 'r'econciled
    # and:
    #   ccreconjb_rec as 'ar' (auto-reconciled)

    try:
        session.execute("DROP TABLE tmp_reconupdta")
        print "tmp_reconupdta dropped"
    except:
        print "no temp table: tmp_reconupdta"

    sql = """
        SELECT
            ccreconjb_rec.jbimprt_date, ccreconjb_rec.jbseqno,
            ccreconjb_rec.jbchkno, ccreconjb_rec.jbchk_reconupdtanolnk,
            ccreconjb_rec.jbstatus, ccreconjb_rec.jbaction,
            ccreconjb_rec.jbamount, ccreconjb_rec.jbamountlnk,
            ccreconjb_rec.jbaccount, ccreconjb_rec.jbstatus_date,
            ccreconjb_rec.jbpayee, gltr_rec.gltr_no, gle_rec.jrnl_ref,
            gle_rec.jrnl_no, gle_rec.doc_id cknodoc_id, gltr_rec.amt,
            gle_rec.doc_no cknodoc_no, gltr_rec.subs, gltr_rec.stat,
            gltr_rec.recon_stat
        FROM
            vch_rec, gle_rec, gltr_rec, ccreconjb_rec
        WHERE
            gle_rec.jrnl_ref = 'CK'
        AND
            vch_rec.amt_type = 'ACT'
        AND
            gle_rec.ctgry = 'CHK'
        AND
            gle_rec.jrnl_ref = vch_rec.vch_ref
        AND
            gle_rec.jrnl_no = vch_rec.jrnl_no
        AND
            gle_rec.jrnl_ref = gltr_rec.jrnl_ref
        AND
            gle_rec.jrnl_no = gltr_rec.jrnl_no
        AND
            gle_rec.gle_no = gltr_rec.ent_no
        AND
            gltr_rec.stat IN('P','xV')
        AND
            ccreconjb_rec.jbimprt_date >= '{}'
        AND
            ccreconjb_rec.jbchknolnk = gle_rec.doc_no
        AND
            ccreconjb_rec.jbamountlnk = gltr_rec.amt
        AND
            ccreconjb_rec.jbstatus NOT IN("s","ar","er","mr")
        AND
            gltr_rec.recon_stat NOT IN("r","v")
        ORDER BY
            gle_rec.doc_no
        INTO TEMP
            tmp_reconupdta
        WITH NO LOG
    """.format(import_date)

    select_reconciled = session.execute(sql)

    sql = """
        UPDATE
            gltr_rec
        SET
            gltr_rec.recon_stat = 'r'
        WHERE
            gltr_rec.gltr_no
        IN  (
                SELECT
                    tmp_reconupdta.gltr_no
                FROM
                    tmp_reconupdta
            )
        AND
            gltr_rec.recon_stat = 'O'
    """

    update_reconciled = session.execute(sql)

    sql = """
        UPDATE
            ccreconjb_rec
        SET
            ccreconjb_rec.jbstatus = 'ar'
        WHERE
            ccreconjb_rec.jbseqno
        IN  (
                SELECT
                    tmp_reconupdta.jbseqno
                FROM
                    tmp_reconupdta
            )
        AND
            ccreconjb_rec.jbstatus = 'I'
    """

    update_status = session.execute(sql)

    # send the results to business office

    sql = """
        SELECT
            *
        FROM
            tmp_reconupdta
        ORDER BY
            tmp_reconupdta.cknodoc_no
    """

    objs = session.execute(sql)

    session.close()


######################
# shell command line
######################

if __name__ == "__main__":
    args = parser.parse_args()
    test = args.test

    sys.exit(main())
