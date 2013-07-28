from pascalm import compile_pascal

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

compile_pascal('cases/write.pm', 'dest', False, True, stream)
assert stream.val() == 'AA', stream.val()
stream.reset()

compile_pascal('cases/arithmetic.pm', 'dest', False, True, stream)
assert stream.val() == 'A', stream.val()
stream.reset()

compile_pascal('cases/while.pm', 'dest', False, True, stream)
assert stream.val() == 'AAAAAAAAAAB', stream.val()
stream.reset()

compile_pascal('cases/if.pm', 'dest', False, True, stream)
assert stream.val() == 'AD', stream.val()
stream.reset()

compile_pascal('cases/array.pm', 'dest', False, True, stream)
assert stream.val() == 'A', stream.val()
stream.reset()

compile_pascal('cases/record.pm', 'dest', False, True, stream)
assert stream.val() == 'AB', stream.val()
stream.reset()

compile_pascal('cases/deep_array.pm', 'dest', False, True, stream)
assert stream.val() == 'A', stream.val()
stream.reset()

compile_pascal('cases/nested_record.pm', 'dest', False, True, stream)
assert stream.val() == 'ABCD', stream.val()
stream.reset()

compile_pascal('cases/long_assign.pm', 'dest', False, True, stream)
assert stream.val() == 'ABCDEFGHIJ', stream.val()
stream.reset()

compile_pascal('cases/long_record_assign.pm', 'dest', False, True, stream)
assert stream.val() == 'ABC', stream.val()
stream.reset()

