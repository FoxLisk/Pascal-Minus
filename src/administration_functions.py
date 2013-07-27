import sys
from errors import Errors
from bytecodes import reverse_bytecodes, bytecodes, code_lengths

errors = False
line_no = 0
correct_line = True
input_file = None
output_file = None
eof = False
debug_mode = False

def set_debug(debug):
  global debug_mode
  debug_mode = debug

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

def prettify(bytecodes):
  pretty = []
  i = 0
  while i < len(bytecodes):
    op = bytecodes[i]
    l = code_lengths[op]
    pretty.append(reverse_bytecodes[op])
    for j in range(1, l):
      pretty.append(bytecodes[i + j])
    i += l
  return pretty
