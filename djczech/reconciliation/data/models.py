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
    jbstatus = Column(String(8))
    jbstatus_date = Column(DateTime)
    jbaction = Column(String(24))
    jbaccount = Column(String(64))
    jbamount = Column(Float)
    jbamountlnk = Column(Float)
    jbissue_date = Column(DateTime)
    jbpostd_dat = Column(String(16))
    jbpayee = Column(String(64))
    jbseqno = Column(Integer, primary_key=True, autoincrement=True)

    def __repr__(self):
        return str(self.jbchkno)


class GltrRec(Base):
    __tablename__ = 'gltr_rec'

    gltr_no = Column(Integer, primary_key=True, autoincrement=True)
    jrnl_ref = Column(String(2))
    jrnl_no = Column(Integer)
    ent_no = Column(Integer)
    amt = Column(Float)
    fund = Column(String(1))
    func = Column(String(3))
    obj = Column(String(5))
    proj = Column(String(7))
    subs = Column(String(4))
    stat = Column(String(1))
    recon_stat = Column(String(1))

    def __repr__(self):
        return str(self.amt)

