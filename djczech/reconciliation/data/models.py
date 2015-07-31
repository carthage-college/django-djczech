from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, BigInteger, Integer, String, DateTime, Float

import datetime

Base = declarative_base()

def _get_date():
    return datetime.datetime.now()

class Cheque(Base):
    __tablename__ = 'ccreconjb_rec'

    """
    Integer might not work here since our informix database can
    have primary key values that are quite large. LongInteger
    seems to be BigInteger in the SQLAlchemy universe.
    """
    jbchkno = Column(BigInteger)
    jbchknolnk = Column(BigInteger)
    jbimprt_date = Column(DateTime, default=_get_date)
    jbstatus = Column(String)
    jbstatus_date = Column(DateTime)
    jbaction = Column(String)
    jbaccount = Column(String)
    jbamount = Column(Float)
    jbamountlnk = Column(Float)
    jbissue_date = Column(DateTime)
    jbpostd_dat = Column(String)
    jbpayee = Column(String)
    jbseqno = Column(Integer, primary_key=True, autoincrement=True)

    def __repr__(self):
        return str(self.jbchkno)

