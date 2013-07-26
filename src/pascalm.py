import sys
from administration_functions import reset, rewrite, read, debug, close
from errors import Errors
from scanner import pass1
from parser import pass2
from assembler import pass3
from interpreter import interpret

def main():
  source = sys.argv[1]
  dest = sys.argv[2]
  if len(sys.argv) > 3:
    last_pass = sys.argv[3]
  else:
    last_pass = 'compile'
  debug("Compiling %s into %s" % (source, dest))
  reset(source)
  rewrite('temp1')
  pass1()
  close()
  debug('scanning complete')
  if last_pass.lower() == 'scan':
    return
  rewrite('temp2')
  pass2()
  close()
  debug('parsing complete')
  if last_pass.lower() == 'parse':
    return
  rewrite(dest)
  pass3()
  close()
  debug('assembly complete.' )
  if '-i' in sys.argv:
    interpret(dest)
  else:
    debug('run program now with `python interpreter.py %s`' % dest)

if __name__ == '__main__':
  main()
