from pascalm import compile_pascal
import subprocess
import traceback
import sys

class CheatingStream:
  def __init__(self):
    self.__val = ''

  def write(self, c):
    self.__val += c

  def reset(self):
    self.__val = ''

  def val(self):
    return self.__val

class CheatingInStream:
  def __init__(self, val):
    self.val = val

  def readline(self):
    return '%s\n' % self.val

class TestCase:
  def __init__(self, filename, expected, in_stream = sys.stdin):
    self.filename = filename
    self.expected = expected
    self.in_stream = in_stream

out_stream = CheatingStream()

test_cases = [
  TestCase('write', 'AA'),
  TestCase('arithmetic', 'A'),
  TestCase('while', 'AAAAAAAAAAB'),
  TestCase('if', 'AD'),
  TestCase('array', 'A'),
  TestCase('record', 'AB'),
  TestCase('deep_array', 'A'),
  TestCase('nested_record', 'ABCD'),
  TestCase('long_assign', 'ABCDEFGHIJ'),
  TestCase('long_record_assign', 'ABC'),
  TestCase('proc', 'A'),
  TestCase('proc_vars', 'A'),
  TestCase('nested_proc', 'A'),
  TestCase('recursion', 'ABCDEFGHIJK'),
  TestCase('bitwise', '2\n1\n7\n4\n'),
  TestCase('lib/writeint_test', '12345'),
  TestCase('lib/abs_test', '11'),
  TestCase('long_return', 'ABCDEFGHIJ'),
  TestCase('early_return', 'A'), 
  TestCase('readtest', '\nA', CheatingInStream('65'))
]

subprocess.call(['gcc', '../interpreter.c', '-std=c99', '-Wall', '-pedantic', '-o', 'pascalvm'])

errors = []
c_errors = []

i = 0
for case in test_cases:
  i += 1
  if i % 10 == 0:
    print 'Ran %d/%d cases' % (i, len(test_cases))
  try: 
    compile_pascal('cases/%s.pm' % case.filename, 'dest', is_interpret = True, out_stream = out_stream, lib = ['..'], in_stream = case.in_stream)
    if out_stream.val() != case.expected:
      errors.append("Test case %s failed: Expected `%s`, found `%s`" % (case.filename, case.expected, out_stream.val()))

    output = subprocess.check_output(['./pascalvm', 'dest']);
    if output != case.expected:
      c_errors.append("Test case %s failed: Expected `%s`, found `%s`" % (case.filename, case.expected, output))
  except:
    errors.append('Caught exception in test case %s:\n  %s' % (case.filename, traceback.format_exc()))
  out_stream.reset()

print 'Ran %d cases' % len(test_cases)

if len(errors) > 0:
  print 'Found errors:'
  for error in errors:
    print error

if len(c_errors) > 0:
  print 'Found errors in the C vm:'
  for error in c_errors:
    print error

