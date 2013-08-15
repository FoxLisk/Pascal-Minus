* strings
* importing is fine, but really should probably be handled via linking rather than compile-time imports. low priority.
  update: linking is going to be a very big undertaking since symbol names are currently not preserved in compiled code - will require compilation units to be re-thought out a lot. my first idea is to simply start each file with some header information giving the offsets to each procedure, and then loading those in when we load the libraries, but I haven't thought through the details.
* array initializer literals
* for loop
* operator precedence should be taken more seriously
* error handling could be improved across the board
* I dont know C so probably that could be cleaned up a bit
* there should at least _maybe_ be dynamic allocation (esp. if we intend to make strings the least bit usable)
* functions with different signatures should be allowed
