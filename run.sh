#!/usr/bin/env bash
eval "$(conda shell.bash hook)"
conda activate motospeed

$GS/motospeed/process_csv.py

conda deactivate