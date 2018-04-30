#!/bin/bash

# Set the paths to the external tools we need
export GCC_DIR="/cvmfs/cms.cern.ch/slc6_amd64_gcc630/external/gcc/6.3.0"
export FASTJET_DIR="/cvmfs/cms.cern.ch/slc6_amd64_gcc630/external/fastjet/3.1.0"
export LHAPDF_DIR="/cvmfs/cms.cern.ch/slc6_amd64_gcc630/external/lhapdf/6.2.1-fmblme"
export PYTHIA8_DIR="/cvmfs/cms.cern.ch/slc6_amd64_gcc630/external/pythia8/230"
export ROOT_DIR="/cvmfs/cms.cern.ch/slc6_amd64_gcc630/lcg/root/6.10.08"
export TBB_DIR="/cvmfs/cms.cern.ch/slc6_amd64_gcc630/external/tbb/2018"
export XZ_DIR="/cvmfs/cms.cern.ch/slc6_amd64_gcc630/external/xz/5.2.2-oenich"
export PCRE_DIR="/cvmfs/cms.cern.ch/slc6_amd64_gcc630/external/pcre/8.37-oenich"
export CMSSW_DIR="/cvmfs/cms.cern.ch/slc6_amd64_gcc630/cms/cmssw/CMSSW_9_4_0/external/slc6_amd64_gcc630"

export PATH="${GCC_DIR}/bin${PATH:+:$PATH}"
export PATH="${FASTJET_DIR}/bin${PATH:+:$PATH}"
export PATH="${LHAPDF_DIR}/bin${PATH:+:$PATH}"

export LIBRARY_PATH="$PWD/POWHEG-BOX-V2/gg_H_2HDM/lib${LIBRARY_PATH:+:$LIBRARY_PATH}"
export LD_LIBRARY_PATH="$PWD/POWHEG-BOX-V2/gg_H_2HDM/lib${LD_LIBRARY_PATH:+:$LD_LIBRARY_PATH}"

export LD_LIBRARY_PATH="${GCC_DIR}/lib${LD_LIBRARY_PATH:+:$LD_LIBRARY_PATH}"
export LD_LIBRARY_PATH="${GCC_DIR}/lib64${LD_LIBRARY_PATH:+:$LD_LIBRARY_PATH}"
export LD_LIBRARY_PATH="${PYTHIA8_DIR}/lib${LD_LIBRARY_PATH:+:$LD_LIBRARY_PATH}"
export LD_LIBRARY_PATH="${TBB_DIR}/lib${LD_LIBRARY_PATH:+:$LD_LIBRARY_PATH}"
export LD_LIBRARY_PATH="${XZ_DIR}/lib${LD_LIBRARY_PATH:+:$LD_LIBRARY_PATH}"
export LD_LIBRARY_PATH="${PCRE_DIR}/lib${LD_LIBRARY_PATH:+:$LD_LIBRARY_PATH}"
export LD_LIBRARY_PATH="${CMSSW_DIR}/lib${LD_LIBRARY_PATH:+:$LD_LIBRARY_PATH}"

export LHAPDF_DATA_PATH="${LHAPDF_DIR}/share/LHAPDF"
export PYTHIA8DATA="${PYTHIA8_DIR}/share/Pythia8/xmldoc"

source ${ROOT_DIR}/bin/thisroot.sh

