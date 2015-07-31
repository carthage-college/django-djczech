from django.conf import settings

from djczech.reconciliation.data.models import Cheque

from djzbar.settings import INFORMIX_EARL_TEST as INFORMIX_EARL
from djzbar.utils.informix import do_sql as do_esql

from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from sqlalchemy import text

"""
engine = create_engine(
    'ibm_db_sa://{}:{}@{}:{}/{}:INFORMIXSERVER=wilson'.format(
        settings.INFORMIX_USERNAME,
        settings.INFORMIX_PASSWORD,
        settings.INFORMIX_HOST,
        settings.INFORMIX_PORT,
        settings.INFORMIX_DATABASE
    )
)

engine = create_engine('ibm_db_sa://{}:{}@/pyinformix'.format(
        settings.INFORMIX_USERNAME,
        settings.INFORMIX_PASSWORD,
    )
)
"""

sql = """
    SELECT
        *
    FROM
        ccreconjb_rec
    ORDER BY
        jbissue_date
"""

#Session = sessionmaker(bind=engine)
#session = Session()
# query
#objs = session.query(Cheque).all()

#objs = engine.execute(sql)

objs = do_esql(sql)
for o in objs:
    print o.jbchkno, o.jbimprt_date
    #print o

#session.close()

#session.query(Cheque).delete()
#session.commit()

#cid = 172207
#cheque = session.query(Cheque).filter_by(jbchkno=cid).first()

#print cheque

'''
sql = """
    SELECT
        jbaction, jbchkno, jbissue_date, jbstatus
    FROM
        ccreconjb_rec where jbaction=:jbaction
    """

objs = session.query("jbaction", "jbchkno", "jbissue_date", "jbstatus").\
        from_statement(text(sql)).\
        params(jbaction='X').all()
for o in objs:
    print o.jbaction, o.jbchkno, o.jbissue_date, o.jbstatus
    #print o
'''

"""
# does the same as do_sql() function
objs = session.execute(sql)
for o in objs:
    print o
"""

"""
seq = 1
for instance in session.query(Cheque):
    print seq, instance.jbchkno
    seq += 1
"""
#session.close()
