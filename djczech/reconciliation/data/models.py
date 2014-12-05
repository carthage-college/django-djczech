from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, DateTime, Float

import datetime

Base = declarative_base()

def _get_date():
    return datetime.datetime.now()
    #return datetime.datetime.now().strftime("%Y-%m-%d")

class Cheque(Base):
    __tablename__ = 'ccreconjb_rec'

    jbchkno = Column(Integer, primary_key=True)
    jbimprt_date = Column(DateTime, default=_get_date)
    jbstatus = Column(String)
    jbstatus_date = Column(DateTime)
    jbaction = Column(String)
    jbaccount = Column(String)
    jbamount = Column(Float)
    jbissue_date = Column(DateTime)
    jbpostd_dat = Column(String)
    jbpayee = Column(String)
    jbseqno = Column(Integer)

    def __repr__(self):
        return str(self.jbchkno)

#http://turbogears.org/2.1/docs/main/SQLAlchemy.html
