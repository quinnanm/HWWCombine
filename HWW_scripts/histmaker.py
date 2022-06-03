import os
import sys
import math
import numpy as np
import argparse
from ROOT import gROOT,TFile,TTree,TH1D
import ROOT as r
from datacardrefs import datacardrefs
gROOT.SetBatch(True)
import numpy as np
from array import array
 
class histmaker:
# class that creates shape histograms for combine
    def __init__(self, year, chan, outfilename):
        self.df = datacardrefs(year, chan)
        # self.systs = self.df.systs #dictionary of cut+bin ids and selections
        self.outroot = outfilename #name of shape rootfile
        self.year       = year
        self.chan = chan
        self.yields= {}
        data = self.df.datafile
        self.datafile = data
        self.blind = True
        if data=='none' or '.root' not in data:
            print 'blind run. will add empty data_obs histograms'
            self.blind = True

    def datahist(self, channel, binsel):
        histname = channel+'_'+self.year+'_data_obs'
        datahist = r.TH1F(histname, histname, self.df.nbins, self.df.selrange[0], self.df.selrange[1])

        #actually fill the histogram if it isn't a blind analysis
        if not self.blind:
            print self.df.datafile
            pfile = r.TFile(self.df.datafile)
            ptree = pfile.Get(self.df.tn)
            gROOT.cd()
            ptree.Draw(self.df.var+'>>'+histname, binsel)#apply bin selection
            yld, unc = self.df.getyield(datahist)
            self.yields[histname] = [yld, unc]
  
            print 'filled data hist ', histname, 'with selection', binsel, 'for process data_obs and bin', channel
            print 'data yield', yld
        else:
            print 'created empty data_obs hist', histname

        #open rootfile for writing histograms
        histfile = r.TFile(self.outroot, "UPDATE")
        datahist.Write()
        histfile.Close()
        del histfile

    #makes a histogram for each process and bin. channel is the binname
    def getmchists(self, histname, processname, selection):
        shapevar=self.df.var
        # get, modify and return histogram:
        pfile = r.TFile(self.df.procfiles[processname])
        ptree = pfile.Get(self.df.tn)
        # if not self.df.usevarbin:
        dischist = r.TH1F(histname, histname, self.df.nbins, self.df.selrange[0], self.df.selrange[1])
        # else:
        #     dischist = r.TH1F(histname, histname, self.df.nbins, self.df.edges)

        print pfile
        ptree.Draw(shapevar+'>>'+histname, selection)#apply bin selection
        print 'filled hist ', histname, 'with selection', selection, 'for process', processname

        yld, unc = self.df.getyield(dischist)
        print yld, unc
        self.yields[histname] = [yld, unc]

        histfile = r.TFile(self.outroot, "UPDATE")
        dischist.Write()
        histfile.Close()
        del histfile
                      
    def makehists(self):        
        #first get the "normal" histograms
        for chanid, chansel in self.df.binsels.iteritems():
            #data hist
            dsel = '('+self.df.binsels[chanid]+' && '+self.df.getsels('data','nosys',False)+')'
            self.datahist(chanid, dsel)
            #mc hists
            for processname in self.df.mcprocs:
                histname = chanid+'_'+self.year+'_'+processname
                binsel = '('+chansel+' && '+self.df.getsels(processname,'nosys',True)
                self.getmchists(histname, processname, binsel)

        #then get the systematics histograms for shape variations:
        # for processname, systlist in self.df.systs.iteritems():
        #     for syst in systlist:
        #         if syst in['jer','jes']:
        #             discvarup = self.df.var+'_'+syst+'Up'
        #             discvardown = self.df.var+'_'+syst+'Down'
        #         else: 
        #             discvarup = self.df.var+'_nosys'
        #             discvardown = self.df.var+'_nosys'

        #         sysmcsel, sysbinsels = self.df.getsels(syst)
        #         for chanid in self.df.binsels.keys():
        #             syshistname = chanid+'_'+self.year+'_'+processname
        #             binselup = '('+sysbinsels[0][chanid]+' && '+sysmcsel[0]
        #             binseldown = '('+sysbinsels[1][chanid]+' && '+sysmcsel[1]
        #             if syst in ['fsr', 'isr', 'pdf', 'ME', 'btagLF','btagHF','btagCFerr1', 'btagCFerr2']: #year correlated systs
        #                 syshistname_up = syshistname+'_'+syst+'Up'
        #                 syshistname_down = syshistname+'_'+syst+'Down'
        #             else: # not year correlated systs
        #                 syshistname_up = syshistname+'_'+syst+'_'+self.year+'Up'
        #                 syshistname_down = syshistname+'_'+syst+'_'+self.year+'Down'
        #             self.getmchists(syshistname_up, processname, binselup, discvarup)
        #             self.getmchists(syshistname_down, processname, binseldown, discvardown)
        return self.yields



