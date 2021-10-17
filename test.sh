#!/usr/bin/env bash
# -s see prints
# -v more verbose

pytest ./test_xml_util.py::TestXml -k convert -sv
