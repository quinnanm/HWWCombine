import os
import numpy as np
import matplotlib
import argparse
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import root_numpy as rn
# import re
import ROOT as r
import scipy.integrate as integrate
import argparse
import sys
from ROOT import gStyle, gPad
from ROOT import gROOT,TFile,TTree,TH1D
gStyle.SetOptStat(0)

parser = argparse.ArgumentParser(description='adds eventBDT discriminants to premade trees.')
parser.add_argument("-f", "--fitfile", dest="fitfile", default='./datacards_had/hwwcard_2017_shapehists.root')
parser.add_argument("-v", "--var", dest="var", default='fj0_msoftdrop')
parser.add_argument("-y", "--year", dest="year", default='2016')
parser.add_argument("-n", "--note", dest="note", default='hww')
args = parser.parse_args()

class postfit:
    def __init__(self, args):
        self.year = args.year
        self.var = args.var
        self.note = args.note
        self.fitfile = args.fitfile

        self.colors = {'signal':r.TColor.GetColor("#163d4e"),
                       'data_obs':r.TColor.GetColor("#163d4e"),
                       'QCD':r.kRed-7,
                       'wjets':r.TColor.GetColor("#d07e93"),
                       'ttbar':r.kCyan,
                       'other':r.TColor.GetColor("#cf9ddb")}

        outdir = './plots/'+self.note+self.year+'/'
        if not os.path.exists(outdir):
            os.makedirs(outdir)
        self.outdir = outdir

        self.sig = 'signal'
        self.data = 'data_obs'
        self.procs = [self.data, self.sig, 'other', 'ttbar', 'wjets', 'QCD']
        # self.procs = [self.data, self.sig, 'QCD', 'wjets','ttbar', 'other']
        self.rf = r.TFile(self.fitfile, 'read')
        self.cardlist = ['cat1_'+self.year]

    def gethists(self, chan):
        print '////////////////////////////'
        print chan
        print '////////////////////////////'
        hists = {} 
        for proc in self.procs:
            print proc
            gROOT.cd()
            hist = self.rf.Get(chan+'_'+proc)
            print hist
            hist.GetEntries()
            hist.Sumw2()
            hists[proc] = hist                
        return hists

    def plot_settings(self, histname, plots):
        #top plot
        c = r.TCanvas("c","c",800,800)
        p1 = r.TPad("p1","p1", 0, 0.3, 1, 1.0)
        p1.SetBottomMargin(0.1)
        p1.Draw()
        p1.cd()

        stack = r.THStack("stack", "stack")
        legend = r.TLegend(0.1, 0.6, 0.3, 0.9)
        # stacktot = r.TH1F('stacktot', 'stacktot', len(self.pd.edges)-1, self.pd.edges)
        stacktot = r.TH1F('stacktot', 'stacktot',20, 0.0, 350.0)
        hcount = 0; hnames = []
        for proc, plot in plots.iteritems():
            if proc == self.sig:
                sighist = plot
                sighist.SetLineWidth(3)
                sighist.SetMarkerStyle(20)
                sighist.SetLineColor(r.kGray+2)
                legend.AddEntry(sighist, "signal", "L")           
                
            elif proc!=self.sig and proc!=self.data:
                plot.SetLineWidth(1)
                plot.SetFillColor(self.colors[proc])
                plot.SetLineColor(self.colors[proc])
                stack.Add(plot)
                stacktot.Add(plot)
                hnames.append(proc)
                legend.AddEntry(plot, hnames[hcount], "F")           
                hcount+=1

                
        #draw stack
        stack.SetTitle("")
        stack.Draw("hist")
        gPad.Modified()
        gPad.Update()
        ymax = p1.GetUymax()*1.6 #max+30%
        gPad.SetLogy()
        stack.SetMaximum(ymax)

        sighist.Draw("histsame")

        # stacktot = r.TGraphAsymmErrors(stacktot)
        stacktot.SetLineWidth(0) #dont show line
        stacktot.SetFillColor(r.kGray+2)
        stacktot.SetFillStyle(3002)
        stacktot.Draw("e2same")

        stack.GetYaxis().SetTitleSize(20)
        stack.GetYaxis().SetTitleFont(43)
        stack.GetYaxis().SetTitleOffset(1.55)
        stack.GetYaxis().SetTitle('NEntries')
        stack.GetXaxis().SetTitle(args.var)
        stack.GetYaxis().SetLabelFont(43)
        stack.GetYaxis().SetLabelSize(15)

        gPad.Modified()
        gPad.Update()

        legend.Draw()
        gPad.Modified()
        gPad.Update()

        #bottom plot
        c.cd()
        p2 = r.TPad("p2", "p2", 0, 0.05, 1, 0.3)
        p2.SetGridy()
        p2.Draw()
        p2.cd()

        ratio = sighist.Clone("ratio")
        ratio.SetLineColor(r.kBlack)
        ratio.Divide(stacktot) 
        ratio.SetMarkerStyle(20)

        raterr = sighist.Clone("raterr")
        raterr.SetLineWidth(0)
        raterr.SetFillColor(r.kGray+2)
        raterr.SetFillStyle(3002)
        raterr.SetMarkerStyle(1)
        raterr.SetMinimum(0.4)
        raterr.SetMaximum(1.6)

        #error bars
        for ibin in range(0, ratio.GetNbinsX()+2):
            derr = sighist.GetBinError(ibin)
            d = sighist.GetBinContent(ibin)
            relderr=0.0
            if d>0.0: relderr=derr/d

            err = stacktot.GetBinError(ibin)
            s = stacktot.GetBinContent(ibin)
            relerr=0.0
            if s>0:
                relerr = err/s

            raterr.SetBinError(ibin, relerr)
            ratio.SetBinError(ibin, relderr)
            raterr.SetBinContent(ibin, 1)
        
        #draw
        raterr.Draw("e2")
        # ratio.Draw("pe0same")
        l = r.TLine(p2.GetUxmin(), 1.0, p2.GetUxmax(), 1.0);
        l.SetLineColor(r.kBlack)
        l.SetLineWidth(1)
        l.Draw("same")

        raterr.SetTitle("")
        raterr.GetYaxis().SetTitle("ratio data/prediction")
        raterr.GetYaxis().SetNdivisions(505)
        raterr.GetYaxis().SetTitleSize(20)
        raterr.GetYaxis().SetTitleFont(43)
        raterr.GetYaxis().SetTitleOffset(1.55)
        raterr.GetYaxis().SetLabelFont(43)
        raterr.GetYaxis().SetLabelSize(15)
        raterr.GetXaxis().SetTitle(args.var)
        raterr.GetXaxis().SetTitleSize(20)
        raterr.GetXaxis().SetTitleFont(43)
        raterr.GetXaxis().SetTitleOffset(4.0)
        raterr.GetXaxis().SetLabelFont(43)
        raterr.GetXaxis().SetLabelSize(15)

        p2.SetTopMargin(0.1)
        p2.SetBottomMargin(0.2)
        gPad.Modified()
        gPad.Update()
        
        print 'saved histogram: ', self.outdir+histname+'.png'
        c.SaveAs(self.outdir+histname+'.png')        

    def rungraphs(self):
        for chan in self.cardlist:
            hists = self.gethists(chan)
            self.plot_settings(chan, hists)
            r.gROOT.Reset()
        #save
        self.rf.Close()

#run the thing
pf = postfit(args)
pf.rungraphs()
