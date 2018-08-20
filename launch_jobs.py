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
parser.add_argument('--variations', dest='variations', action='store_true')
parser.set_defaults(variations=False)


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
# See https://phystev.cnrs.fr/wiki/2013:groups:tools_lheextension for desctioption of reweighting format
variations = {
    "NOMINAL": ['0','1',"NOMINAL","NOMINAL","none"], #"compute_rwgt,lhrwgt_id,lhrwgt_descr,lhrwgt_group_name,lhrwgt_group_combine", 
    "resup": ['0','2',"mu_res=.5","mu_res_variation","envelope"],
}


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
        pwhg_cfg = pwhg_cfg.replace('{NOMINAL}', variations['NOMINAL'][0])
        pwhg_cfg = pwhg_cfg.replace('{ID}', variations['NOMINAL'][1])
        pwhg_cfg = pwhg_cfg.replace('{DESCR}', variations['NOMINAL'][2])
        pwhg_cfg = pwhg_cfg.replace('{GROUPNAME}', variations['NOMINAL'][3])
        pwhg_cfg = pwhg_cfg.replace('{COMBINE}', variations['NOMINAL'][4])

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

            cmd = base_cmd
            cmd += 'pushd %s; %s/pwhg_main powheg.input' % (key, args.pwhg_dir)
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

