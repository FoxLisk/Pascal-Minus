from pascalm import compile_pascal
import subprocess

class CheatingStream:
  def __init__(self):
    self.__val = ''

  def write(self, c):
    self.__val += c

  def reset(self):
    self.__val = ''

  def val(self):
    return self.__val

stream = CheatingStream()

test_cases = [
  ('write', 'AA'),
  ('arithmetic', 'A'),
  ('while', 'AAAAAAAAAAB'),
  ('if', 'AD'),
  ('array', 'A'),
  ('record', 'AB'),
  ('deep_array', 'A'),
  ('nested_record', 'ABCD'),
  ('long_assign', 'ABCDEFGHIJ'),
  ('long_record_assign', 'ABC'),
  ('proc', 'A'),
  ('proc_vars', 'A'),
  ('nested_proc', 'A'),
  ('recursion', 'ABCDEFGHIJK')
]

subprocess.call(['gcc', '../interpreter.c', '-std=c99', '-Wall', '-pedantic', '-o', 'pascalvm'])

errors = []
c_errors = []

for fn, expected in test_cases:
  '''
  compile_pascal('cases/%s.pm' % fn, 'dest', False, True, stream)
  if stream.val() != expected:
    errors.append("Test case %s failed: Expected `%s`, found `%s`" % (fn, expected, stream.val()))
    '''
  try: 
    compile_pascal('cases/%s.pm' % fn, 'dest', is_interpret = True, out_stream = stream)
    if stream.val() != expected:
      errors.append("Test case %s failed: Expected `%s`, found `%s`" % (fn, expected, stream.val()))

    output = subprocess.check_output(['./pascalvm', 'dest']);
    if output != expected:
      c_errors.append("Test case %s failed: Expected `%s`, found `%s`" % (fn, expected, output))
  except Exception as e:
    errors.append('Caught exception in test case %s:\n  %s' % (fn, e.message))
  stream.reset()

if len(errors) > 0:
  print 'Found errors:'
  for error in errors:
    print error

if len(c_errors) > 0:
  print 'Found errors in the C vm:'
  for error in c_errors:
    print error

