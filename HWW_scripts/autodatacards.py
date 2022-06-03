#a python script for properly generating datacards according to SR categories
import os
import sys
import math
import numpy as np
import argparse
import uproot
import types
from collections import OrderedDict
from ROOT import gROOT,TFile,TTree,TH1D
import ROOT as r
from datacardrefs import datacardrefs
from histmaker import histmaker
gROOT.SetBatch(True)

# can run datacards for example using python autodatacards.py -y 2017

parser = argparse.ArgumentParser(description='Datacard information')
parser.add_argument("-o", "--outdir",   dest="outdir",   default='./datacards/',                      help="directory to put datacards in")
parser.add_argument("-y", "--year",     dest="year",     default='2016',                               help="year")
parser.add_argument("-c", "--chan",     dest="chan",     default='had',                               help="channel")
parser.add_argument("-f", "--shapefile",    dest="shapefile",    default='shapehists.root',            help="file where shape histograms are located")
parser.add_argument("-r", "--remakehists",    dest="remakehists",    default='True',                   help="regenerate shape histograms")
args = parser.parse_args()

class autodatacards:
    def __init__(self, args):
        self.year      = args.year
        self.shapefile = args.shapefile
        self.outdir    = args.outdir
        self.chan = args.chan
        self.refs = datacardrefs(self.year, self.chan)
        
        #enabling/disabling automcstats:
        self.usemcbinuncs = True
        
        #for generating histograms or not
        remakehists=False
        if args.remakehists=='True':
            remakehists=True
        self.remakehists = remakehists

        #setup directories
        if not os.path.exists(self.outdir):
            os.makedirs(self.outdir); print('Making output directory ', self.outdir)

    #organizes set of bins for datacards and sets up card names and output directory
    def cardsetup(self, startbinnum):        
        #set up datacardrefs
        name = 'hwwcard' #name in your datacards
   
        # get name of output shape rootfile
        self.shaperoot = self.outdir+'/'+name+'_'+self.year+'_'+self.shapefile
        cardname = self.outdir+'/'+name

        #print info on the datacards you are making
        #this is also text to be put in each datacard in the set
        header='#----------------------------------------------#\n'+'#generating datacards. name: '+name+', self.year'+self.year+'\n'
        header+='\n'+'#number of cards in set: '+str(len(self.refs.binsels.keys()))+'\n'
        print(header)

        #generate shape histograms:
        hm = histmaker(self.year, self.chan, self.shaperoot)
        if (not os.path.exists(self.shaperoot)) or self.remakehists:
            print('generating histograms...')
            histfile = r.TFile(self.shaperoot, "RECREATE")
            histfile.Close()
            del histfile
            yields = hm.makehists()

        shapeline = 'shapes * * '+name+'_'+self.year+'_'+self.shapefile+' $CHANNEL_$PROCESS $CHANNEL_$PROCESS_$SYSTEMATIC'
        print(shapeline)

        #make cards:
        binnum = startbinnum
        for chanid, binsel in self.refs.binsels.iteritems():
            label=chanid+'_'+self.year
            # sel = '('+binsel+' &&  '+self.refs.mcsel
            self.makecard(cardname, label, binnum, header, shapeline, yields)
            binnum+=1
        return binnum

    #calculates rates and statistical uncertainties
    def getRate(self, procfile, cutstr, year, treename='Events'):
        print(procfile, treename)
        tree = r.TFile(procfile).Get(treename)
        htmp = r.TH1F('htmp','htmp',1,0.0,1.0)
        tree.Project('htmp','catBDTdisc_nosys',cutstr)
        errorVal = r.Double(0)
        rate = htmp.IntegralAndError(0,3,errorVal)
        rate = 0.0;rateunc = 1.0 
        if rate>0.0: #nonzero
            rateunc += (errorVal/rate)
        return round(rate,3), round(rateunc,3)
        
    def uncline(self, proc, uncval, uncname, unctype, binlabel, index, nprocs):
        rowname = binlabel+'_'+proc+'_'+uncname
        line = rowname+'      '+unctype
        row = ['-']*nprocs
        row[index] = str(uncval)
        for u in row:
            line+=('    '+u)
        line += '\n'
        return line

    def unctable(self, processes, unclist, uncname, unctype, binlabel):
        #unctype is lnN or shape...
        #unclist is the list of uncertainties for each process
        rownames = []
        for proc in processes:
            rowname = binlabel+'_'+proc+'_'+uncname
            rownames.append(rowname)
        # loop and create the table
        table = ''
        for i in range(len(processes)):
            row = ['-']*len(processes)
            row[i] = str(unclist[i])
            line = rownames[i]+'      '+unctype
            for u in row:
                line+=('    '+u)
            line += '\n'
            table+=line
            # print(table)
        return table

    #creates a single datacard
    def makecard(self, cardname, binlabel, nbin, header, shapeline, yields):
        #binlabel is cut#_bin#_year
        #cardfile is for example datacards/RTht5_cut1bin5_datacard.txt
        cardfile = cardname+'_'+binlabel+'_datacard'+str(nbin)+'.txt'
        procs = self.refs.processes
        nprocs = len(procs)

        imax = 1#number of final states analyzed (signals)
        jmax = nprocs-1 #number of processes(incl signal)-1
        kmax = '*' #* makes the code figure it out. number of independent systematical uncertainties 
        unctype  = 'lnN'

        print('\n'+binlabel)
        print('writing', cardfile)

        # get yields and statistical uncertainties for each process in this bin:
        rates=[]; stats=[]
        for proc in procs:
            r=0.0;u=0.0
            yld = yields[binlabel+'_'+proc]
            r=yld[0]; u=yld[1]
            rates.append(r); stats.append(1.0+(u/r))
            print(proc, r, u)
        obs  = int(round(sum(rates)))
        print('TOTAL B: ', round(sum(rates[1:])))

        
        # put together uncertanties for each process
        shapeuncs = [str(1.0)]*nprocs
        systuncs = [str(1.2), str(1.3), str(1.1), str(1.1), str(1.1)]
        systuncs2 = [str(1.2)]*nprocs
        stat_table  = self.unctable(procs, stats, 'stat', 'lnN', binlabel)
        shape_table=''
        syst_table = self.unctable(procs, systuncs, 'dummysyst', 'lnN', binlabel)
        syst_table2 = self.unctable(procs, systuncs2, 'dummytagsyst', 'lnN', binlabel)

        
        #norm uncertainty example:
        # lumi_line ='lumi_'+year+'   lnN    '+self.refs.lumiunc+'    '+self.refs.lumiunc+'    '+self.refs.lumiunc+'    -    \n'
        # syst_table+=lumi_line

        #shape uncertainties - leaving now to show correlation differences
        # corr =[]
        # for proc, systlist in self.refs.systs.iteritems():
        #     for sys in systlist: 
        #         if sys not in corr:
        #             corr.append(sys)
        # for sys in corr:
        #     if sys=='isr' or sys=='fsr' or sys=='ME' or sys=='pdf':
        #         shape_table += sys+'  shape     1.0    -    -    -  \n'  #need to add the right symbol for procs #correlated between years
        #     elif sys=='btagLF' or sys=='btagHF' or sys=='btagCFerr1' or sys=='btagCFerr2':
        #         shape_table += sys+'  shape     1.0    1.0    1.0    - \n'
        #     else: 
        #         shape_table += sys+'_'+year+'   shape     1.0   1.0    1.0    - \n'

        rateline = ''
        procline = ''
        numline = ''
        binuncline = ''
        if self.usemcbinuncs:
            thr = 0
            includesig = 0
            binuncline = binlabel+' autoMCStats '+str(thr)+' '+str(includesig)
            print(binuncline)

        #write datacard to file

        f = open(cardfile, "w")
        print>>f, '## card: '+cardfile+' number in set: '+str(nbin)
        # print>>f, '##selection: '+cutstr+'*prefirewgt*\n'
        print>>f, header
        print>>f, '## number of signals (i), backgrounds (j), and uncertainties (k)'
        print>>f, "---"
        print>>f, "imax: "+str(imax)
        print>>f, "jmax: "+str(jmax)
        print>>f, "kmax: "+str(kmax)
        print>>f, "---\n"
        # if useshape:
        print>>f, '## input the bdt shape histograms'
        print>>f, "---"
        print>>f, shapeline
        print>>f, "---\n"
        print>>f, '## list the bin label and the number of (data) events observed'
        print>>f, "---"
        print>>f, "bin  "+binlabel
        print>>f, "observation "+str(obs)
        print>>f, "---\n"
        print>>f, '## expected events for signal and all backgrounds in the bins'
        print>>f, "---"
        print>>f, "bin    "+(("    "+binlabel)*nprocs)
        for i,p in enumerate(procs):
            procline+=("    "+p)
            numline+=("        "+str(i))
        print>>f, "process"+procline
        print>>f, "process"+numline
        for r in rates:
            rateline+=("    "+str(r))
        print>>f, "rate   "+rateline        
        print>>f, "---\n"
        # if not nounc:
        print>>f, '## list the independent sources of uncertainties, and give their effect (syst. error) on each process and bin'
        print>>f, "---"
        print>>f, '## statistical uncertainties\n'
        print>>f, stat_table
        # if not nounc:
        print>>f, "---"
        print>>f, '## systematic uncertainties\n'
        print>>f, syst_table
        print>>f, syst_table2
        # if useshape:
        print>>f, "---"
        print>>f, '## shape uncertainties\n'
        print>>f, shape_table
        print>>f, "---\n"
        print>>f, binuncline
        print>>f, "---\n"
    
        f.close()

####################################################################
# run cards

cards = autodatacards(args)
startbinnum=0
# print('how many years?', len(cards.years))
# for year in cards.years:
print('year', args.year, 'startbinnum', startbinnum)
lastbinnum = cards.cardsetup(startbinnum)
print('lastbinnum', lastbinnum)
print('~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~')
print('~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~\n\n')
startbinnum=lastbinnum

