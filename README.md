HiggsAnalysis-CombinedLimit
===========================

### Official documentation

[Manual to run combine](http://cms-analysis.github.io/HiggsAnalysis-CombinedLimit/)

### Setting up the environment and installation

```
# Setting up the environment (once):
export SCRAM_ARCH=slc7_amd64_gcc700
cmsrel CMSSW_10_2_13
cd CMSSW_10_2_13/src
cmsenv

#clone with ssh
git clone git@github.com:quinnanm/HWWCombine.git ./HiggsAnalysis/CombinedLimit
cd HiggsAnalysis/CombinedLimit

# make a clean build
scramv1 b clean; scramv1 b -j8 
```

### Making datacards

The directory /HWW_scripts/ contains newautodatacards.py, newhistmaker.py, and datacardrefs.py. The code for example to run datacards for all three years (I usually use screens) and put them in the directory ./datacards_dir/ is for example:

```
cd $CMSSW_BASE//src/HiggsAnalysis/CombinedLimit/HWW_scripts
python newautodatacards.py -o ./datacards_dir/ -y 2016
python newautodatacards.py -o ./datacards_dir/ -y 2017
python newautodatacards.py -o ./datacards_dir/ -y 2018
```

Note settings for the datacards need to be specified (mainly in datacardrefs.py).


### Useful combine commands 

Here are various useful commands for use in your combine directory.

For blinded (expected) results:

```
#for limits/significance

combineCards.py /DATACARD_DIR//*.txt > NAME_datacard.txt
combine -M AsymptoticLimits --run expected -d allhad4top_datacard.txt -t -1  -v 1 --expectSignal 1
combine -M Significance -d allhad4top_datacard.txt -t -1 --expectSignal 1

#for impacts: (m doesnt matter, but if running many impacts at once use different numbers)

python runHWWcombine.py -i /DATACARD_DIR/*.txt
text2workspace.py allhad4top_RunII_datacard.txt -o NAME_workspace.root
combineTool.py -M Impacts -d NAME_workspace.root --rMin -1 --rMax 2 --robustFit 1 --doInitialFit --expectSignal 1 -m 2 -t -1
combineTool.py -M Impacts -d NAME_workspace.root --rMin -1 --rMax 2 --robustFit 1 --doFits -m 2 --expectSignal 1 -t -1 --parallel 50
combineTool.py -M Impacts -d NAME_workspace.root --rMin -1 --rMax 2 --robustFit 1 --output impacts.json -m 2 --expectSignal 1 -t -1
plotImpacts.py -i impacts.json -o impacts

```

For unblinded (observed) results:

```
#for limits/significance

combineCards.py /DATACARD_DIR//*.txt > NAME_datacard.txt
combine -M AsymptoticLimits -d allhad4top_datacard.txt
combine -M Significance -d allhad4top_datacard.txt

#for impacts: (m doesnt matter, but if running many impacts at once use different numbers)

python runHWWcombine.py -i /DATACARD_DIR/*.txt
text2workspace.py allhad4top_RunII_datacard.txt -o NAME_workspace.root
combineTool.py -M Impacts -d NAME_workspace.root  --robustFit 1 --doInitialFit -m 2 
combineTool.py -M Impacts -d NAME_workspace.root  --robustFit 1 --doFits -m 2 --parallel 50
combineTool.py -M Impacts -d NAME_workspace.root--robustFit 1 --output impacts.json -m 2
plotImpacts.py -i impacts.json -o impacts

#for postfit distributions and fit to signal

python runHWWcombine.py -i /DATACARD_DIR/*.txt
text2workspace.py allhad4top_RunII_datacard.txt -o NAME_workspace.root
combine -M FitDiagnostics NAME_workspace.root -m 2 --saveShapes --saveWithUncertainties  --robustFit 1  -v 3 
mv fitDiagnostics.root fitDiagnostics_NAME.root

#for goodness of fit test statistic distributions
#for example for 100 toys, random seed of 1, output rootfile higgsCombineTest.GoodnessOfFit.mH120.1.root for toys

combine -M GoodnessOfFit NAME_datacard.txt --algo=saturated
combine -M GoodnessOfFit NAME_datacard.txt --algo=saturated -t 100 -s 1

```
