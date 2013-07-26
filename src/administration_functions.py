import sys
from errors import Errors
from bytecodes import reverse_bytecodes, bytecodes

errors = False
line_no = 0
correct_line = True
input_file = None
output_file = None
eof = False
debug_mode = 'debug' in sys.argv

def debug(msg):
  if debug_mode:
    print msg

def get_code(filename):
  '''
  returns a list of opcodes
  '''
  f = open(filename)
  code = f.read()
  f.close()
  codes = []
  for c in code.strip().split(' '):
    try:
      codes.append(int(c))
    except ValueError:
      codes.append(bytecodes[c])
  return codes

def eof():
  return eof

def reset(filename):
  global eof, input_file
  eof = False
  input_file = open(filename, 'r')
  read.next_char = input_file.read(1)

def rewrite(filename):
  global output_file
  if output_file is not None:
    output_file.close()
  output_file = open(filename, 'w')

def read():
  global input_file, eof
  if eof:
    return None
  this_char = read.next_char
  read.next_char = input_file.read(1)
  if read.next_char == '':
    eof = True
  return this_char

def emit(val):
  output_file.write(str(val) + " ")

def emit_code_real(*args):
  for arg in args:
    output_file.write(str(arg) + " ") 

def emit_code_debug(*args):
  output_file.write(reverse_bytecodes[int(args[0])] + " ")
  for arg in args[1:]:
    output_file.write(str(arg) + " ")

if debug_mode:
  emit_code = emit_code_debug
else:
  emit_code = emit_code_real

def new_line(num):
  line_no = num
  correct_line = True

def close():
  global input_file, output_file
  if input_file is not None:
    input_file.close()
  if output_file is not None:
    output_file.close()


def error(error):
  global errors, correct_line
  if not errors:
    close()
    rewrite('notes')
    errors = True
  if correct_line:
    print 'Line %d' % line_no
    print error
    correct_line = False
