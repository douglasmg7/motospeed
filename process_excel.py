#!/usr/bin/env python3
__version__ = '0.2.0'

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
excel_file = os.environ['MOTOSPEED_EXCEL']

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
        'PREÇO REVENDA':        'price', 
        'PREÇO DISTRIBUIDOR':   'price_dist', 
        'STREET PRICE':         'price_sell', 
        'Estoque':              'stock',
    }
    ms.rename(new_column_titles, axis=1, inplace=True)
    ms.info(3)

    #  ms.columns
    #  ms['cx_master'].unique()

    # Remove row that have NaN, pd.NaT, None into Estoque.
    ms = ms.dropna(subset=['stock', 'model', 'description']);
    ms.stock = ms.stock.astype(int)

    # Remove not numeric values from price and price_dist.
    ms = ms.loc[pd.to_numeric(ms['price'], errors='coerce').notnull()]
    ms = ms.loc[pd.to_numeric(ms['price_dist'], errors='coerce').notnull()]
    ms = ms.loc[pd.to_numeric(ms['price_sell'], errors='coerce').notnull()]

    ms.price = ms.price.astype(float)*100
    ms['price_100'] = ms.price.astype(int)
    ms.pop('price')

    ms.price_dist = ms.price_dist.astype(float)*100
    ms['price_dist_100'] = ms.price_dist.astype(int)
    ms.pop('price_dist')

    ms.price_sell = ms.price_sell.astype(float)*100
    ms['price_sell_100'] = ms.price_sell.astype(int)
    ms.pop('price_sell')


    # Only rows with price and price_dist above some value.
    ms = ms.loc[(ms.price_100 > 100) & (ms.price_dist_100 > 100)]

    # Create a column for each dimension.
    # Decimal separator correction.
    ms.dim_cm = ms.dim_cm.replace({',':'.'}, regex=True)
    dim = ms.dim_cm.str.split('x', expand=True)

    # Length.
    dim[0] = dim[0].str.replace(r'[a-zA-Z]', '', regex=True)
    dim[0].fillna(0, inplace=True)
    dim[0] = dim[0].astype(float)*10
    dim[0] = dim[0].astype(int)
    ms['length_mm'] = dim[0]

    # Width.
    dim[1] = dim[1].str.replace(r'[a-zA-Z]', '', regex=True)
    dim[1].fillna(0, inplace=True)
    dim[1] = dim[1].astype(float)*10
    dim[1] = dim[1].astype(int)
    ms['width_mm'] = dim[1]
    
    # Depth.
    dim[2] = dim[2].str.replace(r'[a-zA-Z]', '', regex=True)
    dim[2].fillna(0, inplace=True)
    dim[2] = dim[2].astype(float)*10
    dim[2] = dim[2].astype(int)
    ms['depth_mm'] = dim[2]

    ms.pop('dim_cm');

    # Weight kg to grams.
    ms.weight_kg.fillna(0, inplace=True)
    ms['weight_g'] = ms.weight_kg.astype(float)*1000
    ms.weight_g = ms.weight_g.astype(int)
    ms.pop('weight_kg')

    # Master box.
    ms.master_box.fillna(0, inplace=True)
    ms.master_box = ms.master_box.astype(int)

    # Create title and description columns.
    desc_temp = ms.description.str.split(':', n=1, expand=True)
    ms['title'] = desc_temp[0]
    ms['description'] = desc_temp[1]

    #  print(ms.head(3))
    #  print(ms.title.iloc[0])
    info(f'Data frame shape: {ms.shape}')

    # Convert ipi to decimals to x100.
    ms.ipi.fillna(0, inplace=True)
    ms['ipi_100'] = ms.ipi*100
    ms.ipi_100 = ms.ipi_100.astype(int)
    ms.pop('ipi')

    #  print(ms.dtypes)

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
                product.ipi_100 = row.ipi_100
                product.weight_g = row.weight_g
                product.length_mm = row.length_mm
                product.width_mm = row.width_mm
                product.depth_mm = row.depth_mm
                product.price_100 = row.price_100
                product.price_dist_100 = row.price_dist_100
                product.price_sell_100 = row.price_sell_100
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
            info(f'Product {product.sku} not in new excel file, setting stock to 0')
            product.stock = 0
            sess.merge(product)
            sess.commit()


if os.path.exists(excel_file):
    #  process_excel('tabela_minus_one.xlsm')
    #  process_excel('tabela.xlsm')
    process_excel(excel_file)

    # Rename file processd.
    now = datetime.datetime.now().date()
    new_file_name = os.path.join(os.path.dirname(excel_file), f'{now.year}_{now.month}_{now.day}_processed_motospeed_products.csv')
    #  copyfile(excel_file, new_file_name)
    #  os.remove(excel_file)
else:
    info(f'No {excel_file} to be processed')
