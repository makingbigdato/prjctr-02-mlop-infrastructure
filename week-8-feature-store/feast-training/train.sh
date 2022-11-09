#!/bin/bash
set -xeu

cd features/
feast apply

cd /train
python train.py $@