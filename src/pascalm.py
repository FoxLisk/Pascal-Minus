import sys
from scanner import pass1
from administration_functions import reset, rewrite, read, debug
from errors import Errors
from parser import pass2
from assembler import pass3

def main():
  source = sys.argv[1]
  dest = sys.argv[2]
  if len(sys.argv) > 3:
    last_pass = sys.argv[3]
  else:
    last_pass = 'compile'
  print "Compiling %s into %s" % (source, dest)
  reset(source)
  rewrite('temp1')
  pass1()
  print 'scanning complete'
  if last_pass.lower() == 'scan':
    return
  rewrite('temp2')
  pass2()
  print 'parsing complete'
  if last_pass.lower() == 'parse':
    return
  rewrite(dest)
  pass3()
  print 'assembly complete. run program now with `python interpreter.py %s`' % dest

if __name__ == '__main__':
  main()
