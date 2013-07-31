import sys
from administration_functions import reset, rewrite, close, debug, set_debug, prettify
from errors import Errors
from scanner import Scanner
from parser import Parser
from assembler import Assembler
from interpreter import Interpreter

def write(codes, filename):
  f = open(filename, 'w')
  for c in codes:
    f.write(str(c) + " ")
  f.close()

def compile_pascal(source, dest, is_debug = False, is_interpret = False, out_stream = sys.stdout, output_tokens = False, output_bytecodes = False):
  '''
  DID YOU KNOW that compile() is a built in function?
  '''
  set_debug(is_debug)
  debug("Compiling %s into %s" % (source, dest))
  scanner = Scanner(source)
  tokens = scanner.scan()
  if output_tokens:
    write(tokens, source + "_tokenized")
  debug('scanning complete')
  parser = Parser(tokens)
  bytecodes = parser.parse()
  if output_bytecodes:
    if is_debug:
      write(prettify(bytecodes), source + "_unassembled")
    else:
      write(bytecodes, source + "_unassembled")
  debug('parsing complete')
  assembler = Assembler(bytecodes)
  assembled = assembler.assemble()
  if is_debug:
    write(prettify(assembled), dest)
  else:
    write(assembled, dest)
  debug('assembly complete.' )
  if is_interpret:
    interp = Interpreter(out_stream, code = assembled)
    interp.interpret()
  else:
    debug('run program now with `python interpreter.py %s`' % dest)

def main():
  source = sys.argv[1]
  is_debug = '-d' in sys.argv or '--debug' in sys.argv
  interpret = '-i' in sys.argv or '--interpret' in sys.argv
  output_tokens = '-t' in sys.argv or '--tokens' in sys.argv
  output_bytecodes = '-b' in sys.argv or '--bytecodes' in sys.argv
  dest = source + 'c'
  if '-o' in sys.argv:
    i = sys.argv.index('-o') + 1
    if i < len(sys.argv):
      dest = sys.argv[i]

  compile_pascal(source, dest, is_debug, interpret, sys.stdout, output_tokens, output_bytecodes)

if __name__ == '__main__':
  main()
