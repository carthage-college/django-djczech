from djczech.reconciliation.data.models import Cheque

from djzbar.settings import INFORMIX_EARL_TEST as INFORMIX_EARL
from djzbar.utils.informix import do_sql as do_esql

from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from sqlalchemy import text

sql = """
    SELECT
        first 1000
        *
    FROM
        ccreconjb_rec
    ORDER BY
        jbissue_date
"""

"""
objs = do_esql(sql)
for o in objs:
    print o.jbchkno, o.jbimprt_date
"""

engine = create_engine(INFORMIX_EARL)
Session = sessionmaker(bind=engine)
session = Session()

#session.query(Cheque).delete()
#session.commit()

cid = 172207
cheque = session.query(Cheque).filter_by(jbchkno=cid).first()

print cheque

#sql = "SELECT jbchkno, jbissue_date, status FROM users where jbaction=:action"
#objs = session.query("jbchkno", "jbissue_date", "status").\
#        from_statement(text(sql)).\
#        params(action='X').all()
#for o in objs:
#    print o.jbchkno, o.jbissue_date, o.status

"""
seq = 1
for instance in session.query(Cheque):
    print seq, instance.jbchkno
    seq += 1
"""
session.close()
