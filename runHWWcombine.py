#combines cards with little lablels                                                                                                                                                        
import subprocess
import numpy as np
import argparse
import ROOT as r
import pandas as pd
import sys
import os
import re

parser = argparse.ArgumentParser(description='')
parser.add_argument("-i", "--indir", dest="indir", nargs="*", default=[])
parser.add_argument("-o", "--outname", dest="outname", default='combined_HWW_datacard.txt')
args = parser.parse_args()

cmd='combineCards.py '

for cardpath in args.indir:
    cardname =  cardpath[cardpath.rfind('datacard_')+11:]
    cardname = cardname.strip('.txt')
    cmd+=''+cardname+'='+cardpath+' '

# cmd+=' combineCards.py > '+args.outname 

cmd+=' > '+args.outname
print cmd
subprocess.call(cmd, shell=True)
