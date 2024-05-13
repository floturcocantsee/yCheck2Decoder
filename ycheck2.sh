#!/bin/bash

filename=$1
basename=$(basename $filename .ycheck2)

./decode_ycheck2.py -i $filename -o output/$basename.pdf

open output/$basename.pdf
