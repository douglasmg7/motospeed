#!/usr/bin/env python3
__version__ = '0.1.0'

import os, sys, datetime, csv
from shutil import copyfile
from logger import debug, info, warning, error, critical
from sqlalchemy.orm import Session
#  from db import engine, Product
from db import engine, Product
import db

import pandas as pd
#  from pandas import DataFrame

import motospeed

info('Running ...')
info(f'Script: {__version__}')
info(f'Python: {sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}')
csv_file = os.environ['MOTOSPEED_CSV']

def process_excel(xlsm_file):
    ms = pd.read_excel(xlsm_file)

    # Change column names to be the first item.
    ms.columns = ms.loc[0]
    # Remove the first row, thas was used as column name.
    ms = ms.drop(0)
    #  ms.columns

    # Remove columns that will not be used.
    ms.pop('PRODUTO');
    ms.pop('QTD');
    ms.pop('TOTAL');

    # Rename column names.
    new_column_titles = {   
        'SKU':                  'sku', 
        'EAN':                  'ean', 
        'MODELO':               'model', 
        'DESCRIÇÃO':            'description', 
        'CX MASTER':            'master_box', 
        'IPI':                  'ipi',
        'NCM':                  'ncm', 
        'CONEXÃO':              'connection', 
        'COMPATIVEL':           'compatibility', 
        'CURVA':                'curve', 
        'DIMENSOES     (CM)':   'dim_cm',
        'PESO       (KG)':      'weight_kg', 
        'PREÇO':                'price', 
        'DISTR':                'price_dist', 
        'PSV':                  'price_sell', 
        'Estoque':              'stock',
    }
    ms.rename(new_column_titles, axis=1, inplace=True)

    #  ms.columns
    #  ms['cx_master'].unique()

    # Remove row that have NaN, pd.NaT, None into Estoque.
    ms = ms.dropna(subset=['stock', 'model', 'description']);

    # Remove not numeric values from price and price_dist.
    ms = ms.loc[pd.to_numeric(ms['price'], errors='coerce').notnull()]
    ms = ms.loc[pd.to_numeric(ms['price_dist'], errors='coerce').notnull()]

    # Only rows with price and price_dist above some value.
    ms = ms.loc[(ms['price'] > 10) & (ms['price_dist'] > 10)]

    # Create a column for each dimension.
    # Decimal separator correction.
    ms.dim_cm = ms.dim_cm.str.replace(',', '.')
    dim = ms.dim_cm.str.split('x', expand=True)
    ms['length_cm'] = dim[0]
    ms['width_cm'] = dim[1]
    ms['depth_cm'] = dim[2]
    ms.pop('dim_cm');

    # Create title and description columns.
    desc_temp = ms.description.str.split(':', n=1, expand=True)
    ms['title'] = desc_temp[0]
    ms['description'] = desc_temp[1]

    #  print(ms.head(3))
    #  print(ms.title.iloc[0])
    print(f'Data frame shape: {ms.shape}')

    # Upsert dataframe products.
    now = datetime.datetime.utcnow()
    with Session(engine) as sess:
        for index, row in ms.iterrows():
            #  print(row['sku'], row['title'])
            #  print(row.sku)
            #  dbProduct = db.Product(sku=product.sku, title=product.title, desc=product.desc)
            try:
                product = Product() 
                product.sku = row.sku
                product.title = row.title
                product.description = row.description
                product.ean = row.ean
                product.model = row.model
                product.connection = row.connection
                product.compatibility = row.compatibility
                product.curve = row.curve
                product.ncm = row.ncm
                product.master_box = row.master_box
                product.ipi = row.ipi
                product.weight_kg = row.weight_kg
                product.length_cm = row.length_cm
                product.width_cm = row.width_cm
                product.depth_cm = row.depth_cm
                product.price_100 = row.price * 100
                product.price_dist_100 = row.price_dist * 100
                product.price_sell_100 = row.price_sell * 100
                product.stock = row.stock
                product.changed_at = now
            except Exception as e:
                error(f'Product sku: {row.sku}. {e}')
            #  print(vars(product))
            sess.merge(product)
        sess.commit()

        # Update product not updated to stock 0.
        one_minute_ago = now - datetime.timedelta(minutes=1)
        for product in sess.query(Product).filter(Product.changed_at<one_minute_ago).all():
            print(f'Product {product.sku} not in new excel file, setting stock to 0')
            product.stock = 0
            sess.merge(product)
            sess.commit()


if os.path.exists(csv_file):
    #  process_excel('tabela_minus_one.xlsm')
    process_excel('tabela.xlsm')

    # Rename file processd.
    now = datetime.datetime.now().date()
    new_file_name = os.path.join(os.path.dirname(csv_file), f'{now.year}_{now.month}_{now.day}_processed_motospeed_products.csv')
    #  copyfile(csv_file, new_file_name)
    #  os.remove(csv_file)
else:
    info(f'No {csv_file} to be processed')
