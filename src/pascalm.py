import sys
import administration_functions
from administration_functions import reset, rewrite, read, close, debug, set_debug
from errors import Errors
from scanner import pass1
from parser import pass2
from assembler import pass3
from interpreter import interpret

def compile_pascal(source, dest, is_debug, is_interpret, out_stream):
  '''
  DID YOU KNOW that compile() is a built in function?
  '''
  set_debug(is_debug)
  administration_functions.debug("Compiling %s into %s" % (source, dest))
  reset(source)
  rewrite('temp1')
  pass1()
  close()
  debug('scanning complete')
  rewrite('temp2')
  pass2()
  close()
  debug('parsing complete')
  rewrite(dest)
  pass3()
  close()
  debug('assembly complete.' )
  if is_interpret:
    interpret(dest, out_stream)
  else:
    debug('run program now with `python interpreter.py %s`' % dest)


def main():
  source = sys.argv[1]
  dest = sys.argv[2]
  is_debug = '-d' in sys.argv or '--debug' in sys.argv
  interpret = '-i' in sys.argv or '--interpret' in sys.argv
  compile_pascal(source, dest, is_debug, interpret, sys.stdout)

if __name__ == '__main__':
  main()
