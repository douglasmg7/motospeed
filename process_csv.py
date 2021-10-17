#!/usr/bin/env python3

import os, csv
from shutil import copyfile
from logger import debug, info, warning, error, critical
from sqlalchemy.orm import Session
from db import Product, engine

csv_file = os.environ['MOTOSPEED_CSV']

def process_csv():
    with open(csv_file) as csv_data_file:
        csv_reader = csv.reader(csv_data_file)
        for product in csv_reader:
            print(product)

#  # Upsert on db.
#  def upsert_on_db(root):
    #  info(f'Processing {len(root)} products')
    #  with Session(engine) as sess:
        #  for item in root:
            #  try:
                #  product = Product() 
                #  product.it_codigo = handytech.get_it_codigo(item)
                #  product.desc_item = handytech.get_desc_item(item)
                #  product.desc_item_ec = handytech.get_desc_item_ec(item)
                #  product.narrativa_ec = handytech.get_narrativa_ec(item)
                #  product.vl_item = handytech.get_vl_item(item)
                #  product.vl_item_sdesc = handytech.get_vl_item_sdesc(item)
                #  product.vl_ipi = handytech.get_vl_ipi(item)
                #  product.perc_preco_sugerido_solar = handytech.get_perc_preco_sugerido_solar(item)
                #  product.preco_sugerido = handytech.get_preco_sugerido(item)
                #  product.preco_maximo = handytech.get_preco_maximo(item)
                #  product.categoria = handytech.get_categoria(item)
                #  product.sub_categoria = handytech.get_sub_categoria(item)
                #  product.peso = handytech.get_peso(item)
                #  product.codigo_refer = handytech.get_codigo_refer(item)
                #  product.fabricante = handytech.get_fabricante(item)
                #  product.saldos = handytech.get_saldos(item)
                #  product.arquivo_imagem = handytech.get_arquivo_imagem(item)
            #  except Exception as e:
                #  error(f'Product it_codigo: {product.it_codigo}. {e}')
            #  #  print(vars(product))
            #  sess.merge(product)
        #  sess.commit()

if os.path.exists(csv_file):
    process_csv()
    copyfile(csv_file, f'{csv_file}_processed')
    # Remove file, next will be download.
    os.remove(csv_file)
else:
    info(f'No {csv_file} to be processed')

