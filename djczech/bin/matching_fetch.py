# -*- coding: utf-8 -*-
import os, sys

# env
sys.path.append('/usr/lib/python2.7/dist-packages/')
sys.path.append('/usr/lib/python2.7/')
sys.path.append('/usr/local/lib/python2.7/dist-packages/')
sys.path.append('/d1/staging/django_1.7/')
sys.path.append('/d1/staging/django_projects/')
sys.path.append('/d1/staging/django_third/')
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "djczech.settings")


from django.conf import settings

from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine

EARL = settings.INFORMIX_EARL

def main():
    """
    main function
    """

    engine = create_engine(EARL)
    print EARL
    Session = sessionmaker(bind=engine)
    session = Session()
    sql = """
        SELECT gle_rec.doc_no as check_number, gltr_rec.amt as amount,
            trim(id_rec.fullname) as fullname,
            TO_CHAR(vch_rec.pst_date,'%Y-%m-%d') as post_date
        FROM
            vch_rec, gle_rec, gltr_rec, id_rec
        WHERE
            vch_rec.vch_ref = gle_rec.jrnl_ref
        AND vch_rec.jrnl_no = gle_rec.jrnl_no
        AND vch_rec.vch_ref = "CK"
        AND gle_rec.doc_id = id_rec.id
        AND gle_rec.jrnl_ref = gltr_rec.jrnl_ref
        AND gle_rec.jrnl_no = gltr_rec.jrnl_no
        AND gle_rec.gle_no = gltr_rec.ent_no
        AND (gltr_rec.recon_stat != "r" AND gltr_rec.recon_stat != "v")
        AND gltr_rec.stat = "P"
        ORDER BY check_number DESC
    """
    print sql
    cheques = session.execute(sql)
    for c in cheques:
        print c

    sql = """
       SELECT
            jbchkno as check_number, jbamount as amt, jbaction,
            jbstatus, TO_CHAR(jbstatus_date,'%Y-%m-%d') as cleared_date,
            jbpayee, jbaccount, jbseqno
       FROM
            ccreconjb_rec
       WHERE
            (jbstatus = "I" OR jbstatus = "s")
       AND
            jbimprt_date > "2015-05-31 00:00:00.0"
       ORDER BY check_number DESC
    """
    print sql
    cheques = session.execute(sql)
    for c in cheques:
        print c

    session.close()

######################
# shell command line
######################

if __name__ == "__main__":
    sys.exit(main())
