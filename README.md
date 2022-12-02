[![GitIgnore](../../actions/workflows/GitIgnore.yml/badge.svg)](../../actions/workflows/GitIgnore.yml)

# Industrial Brainframe - Utilities library

This repo contains the Utilities library, and also a `.libcat.xml` file that can be used to add libraries to a library category. For more info, see [this post](https://alltwincat.com/2018/08/16/library-categories/) on AllTwinCAT.

## TODO

### Generic repo / project wide

1. Add build action
1. Add automatic tests

### Improvements

1. `fbFaultHandler.CmdReset` will reset all bActXXX bits for one cycle, even if faults are still active
1. `fbFaultHandler.nActiveFaults` does not always match actual number of active faults (can be +1)
1. Fix errors generated when static analysis rule "Unused variables" is enabled
1. `GVL_Parameters.fbParameterHandler`: parameter array has invalid element on index 1
1. `Fb_ParameterFileHandler`: 
	- test if parameter name with `;` break CSV file
	- do not fail on parameter file mismatch, just rewrite file and only throw error if that fails
1. Fault logging code: does not check remaining disk space
