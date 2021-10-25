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
#  engine = create_engine(f'sqlite+pysqlite:///{DB_FILE}', echo=False)
Base = declarative_base()
session = Session(engine)

class Product(Base):
    __tablename__ = 'product'
    sku = Column(String, primary_key=True)
    title = Column(String)
    description = Column(String)
    ean = Column(String)
    model = Column(String)
    connection = Column(String)
    compatibility = Column(String)
    curve = Column(String)          # Product seller rank.
    ncm = Column(String)
    master_box = Column(Integer)    # Quantity of products for master box.
    weight_kg = Column(Integer)
    length_cm = Column(Integer)
    width_cm = Column(Integer)
    depth_cm = Column(Integer)
    ipi = Column(Integer)
    price_100 = Column(Integer)
    price_dist_100 = Column(Integer)    # Product price when buy as master box.
    price_sell_100 = Column(Integer)
    stock = Column(Integer)
    zunka_product_id = Column(String, default='')
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    changed_at = Column(DateTime, default=datetime.datetime.utcnow)
    removed_at = Column(DateTime)

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
