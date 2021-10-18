#!/usr/bin/env python3
__version__ = '0.0.1'

import os, datetime, csv
from shutil import copyfile
from logger import debug, info, warning, error, critical
from sqlalchemy.orm import Session
from db import Product, engine
import motospeed

debug(f'Running version: {__version__}')
csv_file = os.environ['MOTOSPEED_CSV']

def process_csv():
    with open(csv_file) as csv_data_file:
        csv_reader = csv.reader(csv_data_file)
        with Session(engine) as sess:
            for csv_product in csv_reader:
                # Skip the row names.
                if csv_product[0] == 'Código':
                    continue
                print(csv_product)

                try:
                    product = Product() 
                    product.code = csv_product[0]
                    product.title = csv_product[1]
                    product.desc = csv_product[2]
                    product.price = motospeed.convert_us_currency_to_int_100(csv_product[3])
                    product.stock = csv_product[4]
                except Exception as e:
                    error(f'Product code: {csv_product[0]}. {e}')
                #  print(vars(product))
                sess.merge(product)
            sess.commit()

if os.path.exists(csv_file):
    process_csv()
    # Rename file processd.
    now = datetime.datetime.now().date()
    new_file_name = os.path.join(os.path.dirname(csv_file), f'processed_{now.year}_{now.month}_{now.day}.csv')
    copyfile(csv_file, new_file_name)
    #  os.remove(csv_file)
else:
    info(f'No {csv_file} to be processed')
