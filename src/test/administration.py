import sys
from scanner import pass1
from administration_functions import reset, rewrite, delete, read
from errors import Errors
from parser import pass2

def main():
  source = sys.argv[1]
  code = sys.argv[2]
  if len(sys.argv) > 3:
    last_pass = sys.argv[3]
  else:
    last_pass = 'compile'
  print "Compiling %s into %s" % (source, code)
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
  #delete('temp1')
  #reset('temp2')
  #rewrite(code)
  #pass3()
  #delete('temp2')

if __name__ == '__main__':
  main()
