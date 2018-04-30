
CXX=g++
CXXFLAGS=-std=c++14

main: RunPythia

RunPythia: RunPythia.cc
		$(CXX) $(CXXFLAGS) $^ -o $@ -I${PYTHIA8_DIR}/include -I$(shell root-config --incdir) $(shell root-config --libs) -L${CMSSW_DIR}/lib -lpythia8 -ltbb -llzma -lpcre -lpcreposix
clean:
	  rm RunPythia
