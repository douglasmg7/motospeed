#!/usr/bin/env python3

import xml_util

#  def ():
    #  zunka = ZunkaInterface()
    #  product = zunka.get_one_product()
    
class TestXml:
    # No meli product.
    def test_convert_br_currency_to_int_100(self):
        val = '1.234.567,89'
        res = xml_util.convert_br_currency_to_int_100(val)
        assert res == 123456789

        val = '1.234.567,81'
        res = xml_util.convert_br_currency_to_int_100(val)
        assert res == 123456781

        val = '0,11'
        res = xml_util.convert_br_currency_to_int_100(val)
        assert res == 11

        val = '0,19'
        res = xml_util.convert_br_currency_to_int_100(val)
        assert res == 19

        print('end')
