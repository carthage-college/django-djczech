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

from datetime import datetime

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

    # start time
    print datetime.now()

    # convert date to datetime
    import_date = datetime.strptime(date, "%Y-%m-%d")
    print "import_date = {}".format(import_date)

    # create database connection
    session = get_session(EARL)
    print "database connection URL = {}".format(EARL)

    #...........................................
    print "drop temp tables, just in case"
    sql = "DROP TABLE tmp_voida"
    print sql
    if not test:
        try:
            session.execute(sql)
            print "tmp_voida dropped"
        except:
            print "no temp table: tmp_voida"

    #...........................................
    sql = "DROP TABLE tmp_voidb"
    print sql
    if not test:
        try:
            session.execute(sql)
            print "tmp_voidb dropped"
        except:
            print "no temp table: tmp_voidb"

    #...........................................
    print "Populate tmp_voida temp table"
    print "TMP_VOID_A sql:"
    sql = TMP_VOID_A
    if not test:
        x = session.execute(sql)
        print x.context.statement
    else:
        print sql

    #...........................................
    print "TEST: select * from tmp_voida table and print"
    print "SELECT_VOID_A sql:"
    sql = SELECT_VOID_A
    print sql
    if not test:
        objs = session.execute(sql).fetchall()
        for o in objs:
            print o

    #...........................................
    print "Populate tmp_voidb temp table"
    print "TMP_VOID_B sql:"
    sql = TMP_VOID_B
    if not test:
        x = session.execute(sql)
        print x.context.statement
    else:
        print sql

    #...........................................
    print "select * from tmp_voidb. print here / send_mail() in the view"
    print "SELECT_VOID_B sql:"
    sql = SELECT_VOID_B
    print sql
    if not test:
        objs = session.execute(sql).fetchall()
        for o in objs:
            print o

    #...........................................
    print "set reconciliation status to 'v'"
    print "UPDATE_RECONCILIATION_STATUS sql:"
    sql = UPDATE_RECONCILIATION_STATUS
    if not test:
        x = session.execute(sql)
        print x.context.statement
    else:
        print sql

    print "Find the duplicate check numbers and update as 's'uspicious"

    #...........................................
    print "TEST sql:"
    sql = "SELECT * FROM gltr_rec WHERE recon_stat = '{}'".format(
        settings.REQUI_VICH
    )
    print sql
    if not test:
        objs = session.execute(sql).fetchall()
        for o in objs:
            print o

    #...........................................
    print "first, drop the temp tables, just in case. sql:"
    sql = "DROP TABLE tmp_maxbtchdate"
    print sql
    if not test:
        try:
            session.execute(sql)
            print "tmp_maxbtchdate dropped"
        except:
            print "no temp table: tmp_maxbtchdate"

    #...........................................
    sql = "DROP TABLE tmp_DupCkNos"
    print sql
    if not test:
        try:
            session.execute(sql)
            print "tmp_DupCkNos dropped"
        except:
            print "no temp table: tmp_DupCkNos"

    #...........................................
    sql = "DROP TABLE tmp_4updtstatus"
    print sql
    #if not test:
    try:
        session.execute(sql)
        print "tmp_4updtstatus dropped"
    except:
        print "no temp table: tmp_4updtstatus"

    #...........................................
    print "select import_date and stick it in a temp table, for some reason"
    print "SELECT_CURRENT_BATCH_DATE sql:"
    sql = SELECT_CURRENT_BATCH_DATE(import_date=import_date)
    if not test:
        x = session.execute(sql)
        print x.context.statement
    else:
        print sql

    #...........................................
    print "TEST: display batch date. sql:"
    sql = "SELECT * FROM tmp_maxbtchdate"
    print sql
    if not test:
        obj = session.execute(sql)
        print obj.fetchone().crrntbatchdate

    #...........................................
    print "Select the duplicate cheques"
    print "SELECT_DUPLICATES_1 sql:"
    sql = SELECT_DUPLICATES_1(import_date=import_date)
    if not test:
        x = session.execute(sql)
        print x.context.statement
    else:
        print sql

    #...........................................
    print "TEST: print selected duplicate cheques. sql:"
    sql = "SELECT * FROM tmp_dupcknos"
    print sql
    if not test:
        objs = session.execute(sql).fetchall()
        for o in objs:
            print o

    #...........................................
    print "Select for updating"
    print "SELECT_FOR_UPDATING sql:"
    sql = SELECT_FOR_UPDATING(
        import_date=import_date,
        status=settings.IMPORT_STATUS
    )
    if not test:
        x = session.execute(sql)
        print x.context.statement
    else:
        print sql

    #...........................................
    print "Select the records for update. print here / send_mail() in the view"
    print "SELECT_RECORDS_FOR_UPDATE sql:"
    sql = SELECT_RECORDS_FOR_UPDATE
    print sql
    if not test:
        objs = session.execute(SELECT_RECORDS_FOR_UPDATE).fetchall()
        for o in objs:
            print o

    #...........................................
    print "Update cheque status to 's'uspictious"
    print "UPDATE_STATUS_SUSPICIOUS sql:"
    sql = UPDATE_STATUS_SUSPICIOUS
    if not test:
        x = session.execute(sql)
        print x.context.statement
    else:
        print sql

    #...........................................
    print "TEST sql:"
    sql = "SELECT * FROM ccreconjb_rec WHERE jbstatus = '{}'".format(
        settings.SUSPICIOUS
    )
    print sql
    if not test:
        objs = session.execute(sql).fetchall()
        for o in objs:
            print o

    #...........................................
    print "Select the duplicates. print here / send_mail() in the view"
    print "SELECT_DUPLICATES_2 sql:"
    sql = SELECT_DUPLICATES_2(import_date=import_date)
    print sql
    if not test:
        objs = session.execute(sql).fetchall()
        for o in objs:
            print o

    print "Find the cleared CheckNos and update gltr_rec as 'r'econciled"
    print "and ccreconjb_rec as 'ar' (auto-reconciled)"

    #...........................................
    print "Drop the temporary table, just in case. sql:"
    sql = "DROP TABLE tmp_reconupdta"
    print sql
    if not test:
        try:
            session.execute(sql)
            print "tmp_reconupdta dropped"
        except:
            print "no temp table: tmp_reconupdta"

    #...........................................
    print "Find the cleared Check Numbers"
    print "SELECT_CLEARED_CHEQUES sql:"
    sql = SELECT_CLEARED_CHEQUES(
        import_date=import_date,
        suspicious=settings.SUSPICIOUS,
        auto_rec=settings.AUTO_REC,
        requi_rich=settings.REQUI_RICH,
        requi_vich=settings.REQUI_VICH
    )
    if not test:
        x = session.execute(sql)
        print x.context.statement
    else:
        print sql

    #...........................................
    print "TEST: print selected duplicate cheques. sql:"
    sql = "SELECT * FROM tmp_reconupdta"
    print sql
    if not test:
        objs = session.execute("SELECT * FROM tmp_reconupdta").fetchall()
        for o in objs:
            print o

    #...........................................
    print "Set gltr_rec as 'r'econciled"
    print "UPDATE_RECONCILED sql:"
    sql = UPDATE_RECONCILED
    if not test:
        x = session.execute(sql)
        print x.context.statement
    else:
        print sql

    #...........................................
    print "TEST sql:"
    sql = "SELECT * FROM gltr_rec WHERE recon_stat = '{}'".format(
        settings.REQUI_RICH
    )
    print sql
    if not test:
        objs = session.execute(sql).fetchall()
        for o in objs:
            print o

    #...........................................
    print "Set ccreconjb_rec as 'ar' (auto-reconciled)"
    print "UPDATE_STATUS_AUTO_REC sql:"
    sql = UPDATE_STATUS_AUTO_REC
    if not test:
        x = session.execute(sql)
        print x.context.statement
    else:
        print sql

    #...........................................
    print "TEST sql:"
    sql = "SELECT * FROM ccreconjb_rec where jbstatus = '{}'".format(
        settings.AUTO_REC
    )
    print sql
    if not test:
        objs = session.execute(sql).fetchall()
        for o in objs:
            print o

    #...........................................
    print "select the reconciled checks. print here / send_mail() in view"
    print "SELECT_RECONCILIATED sql:"
    sql = SELECT_RECONCILIATED
    print sql
    if not test:
        objs = session.execute(sql).fetchall()
        for o in objs:
            print o

    session.commit()
    session.close()

    # end time
    print datetime.now()

######################
# shell command line
######################

if __name__ == "__main__":
    args = parser.parse_args()
    test = args.test
    date = args.date

    if not date:
        print "mandatory option is missing: date\n"
        parser.print_help()
        exit(-1)

    sys.exit(main())
