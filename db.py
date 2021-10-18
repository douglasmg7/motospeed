#!/usr/bin/env python3

import os
import datetime
from logger import debug, info, warning, error, critical

from sqlalchemy import create_engine, text, MetaData, Table, Column, Integer, String, DateTime
#  from sqlalchemy.orm import registry
from sqlalchemy.orm import declarative_base, Session

DB_FILE = os.environ['MOTOSPEED_DB']
#  debug(f'Db file: {DB_FILE}')
engine = create_engine(f'sqlite+pysqlite:///{DB_FILE}', echo=False, future=True)
Base = declarative_base()
session = Session(engine)

class Product(Base):
    __tablename__ = 'product'
    code = Column(String, primary_key=True)
    title = Column(String)
    desc = Column(String)
    price = Column(Integer)
    stock = Column(Integer)
    zunka_product_id = Column(String)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

#  product = Product(it_code='qwe', desc_item='asdf asdf ', vl_item=123)
#  session.add(product)
#  session.commit()

#  product = session.get(Product, 'qwe')
#  print(vars(product))

# Create db.
if not os.path.exists(DB_FILE):
    info(f'Creating {DB_FILE}')
    os.makedirs(os.environ['ZUNKAPATH_DB'], exist_ok=True)
    Base.metadata.create_all(engine)
    #  Base.metadata.drop_all()
