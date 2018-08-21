from jobs import Jobs
import argparse
import os
import ROOT
import json
from array import array
from itertools import product

job_mgr = Jobs()
parser = argparse.ArgumentParser()

parser.add_argument('--pwhg-dir', default='.')
parser.add_argument('-n', '--nevents', default=10000, type=int)
parser.add_argument('-m', '--mass', default='500')
parser.add_argument('-c', '--contribution', default='t:t')
parser.add_argument('-H', '--higgs-tanb', default='H:15')
parser.add_argument('--step', default='none', choices=['none', 'lhe', 'xsec', 'shower', 'workspace'])
parser.add_argument('--shower-cmd', default='./RunPythia cms_pythia.cmnd')
parser.add_argument('--dovariations', dest='dovariations', action='store_true')
parser.set_defaults(dovariations=False)


job_mgr.attach_job_args(parser)
args = parser.parse_args()
job_mgr.set_args(args)


higgstype = {
    's': '1',
    'H': '2',
    'A': '3'
    }

higgs_pdg = {
        's': '25',
        'H': '35',
        'A': '36'
        }

class Variations(object):
    rwgt_id                ='ID'
    descr             ='Description'
    group_name        ='GROUPNAME'
    group_combine     ='COMBINE'
    rensfact = '1'
    facsfact = '1'
    hfactscale = 1
    def __init__(self,rwgt_id,descr,group_name,group_combine,rensfact, facsfact, hfactscale):
        self.rwgt_id       = rwgt_id          
        self.descr         = descr            
        self.group_name    = group_name       
        self.group_combine = group_combine
        self.rensfact =  rensfact
        self.facsfact =  facsfact
        self.hfactscale =  hfactscale
# See https://phystev.cnrs.fr/wiki/2013:groups:tools_lheextension for desctioption of reweighting format
variations = [
    Variations(rwgt_id='1',descr="mu_res=0.5",    group_name="mu_res_variation",  group_combine="envelope",rensfact = '1', facsfact = '1', hfactscale = 0.5),
    Variations(rwgt_id='2',descr="mu_res=2",      group_name="mu_res_variation",  group_combine="envelope",rensfact = '1', facsfact = '1', hfactscale = 2),
    Variations(rwgt_id='3',descr="mu_F=mu_R=0.5", group_name="mu_scale_variation",group_combine="envelope",rensfact = '0.5', facsfact = '0.5', hfactscale = 1),
    Variations(rwgt_id='4',descr="mu_F=mu_R=0.25",group_name="mu_scale_variation",group_combine="envelope",rensfact = '0.25', facsfact = '0.25', hfactscale = 1)
]

# Fuctions which takes care of altering input file for uncertainty variations
def writeVariationFiles(key=None,hfac=None):
    for var in variations:
        with open(os.path.join(key,'powheg.input')) as pwhg_file:
            pwhg_cfg = pwhg_file.read()
        cfg = pwhg_cfg
        cfg = cfg.replace('compute_rwgt', 'compute_rwgt 1 !')
        cfg = cfg.replace('lhrwgt_id'                ,'lhrwgt_id \''+var.rwgt_id+"\' !")                
        cfg = cfg.replace('lhrwgt_descr'             ,'lhrwgt_descr \''             +var.descr+"\' !")
        cfg = cfg.replace('lhrwgt_group_name'        ,'lhrwgt_group_name \''        +var.group_name+"\' !")
        cfg = cfg.replace('lhrwgt_group_combine'     ,'lhrwgt_group_combine \''     +var.group_combine+"\' !")
        cfg = cfg.replace('#renscfact','renscfact '+var.rensfact+" !")
        cfg = cfg.replace('#facscfact','facscfact '+var.facsfact+" !")
        cfg = cfg.replace('hfact','hfact '+str(int(round(var.hfactscale*hfac)))+" !") # multiply hfac by scale, and update config
        
        with open(os.path.join(key,'powheg'+var.rwgt_id+'.input'), "w") as outfile:
            outfile.write(cfg)




mvec = []
qt = []
qb = []
qtb = []

with open('scales-higgs-mass-scan.dat') as scales_file:
    for line in scales_file:
        m, ht, hb, htb = line.split()
        mvec.append(float(m))
        qt.append(float(ht))
        qb.append(float(hb))
        qtb.append(float(htb))
gr = {}
gr['t'] = ROOT.TGraph(len(mvec), array('d', mvec), array('d', qt))
gr['b'] = ROOT.TGraph(len(mvec), array('d', mvec), array('d', qb))
gr['tb'] = ROOT.TGraph(len(mvec), array('d', mvec), array('d', qtb))

for pars in product(args.higgs_tanb.split(','), args.mass.split(','), args.contribution.split(',')):
    HIGGS, TANB = pars[0].split(':') 
    MASS = pars[1]
    CONT, SCALE = pars[2].split(':')

    if args.step in ['lhe', 'xsec', 'shower']:

        with open('powheg.input') as pwhg_file:
            pwhg_cfg = pwhg_file.read()

        pwhg_cfg = pwhg_cfg.replace('{EVENTS}', str(args.nevents))
        pwhg_cfg = pwhg_cfg.replace('{MASS}', MASS)
        pwhg_cfg = pwhg_cfg.replace('{TANB}', TANB)
        pwhg_cfg = pwhg_cfg.replace('{HIGGSTYPE}', higgstype[HIGGS])

        base_cmd = ''

        key = '%s_%s_%s_%s_%s' % (HIGGS, MASS, TANB, CONT, SCALE)
        
        if args.step == 'lhe':
            cfg = pwhg_cfg
            cfg = cfg.replace('{HFACT}', str(int(round(gr[SCALE].Eval(float(MASS))))))
            if CONT == 't':
                cfg += 'nobot 1\n'
            if CONT == 'b':
                cfg += 'notop 1\n'
        
            os.system('mkdir -p %s' % key)

            with open(os.path.join(key,'powheg.input'), "w") as outfile:
                outfile.write(cfg)
            if args.dovariations:
                writeVariationFiles(key,gr[SCALE].Eval(float(MASS)))
            cmd = base_cmd
            cmd += 'pushd %s; %s/pwhg_main powheg.input' % (key, args.pwhg_dir)
            cmd += '; cp powheg.input powheg0.input' # keep a seperate copy of the nominal powheg input file
            if args.dovariations:
                for var in variations:
                    cmd += '; cp powheg%s.input powheg.input' % (var.rwgt_id)
                    cmd += '; %s/pwhg_main powheg.input' % (args.pwhg_dir)
                    cmd += "; mv pwgevents-rwgt.lhe pwgevents.lhe"
            cmd += '; popd'
            job_mgr.job_queue.append(cmd)
        
        if args.step == 'xsec':
            js = {}
            if os.path.isfile('xsec.json'):
                with open('xsec.json') as jsonfile:
                    js = json.load(jsonfile)
            with open('%s/pwg-stat.dat' % key) as xsec_file:
                for line in xsec_file:
                    splitline = line.split()
                    if splitline[0] == 'total':
                        xsec = float(splitline[-3])
                        err = float(splitline[-1])
                        print '%s: %.3f +/- %.5f' % (key, xsec, err)
                        js[key] = [xsec, err]
            with open('xsec.json', 'w') as outfile:
                json.dump(js, outfile, sort_keys=True, indent=4, separators=(',', ': '))
        
        if args.step == 'shower':
            job_mgr.job_queue.append('%s %s/pwgevents.lhe %s/hpt.root' % (args.shower_cmd, key, key))
 
job_mgr.flush_queue()

