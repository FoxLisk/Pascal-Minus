import sys
from errors import Errors

errors = False
emitting = True
line_no = 0
correct_line = True
input_file = None
output_file = None
eof = False

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
  if emitting:
    output_file.write(str(val) + " ")

def re_run():
  reset('temp2')
  emitting = True

def new_line(num):
  line_no = num
  correct_line = True

def close():
  global input_file
  input_file.close()

def error(error):
  global errors, emitting, correct_line
  if not errors:
    close()
    rewrite('notes')
    emitting = False
    errors = True
  if correct_line:
    print 'Line %d' % line_no
    print error
    correct_line = False

def test_limit(length, maximum):
  print 'Program Too Big'
  exit()

def delete(filename):
  pass #who cares
