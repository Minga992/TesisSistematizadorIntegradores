/control/verbose 0
/run/verbose 0
/event/verbose 0
/tracking/verbose 0

##  SET NUMBER OF THREADS (will be ignored in case of sequential Geant4)
/run/numberOfThreads ${numberOfThreads}
/control/cout/prefixString G4Worker_


## To Switch off the field set it to 0 tesla
#/mydet/setField 4.0 tesla
/FSLdet/setField 4.0 tesla
## STEPPER CONFIG
# QSS Params
/QSS/selectStepper ${stepper}
/QSS/dQMin ${dQMin}
/QSS/dQRel ${dQRel}
/QSS/trialProposedStepModifier ${trialProposedStepModifier}


/run/initialize
/FSLgun/primaryPerEvt 2
/FSLgun/particle e-
/FSLgun/energy  100 GeV
####/FSLgun/direction  0 1 0
/run/beamOn ${beams}
/process/list
