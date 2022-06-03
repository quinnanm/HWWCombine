# revamped datacard dictionary
# before running I recommend saving dataframes as rootfiles with systematics appended to variable names as _nosys _jerUp _jes_Down etc
import numpy as np
from collections import OrderedDict
import ROOT as r

class datacardrefs:
    def __init__(self, year, chan):
        self.year = year
        self.chan = chan #ele, mu, had
        #shape systematics included  
        # systs = {'proc1':['syst1', 'syst2'], 
        #          'proc2':['syst1', 'syst2'],
        #          'proc3':['syst1', 'syst2']}
        # self.systs=systs

        #treename for accessing events
        self.tn = 'Events'
        #variable you are using for histograms/templates:
        self.var = 'fj_msoftdrop'
        tageff = {'had':{'signal':'*0.45',
                         'QCD'   :'*0.01',
                         'wjets' :'*0.02',
                         'ttbar' :'*0.04',
                         'other' :'*0.04',
                         'data'  :'*0.0'},
                  'ele':{'signal':'*0.40',
                         'QCD'   :'*0.002',
                         'wjets' :'*0.01',
                         'ttbar' :'*0.002',
                         'other' :'*0.002',
                         'data'  :'*0.0'},
                  'mu':{'signal':'*0.45',
                        'QCD'   :'*0.0003',
                        'wjets' :'*0.01',
                        'ttbar' :'*0.001',
                        'other' :'*0.001',
                        'data'  :'*0.0'}}
        self.tageff = tageff[self.chan]

        #histogram settings
        # self.edges = np.array([0.0, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.85, 0.9, 0.95,  1.0], dtype=np.double)
        self.nbins = 20
        self.selrange = [0.0, 350.0]

        lumi = {'2016':'35.92',
                '2017':'41.53',
                '2018':'59.74'}
        self.lumi = lumi[year]

        
        self.mcprocs = ['signal', 'QCD', 'wjets', 'ttbar', 'other']
        self.processes = ['signal', 'QCD', 'wjets', 'ttbar', 'other']
        # self.DDprocname = 'DDBKG'
        # self.processes=['proc1', 'proc2', 'proc3', self.DDprocname]
        
        # self.datafile = 'none'
        self.datafile = '/eos/uscms/store/user/mequinna/boostedhiggs/combinetest_23may22/merged/'+year+'/data_'+chan+'_merged.root'
        #leaving as example of rootfile location
        self.procfiles={'signal' :'/eos/uscms/store/user/mequinna/boostedhiggs/combinetest_23may22/merged/'+year+'/signal2_'+chan+'_merged.root',
                        'QCD'    :'/eos/uscms/store/user/mequinna/boostedhiggs/combinetest_23may22/merged/'+year+'/QCD_'+chan+'_merged.root',
                        'wjets'  :'/eos/uscms/store/user/mequinna/boostedhiggs/combinetest_23may22/merged/'+year+'/wjets_'+chan+'_merged.root',
                        'ttbar'  :'/eos/uscms/store/user/mequinna/boostedhiggs/combinetest_23may22/merged/'+year+'/ttbar_'+chan+'_merged.root',
                        'other'  :'/eos/uscms/store/user/mequinna/boostedhiggs/combinetest_23may22/merged/'+year+'/other_'+chan+'_merged.root'}
        
        metfilters   = ' && (goodverticesflag && haloflag && HBHEflag && HBHEisoflag && ecaldeadcellflag && badmuonflag)'
        if year=='2016':
            metfilters =  ' && (goodverticesflag && haloflag && HBHEflag && HBHEisoflag && ecaldeadcellflag && badmuonflag && eeBadScFilterflag)'
        self.metfilters = metfilters

        self.binsels =self.getbinsels()
        # self.mcsel = self.getsels('nosys',True)
        # self.datasel = self.getsels('nosys',False)

        
    #leaving as example
    def getsels(self, proc, systyp='nosys', isMC=True):
        # wgtstr = '*tot_weight'
        wgtstr = '*tot_weight'+self.tageff[proc]
        #preselection:
        basesel = 'fj_pt>=300.0'
        binsels = self.getbinsels()
        if not isMC:
            # sel = '('+basesel+')'#trigcorr
            sel = basesel
            return sel
        elif isMC:
            sel = ''+basesel+')'+wgtstr
            return sel

    # leaving for now as example of how SR categories are set up
    def getbinsels(self):
        binsels = {'cat1':'fj_msoftdrop>=0.0'}
        return binsels    

    def getyield(self, hist, verbose=False):
        errorVal = r.Double(0)
        minbin=0
        maxbin=hist.GetNbinsX()+2
        hyield = hist.IntegralAndError(minbin, maxbin, errorVal)
        if verbose:
            print('yield:', round(hyield, 3), '+/-', round(errorVal, 3), '\n')
        return hyield,  errorVal
    
    def fixref(self, rootfile, hist):
        hist.SetDirectory(0)
        rootfile.Close()

    def makeroot(self, infile, treename, options="read"):
        rfile = r.TFile(infile, options)
        tree = rfile.Get(treename)
        return rfile, tree
