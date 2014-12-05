from djczech.reconciliation.data.models import Cheque

from djzbar.settings import INFORMIX_EARL_PROD

from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from sqlalchemy import text

engine = create_engine(INFORMIX_EARL_PROD)
Session = sessionmaker(bind=engine)
session = Session()

sql = """
    SELECT
        first 1000
        *
    FROM
        ccreconjb_rec
    ORDER BY
        jbissue_date
"""

#sql = "SELECT jbchkno, jbissue_date, status FROM users where jbaction=:action"
#objs = session.query("jbchkno", "jbissue_date", "status").\
#        from_statement(text(sql)).\
#        params(action='X').all()
#for o in objs:
#    print o.jbchkno, o.jbissue_date, o.status

for instance in session.query(Cheque):
    print instance.jbchkno
