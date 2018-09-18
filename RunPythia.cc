// Copyright (C) 2017 Torbjorn Sjostrand.
// PYTHIA is licenced under the GNU GPL version 2, see COPYING for details.
// Please respect the MCnet Guidelines, see GUIDELINES for details.

#include "Pythia8/Pythia.h"
#include "TFile.h"
#include "TTree.h"

#include <string>
#include <iostream>

using namespace Pythia8;
int main(int argc, char *argv[]) {

  
  if (argc < 4) {
    std::cout << "Not enough options specified, usage is: RunPythia [pythia cmnd file] [input file] [output file]" << std::endl;
    return 1;
  }
  
  std::string cmnd_file = argv[1];
  std::string lhe_input_file = argv[2];
  std::string tree_output_file = argv[3];

  TFile f(tree_output_file.c_str(), "RECREATE");
  TTree t("hpt", "hpt");

  float hpt = 0.;
  //float wt = 0.; Moving to vector definition in order to include multiple weights
  std::vector<float> wt;
  t.Branch("hpt", &hpt);
  t.Branch("wt", &wt);

  Pythia pythia;

  pythia.readFile(cmnd_file);

  // Initialize Les Houches Event File run. List initialization information.
  pythia.readString("Beams:frameType = 4");
  pythia.readString("Beams:LHEF = " + lhe_input_file);
  pythia.init();


  // Allow for possibility of a few faulty events.
  int nAbort = 10;
  int iAbort = 0;

  // Begin event loop; generate until none left in input file.
  for (int iEvent = 0; iEvent <= 1E7; ++iEvent) {

    // Generate events, and check whether generation failed.
    if (!pythia.next()) {

      // If failure because reached end of file then exit event loop.
      if (pythia.info.atEndOfFile()) break;

      // First few failures write off as "acceptable" errors, then quit.
      if (++iAbort < nAbort) continue;
      break;
    }

    bool found_last_higgs = false;
    int last_higgs_idx = -1;
    for (int i = 0; i < pythia.event.size(); ++i) {
      auto const& part = pythia.event[i];
      if (part.id() == 25 || part.id() == 35 || part.id() == 36) {
        // Found a Higgs boson
        if (part.daughterList().size() == 2 && std::abs(pythia.event[part.daughterList()[0]].id()) == 15 && std::abs(pythia.event[part.daughterList()[1]].id()) == 15) {
          if (found_last_higgs) {
            std::cout << "Found more than one last Higgs!\n";
          } else {
            //std::cout << "Found the last Higgs!\n";
            found_last_higgs = true;
            last_higgs_idx = i;
          }
        }
	//else{
	//  std::cout << "Higgs Daughters \n";
	//  for (int i = 0; i < part.daughterList().size(); ++i){
	//    std::cout << pythia.event[part.daughterList()[i]].id() << " \n";
	//  }
	//}
      }
    }
    if (!found_last_higgs) {
      std::cout << "Did not find the last Higgs!\n";
    } else {
      hpt = pythia.event[last_higgs_idx].p().pT();
      wt.clear();
      std::cout << "There are these many weights!"<<pythia.info.getWeightsDetailedSize()<<"\n";
      //for (int i = 0; i < pythia.info.nWeights(); i++){
      for (int i = 0; i < pythia.info.getWeightsDetailedSize(); i++){
	//wt.push_back(pythia.info.weight(i));
	//cout<< pythia.info.getWeightsDetailedValue(std::to_string(i));
	wt.push_back(pythia.info.getWeightsDetailedValue(std::to_string(i)));
	//std::cout << "weight number i="<<i<<"\n";

      }
      t.Fill();
    }
    if (iEvent % 100 == 0) {
      std::cout << "Processed " << iEvent << "events...\n";
    }
  }

  t.Write();
  f.Close();


  return 0;
}
