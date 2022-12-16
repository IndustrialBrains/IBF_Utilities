[![GitIgnore](../../actions/workflows/GitIgnore.yml/badge.svg)](../../actions/workflows/GitIgnore.yml)

# Industrial Brainframe - Utilities library

This repo contains the Utilities library, and also a `.libcat.xml` file that can be used to add libraries to a library category. For more info, see [this post](https://alltwincat.com/2018/08/16/library-categories/) on AllTwinCAT.

## TODO

1. Fix errors generated when static analysis rule "Unused variables" is enabled
1. `GVL_Parameters.fbParameterHandler`:
	- parameter array has invalid element on index 1
	- test adding the same parameter continuously (was a bug, using wrong number)
	- test hitting max number of parameters
	- use FB_IterableList (add sort method?)
	- automatically add param using FB_init
1. `Fb_ParameterFileHandler`: 
	- test if parameter name with `;` break CSV file
	- do not fail on parameter file mismatch, just rewrite file and only throw error if that fails
1. Fault logging code: does not check remaining disk space
1. Add CSV writer for fault log (this functionality was removed after fault handler refactoring)
1.