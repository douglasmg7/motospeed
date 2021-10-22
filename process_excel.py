#!/usr/bin/env python3
__version__ = '0.1.0'

import os, sys, datetime, csv
from shutil import copyfile
from logger import debug, info, warning, error, critical
from sqlalchemy.orm import Session
#  from db import Product, engine
from db import  engine

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
        'DESCRIÇÃO':            'desc', 
        'CX MASTER':            'cx_master', 
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

    #  ms.rename({'SKU':'sku', 'EAN':'ean', 'MODELO':'model', 'DESCRIÇÃO': 'desc', 'CX MASTER': 'cx_master', 'IPI':'ipi'}, axis=1, inplace=True)
    #  ms.rename({'NCM':'ncm', 'CONEXÃO':'connection', 'COMPATIVEL':'compatibility', 'CURVA': 'curve', 'DIMENSOES     (CM)':'dim_cm'}, axis=1, inplace=True)
    #  ms.rename({'PESO       (KG)': 'weight_kg', 'PREÇO':'price', 'DISTR': 'price_dist', 'PSV': 'price_sell', 'Estoque':'stock'}, axis=1, inplace=True)
    #  ms.columns
    #  ms['cx_master'].unique()

    # Remove row that have NaN, pd.NaT, None into Estoque.
    ms = ms.dropna(subset=['stock', 'model', 'desc']);

    # Remove not numeric values from price and price_dist.
    ms = ms.loc[pd.to_numeric(ms['price'], errors='coerce').notnull()]
    ms = ms.loc[pd.to_numeric(ms['price_dist'], errors='coerce').notnull()]

    # Only rows with price and price_dist above some value.
    ms = ms.loc[(ms['price'] > 10) & (ms['price_dist'] > 10)]

    # Create a column for each dimension.
    dim = ms.dim_cm.str.split('x', expand=True)
    ms['length'] = dim[0]
    ms['width'] = dim[1]
    ms['depth'] = dim[2]
    ms.pop('dim_cm');

    # Create title and desc columns.
    desc_temp = ms.desc.str.split(':', n=1, expand=True)
    ms['title'] = desc_temp[0]
    ms['desc'] = desc_temp[1]

    print(ms.head(3))
    #  print(ms.title.iloc[0])

    ms.to_sql('test', con=engine)


if os.path.exists(csv_file):
    process_excel('tabela.xlsm')

    # Rename file processd.
    now = datetime.datetime.now().date()
    new_file_name = os.path.join(os.path.dirname(csv_file), f'{now.year}_{now.month}_{now.day}_processed_motospeed_products.csv')
    #  copyfile(csv_file, new_file_name)
    #  os.remove(csv_file)
else:
    info(f'No {csv_file} to be processed')
