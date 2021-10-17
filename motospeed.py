#!/usr/bin/env python3

import sys
from logger import debug, info, warning, error, critical

# Convert string with br formar number to int X 100.
def convert_br_currency_to_int_100(val):
    return round(float(val.replace('.', '').replace(',', '.')) * 100)

# Convert kg string to int grams.
def convert_kg_string_to_int_grams(val):
    return round(float(val.replace('.', '').replace(',', '.')) * 1000)
