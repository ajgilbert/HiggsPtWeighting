# Instructions

These steps have been tested on the CERN lxplus service using Scientific Linux 6 (SL6) and the bash shell. They should also work on other SL6 installations, but note that it is currently required that the CERN cvmfs service is mounted.

## Setting up the work area

Clone this repository via ssh using

    git clone git@github.com:ajgilbert/HiggsPtWeighting.git

or via https using

    git clone https://github.com/ajgilbert/HiggsPtWeighting.git
    
Switch to the `HiggsPtWeighting` directory and run a script that will download and compile POWHEG along with the gg_H_2HDM process:

    cd HiggsPtWeighting
    ./setup_powheg.sh

Source the `setup_env.sh` script to set various environment variables needed in subsequent steps:

    source setup_env.sh
    
This should be repeated for every fresh login.

## Step 1: LHE production with POWHEG
The `launch_jobs.py` script is provided, which steers each of the following steps and allows the user to choose which mass points to run, which reference tan(beta) values to set as well as a number of other options. For example, to run POWHEG and produce the LHE output files the following command could be used:

    python launch_jobs.py --step lhe -n 10000 -m 100,200 -H A:15 -c t:t,b:b,tb:tb,t:tb,b:tb \
      --pwhg-dir $PWD/POWHEG-BOX-V2/gg_H_2HDM \
      --job-mode condor --task-name lhe_step --sub-opts '+JobFlavour = "workday"'

The options are as follows:

 - `--step lhe`: Run the LHE production step
 - `-n 10000`: Produce 10k events
 - `-m 100,200`: Comma separated list of mass points to run
 - `-H A:15`: The Higgs boson to generate, and the reference tan(beta) value to use. Can specify more than one, e.g. `A:15,H:30`.
 - `-c t:t,b:b,tb:tb,t:tb,b:tb`: List of contribution:scale choices to generate, e.g. t:tb means generate top-only contribution at the Q_tb resummation scale. The values of the scales are given in the `scales-higgs-mass-scan.dat` file, with the format `MASS Qt Qb Qtb`.
 - `--pwhg-dir`: Path to the process directory to use, can be changed for debugging purposes.
 - The remaining settings control the job submission and are optional. By default each task will run interactively, one after another. But as these steps are typically CPU intensive it is useful to submit to a batch computing system. In this example jobs are submitted using the condor batch system at CERN. The `--sub-opts` option allows for additional lines to be added to the condor submit file that will be generated automatically.
 
 The input card used for POWHEG is `powheg.input`. This contains placeholders for the settings like mass, Higgs boson type and hfact value which should not be changed, but other settings can be changed as needed before running. The `launch_jobs.py` script will create a directory for each task, e.g. `A_100_15_t_tb`, corresponding to the `[HIGGS]_[MASS]_[TANB]_[CONTRIBUTION]_[SCALE]` settings used.

## Step 2: Hadronisation

Once the jobs of the previous step have completed successfully the next task is to interface these matrix element events to a parton shower and extract the resulting Higgs pT distribution. This step is in principle experiment-dependent, since CMS and ATLAS may use different parton-shower programs and/or different tunes. In the example here Pythia8 is used with the current CMS default tune, but it is possible to use an alternative. A small program `RunPythia` is provided which will shower the LHE events, and save the Higgs pT in a TTree in a ROOT file. First the program is compiled by running make:

    source setup_env.sh
    make

Again the `launch_jobs.py` script is used:

    python launch_jobs.py --step shower -n 10000 -m 100,200 -H A:15 -c t:t,b:b,tb:tb,t:tb,b:tb \
      --pwhg-dir $PWD/POWHEG-BOX-V2/gg_H_2HDM \
      --job-mode condor --task-name shower_step --sub-opts '+JobFlavour = "workday"' \
      --shower-cmd './RunPythia cms_pythia.cmnd'

The `--shower-cmd` option can be any exectuable. In this case the `RunPythia` program is used with the first option being a Pythia8 config file that sets the CMS default settings that are used with POWHEG. The `launch_jobs.py` scripts will append two further arguments: the input LHE file and the name of the output ROOT file that will be created, e.g.:

    ./RunPythia cms_pythia.cmnd A_100_15_t_t/pwgevents.lhe A_100_15_t_t/hpt.root
    
In this way an alternative program or script can be substituted if needed. The only requirements are that it accepts these two additional command line options and that the format of the output ROOT file matches what is expected in subsequent steps. Namely this means the `hpt.root` file should contain a single TTree named `hpt` with two `float` branches: `hpt` and `wt`, the values of the Higgs pT and the generator weight respectively.

## Step 3: 2HDM crosss section extraction
In preparation for the final step, the 2HDM cross sections are extracted from the POWHEG output of step 1:

    python launch_jobs.py --step xsec -n 10000 -m 100,200 -H A:15 -c t:t,b:b,tb:tb,t:tb,b:tb \
      --pwhg-dir $PWD/POWHEG-BOX-V2/gg_H_2HDM

The values are written into the file `xsec.json`, e.g.

~~~json
{
    "A_100_15_t_tb": [
        0.47318443630114509,
        0.0010791597320272816
    ]
}
~~~

where the two values correspond to the cross section and uncertainty respectively.

## Step 4: Building the reweighting workspace

*coming soon*
