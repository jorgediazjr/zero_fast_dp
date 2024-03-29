# Fast DP: Fast Data Processsing with XDS

## 0. Introduction

Fast DP is a small Python program which uses XDS, CCP4 & CCTBX to deliver
data processing results very quickly: quite how quickly will depend on the
operating environment. In essence, the first image in the sweep is passed
to the program, it's header read and then XDS used to index with a triclinic
lattice using spots drawn from small wedges of data around the start, 45
degrees in and 90 degrees in (or as close as possible to this). Integration
is then performed in parallel, either using multiple cores or multiple
processors if the XDS forkintegrate script is appropriately configured. The
data are then scaled with XDS, still in P1, before analysis with Pointless.
Finally the analysis from Pointless and the global postrefinement results
from the XDS CORRECT step are then used to select a pointgroup, after which
the data are re-scaled with XDS in this pointgroup and merged with Aimless.

At Diamond Light Source, using an appropriately configured cluster with a
parallel file store, this process typically takes up to two minutes for any
number of images.

Usage:

```
fast_dp -h
Usage: fast_dp.py [options]

Options:
  -h, --help            show this help message and exit
  -b BEAM, --beam=BEAM  Beam centre: x, y (mm)
  -d DISTANCE, --distance=DISTANCE
                        Detector distance: d (mm)
  -a ATOM, --atom=ATOM  Atom type (e.g. Se)
  -j NUMBER_OF_JOBS, --number-of-jobs=NUMBER_OF_JOBS
                        Number of jobs for integration
  -J MAXIMUM_NUMBER_OF_JOBS, --maximum-number-of-jobs=MAXIMUM_NUMBER_OF_JOBS
                        Maximum number of jobs for integration
  -k NUMBER_OF_CORES, --number-of-cores=NUMBER_OF_CORES
                        Number of cores (theads) for integration
  -l PLUGIN_LIBRARY, --lib=PLUGIN_LIBRARY
                        image reader plugin path, ending with .so
  -e CLUSTER_NODES, -n CLUSTER_NODES, --execution-hosts=CLUSTER_NODES, --cluster-nodes=CLUSTER_NODES
  -c CELL, --cell=CELL  Cell constants for processing, needs spacegroup
  -s SPACEGROUP, --spacegroup=SPACEGROUP
                        Spacegroup for scaling and merging
  -1 FIRST_IMAGE, --first-image=FIRST_IMAGE
                        First image for processing
  -N LAST_IMAGE, --last-image=LAST_IMAGE
                        Last image for processing
  -r RESOLUTION_HIGH, --resolution-high=RESOLUTION_HIGH
                        High resolution limit
  -R RESOLUTION_LOW, --resolution-low=RESOLUTION_LOW
                        Low resolution limit
```
Conventional usage, e.g. on laptop, would be e.g:
```
fast_dp ~/data/i04-BAG-training/th_8_2_0001.cbf
```

giving the following output on a 2011 Macbook Pro:
```
Fast_DP installed in: /Users/graeme/svn/fast_dp
Starting image: /Users/graeme/data/i04-BAG-training/th_8_2_0001.cbf
Number of jobs: 1
Number of cores: 0
Processing images: 1 -> 540
Phi range: 82.00 -> 163.00
Template: th_8_2_####.cbf
Wavelength: 0.97625
Working in: /private/tmp/fdp
All autoindexing results:
Lattice      a      b      c  alpha   beta  gamma
     tP  57.80  57.80 150.00  90.00  90.00  90.00
     oC  81.80  81.70 150.00  90.00  90.00  90.00
     oP  57.80  57.80 150.00  90.00  90.00  90.00
     mC  81.80  81.70 150.00  90.00  90.00  90.00
     mP  57.80  57.80 150.00  90.00  90.00  90.00
     aP  57.80  57.80 150.00  90.00  90.00  90.00
Mosaic spread: 0.04 < 0.06 < 0.07
Happy with sg# 89
 57.80  57.80 150.00  90.00  90.00  90.00
--------------------------------------------------------------------------------
      Low resolution  28.89  28.89   1.37
     High resolution   1.34   5.99   1.34
              Rmerge  0.062  0.024  0.420
             I/sigma  13.40  44.70   1.60
        Completeness   99.6   98.9   96.1
        Multiplicity    5.3    5.0    2.8
  Anom. Completeness   96.5  100.0   71.4
  Anom. Multiplicity    2.6    3.1    1.2
   Anom. Correlation   99.9   99.9   76.0
               Nrefl 306284   3922  11217
             Nunique  57886    786   4030
           Mid-slope  1.007
                dF/F  0.075
          dI/sig(dI)  0.823
--------------------------------------------------------------------------------
Merging point group: P 4 2 2
Unit cell:  57.78  57.78 150.01  90.00  90.00  90.00
Processing took 00h 03m 59s (239 s) [306284 reflections]
RPS: 1277.6
```

The main result is the file fast_dp.mtz containing the scaled and merged
intensities, a log file from Aimless for plotting the merging statistics
and the information above in fast_dp.log.

See also fast_rdp to rerun last steps to change choices.

If you find fast_dp useful please cite 10.5281/zenodo.13039 as a DOI for the
source code and / or:

	Winter, G. & McAuley, K. E. "Automated data collection for macromolecular
	crystallography." Methods 55, 81-93, doi:10.1016/j.ymeth.2011.06.010 (2011).

Please also cite XDS, CCTBX & CCP4:

	Kabsch, W. "XDS." Acta Cryst. D66, 125-132 (2010)

	R. W. Grosse-Kunstleve, N. K. Sauter, N. W. Moriarty and P. D. Adams
	"The Computational Crystallography Toolbox: crystallographic algorithms
	in a reusable software framework" J. Appl. Cryst. (2002). 35, 126-136

	M. D. Winn et al. "Overview of the CCP4 suite and current developments"
	Acta. Cryst. D67, 235-242 (2011)

## 1. Dependencies

fast_dp depends on:

 * XDS
 * CCP4
 * CCTBX

If all of these are installed and configured no further work is needed. For
parallel operation in integration a forkintegrate script is needed to send
jobs to your queuing system.

## 2. Installation

Provided that the dependencies are all satisfied and the programs are on the
PATH, all that is necessary is to unpack the fast_dp tarball and place the
bin directory found therein into your PATH.

Optionally, you may manage paths or other initialization, by creating 
/etc/fast_dp/fast_dp.ini or $HOME/.fast_dp/fast_dp.ini, for example to set
paths to find xds.

## 3. Assumptions

The XDS.INP files generated by fast_dp make the following assumptions:

 * All scans are about a single axis, approximately parallel to the detector
   "fast" axis (multi-axis goniometers are fine provided the axis for the
   scan is fixed)
 * The detector is not offset in two-theta i.e. the beam is approximately
   perpendicular to the detector face.
 * Currently templates are included for Pilatus 2M & 6M, ADSC and Rayonix CCD
   detectors - modification to other detectors may be possible.

## 4. Support

fast_dp is provided with no guarantee of support however "best effort" support
will be provided on contacting scientificsoftware@diamond.ac.uk. Users may be
asked to provide example data in the event of a bug report.

## 5. Acknowledgements

fast_dp was developed at Diamond Light Source with the specific purpose of
providing feedback to users about the merging statistics of their data in the
shortest possible time. Clearly, however, it is very much dependent on XDS
and it's intrinsic parallelisation as well as CCP4 and CCTBX to operate, and
without these fast_dp could not exist.

## 6. License

Copyright 2014 Diamond Light Source

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
