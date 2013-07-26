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

compile_pascal('write.pm', 'dest', False, True, stream)
assert stream.val() == 'AA'
