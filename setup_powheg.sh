#!/bin/bash
set -e
set -x

POWHEG_VERSION="3511"

source setup_env.sh

svn checkout --no-auth-cache --revision ${POWHEG_VERSION} --username anonymous --password anonymous svn://powhegbox.mib.infn.it/trunk/POWHEG-BOX-V2

pushd POWHEG-BOX-V2
  svn co --no-auth-cache --revision ${POWHEG_VERSION} --username anonymous --password anonymous svn://powhegbox.mib.infn.it/trunk/User-Processes-V2/gg_H_2HDM

  pushd gg_H_2HDM
    wget --no-verbose http://chaplin.hepforge.org/code/chaplin-1.2.tar
    tar xvf chaplin-1.2.tar
    pushd chaplin-1.2
      ./configure --prefix=`pwd`/..
      make install
    popd
    
    make pwhg_main
  popd

popd

