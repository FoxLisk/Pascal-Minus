from errors import Errors
from administration_functions import error
from symbols import symbols, reverse_symbols
from first import first

integer_type = 1
boolean_type = 2

class Type(object):
  def __init__(self, name):
    self.name = name

class IntegerType(Type):
  def __init__(self, name):
    super(IntegerType, self).__init__(name)

class BooleanType(Type):
  def __init__(self, name):
    super(BooleanType, self).__init__(name)

class ArrayType(Type):
  def __init__(self, name, type_of, lower, upper):
    """
    type_of is the array that its a type of e.g.
      type myarray = array[2..11] of Integer
      would be called like
      ArrayType(myarray, Integer, 2, 11)
    """
    super(ArrayType, self).__init__(name)
    self.type_of = type_of
    self.lower = lower
    self.upper = upper

class RecordType(Type):
  def __init__(self, name, fields):
    '''
    fields should be a dict of the form
    { field_name: type_name }
    '''
    super(RecordType, self).__init__(name)
    self.fields = fields

class Constant:
  def __init__(self, name, type, value):
    self.name = name
    self.type = type
    self.value = value

class Variable:
  def __init__(self, name, type):
    self.name = name
    self.type = type

class Proc:
  def __init__(self, name, params):
    '''
    params should be a list of tuples of the form (name, type)
    '''
    self.name = name
    self.params = params

line_no = 0

current_symbol = None


#the standard types, Integer and Boolean, are 1 and 2
#the standard values, False and True, are 3 and 4
#the standard procs, Read and Write, are 5 and 6
scope = {'var': {}, 'const': {'False': Constant(3, 2, False), 'True': Constant(4, 2, False)},  'proc': {'Read': None, 'Write': None}, 'type': {'Integer': IntegerType(1), 'Boolean': BooleanType(2)}}

parsed_so_far = []

def error(msg):
  #print '  '.join(parsed_so_far)
  raise Exception(msg + ' on line %d' % line_no)

def push_scope():
  #print 'push_scope'
  global scope
  temp = scope
  scope = {'parent': temp, 'var': {}, 'const': {}, 'proc': {}, 'type': {}}

def pop_scope():
  #print 'pop_scope'
  global scope
  scope = scope['parent']

def get(t, name):
  '''
  t is the type: var, proc, const
  use get_type for type

  returns the saught value if found, or None
  '''
  global scope
  if name in scope[t]:
    return scope[t][name]
  temp = scope
  while 'parent' in temp:
    temp = temp['parent']
    if name in temp[t]:
      return temp[t][name]
  return None

def add_type(name, type):
  scope['type'][name] = type

def add_const(name, type, value):
  scope['const'][name] = Constant(name, type, value)

def add_var(name, type):
  scope['var'][name] = Variable(name, type)

def add_proc(name, params):
  scope['proc'][name] = Proc(name, params)

def _next_symbol():
  #print '_next_symbol'
  global line_no
  f = open('temp1')
  all_symbols = f.read()
  f.close()
  all_symbols = [s for s in all_symbols.split(' ') if s != '']
  is_nl = False
  is_name = False
  is_int = False
  for s in all_symbols:
    if is_nl:
      line_no = int(s)
      #print "found line #%d" % line_no
      is_nl = False
      continue
    if is_name:
      is_name = False
      yield s
      continue
    if is_int:
      is_int = False
      yield s
      continue
    symbol_type = reverse_symbols[s]
    if symbol_type == '\n':
      is_nl = True
      continue
    if symbol_type == 'numeral':
      is_int = True
      yield s
      continue
    if symbol_type == 'name':
      is_name = True
    else:
      is_name = False
    yield s

def next_symbol():
  #print 'next_symbol'
  global current_symbol, parsed_so_far
  try:
    track = True
    if check('name') or check('numeral'):
      track = False
    current_symbol = next_symbol.symbols.next()
    if track:
      parsed_so_far.append(reverse_symbols[current_symbol])
    return current_symbol
  except StopIteration:
    error('out of symbols')
next_symbol.symbols = _next_symbol()

def expect(symbol):
  code = symbols[symbol]
  if current_symbol != code:
    if current_symbol in reverse_symbols:
      error("Expected %s, found %s" % (symbol, reverse_symbols[current_symbol]))
    else:
      error("Expected %s, found unknown symbol %d" % (symbol, current_symbol))
  else:
    #print "found expected %s" % symbol
    next_symbol()

def check(symbol):
  code = symbols[symbol]
  return current_symbol == code

def program():
  #print 'program'
  expect('program')
  program_name = name()
  expect(';')
  block_body()
  expect('.')

def block_body():
  #print 'block_body'
  #print "in block body: current symbol: %s" % reverse_symbols[current_symbol]
  #print first('ConstantDefinitionPart')
  if current_symbol in first('ConstantDefinitionPart'):
    #print "trying constant definition part"
    constant_definition_part()
  if current_symbol in first('TypeDefinitionPart'):
    type_definition_part()
  if current_symbol in first('VariableDefinitionPart'):
    variable_definition_part()
  while current_symbol in first('ProcedureDefinition'):
    procedure_definition()
  compound_statement()

def procedure_definition():
  expect('procedure')
  proc_name = name()
  push_scope()
  procedure_block(proc_name)
  expect(';')
  pop_scope()

def procedure_block(proc_name):
  if check('('):
    #print "running parameter list"
    expect('(')
    params = formal_parameter_list()
    expect(')')

  add_proc(proc_name, params)
  expect(';')
  block_body()

def formal_parameter_list():
  params = parameter_definition()
  while check(';'):
    expect(';')
    params.append([x for x in parameter_definition()])
  return params

def parameter_definition():
  if check('var'):
    expect('var')
  return variable_group()

def variable_definition_part():
  #print 'variable_definition_part'
  expect('var')
  variable_definition()
  while current_symbol in first('VariableDefinition'):
    variable_definition()

def variable_definition():
  vars = variable_group()
  expect(';')
  return vars

def variable_group():
  names = []
  names.append(name())
  while check(','):
    expect(',')
    names.append(name())
  expect(':')
  t = name()
  #print 'variable group: name returned type %d' % t
  if not get('type', t):
    error("Trying to declare variables of undeclared type %s" % t)
  map(lambda name: add_var(name, t), names)
  ret = []
  for n in names:
    ret.append((n, t))
  return ret
  
def compound_statement():
  #print 'compound_statement'
  expect('begin')
  statement()
  while check(';'):
    next_symbol()
    statement()
  expect('end')

def statement():
  #print 'statement'
  if check('name'):
    name = next_symbol()
    next_symbol()
    if get('var', name):
      assignment_statement(name)
    elif get('proc', name):
      procedure_statement(name)
    else:
      #this is okay because, even though statements can be empty, a name cannot follow a statement
      #anywhere so if we find a name we dont need to backtrack - it's just game over
      error('Found a name not associated with a var or proc in a statement')
  elif check('if'):
    if_statement()
  elif check('while'):
    while_statement()
  elif check('begin'):
    compound_statement()

def assignment_statement(name):
  #print 'assignment_statement'
  #name has already been consumed in figuring out whether we're in
  #assignment or procedure statement
  #we now do something gross and mostly reproduce variable_access() here
  #because we have consumed name
  if not get('var', name):
    print 'Cannot assign to missing var'
  while current_symbol in first('Selector'):
    selector()
  expect(':=')
  expression()

def procedure_statement(proc_name):
  #print 'procedure_statement'
  #name has already been consumed in figuring out whether we're in
  #assignment or procedure statement
  if not get('proc', proc_name):
    error('trying to call nonexistent procedure')
  if check('('):
    expect('(')
    actual_parameter_list()
    expect(')')

def actual_parameter_list():
  actual_parameter()
  while check(','):
    expect(',')
    actual_parameter()

def actual_parameter():
  expression()

def if_statement():
  #print 'if_statement'
  expect('if')
  expression()
  expect('then')
  statement()
  if check('else'):
    expect('else')
    statement()

def while_statement():
  #print 'while_statement'
  expect('while')
  expression()
  expect('do')
  statement()

def constant_definition_part():
  #print 'constant_definition_part'
  expect('const')
  constant_definition()
  while current_symbol in first('ConstantDefinition'):
    constant_definition()

def constant_definition():
  #print 'constant_definition'
  const_name = name()
  expect('=')
  type, val = constant()
  expect(';')
  add_const(const_name, type, val)

def type_definition_part():
  #print 'type_definition_part'
  expect('type')
  type_definition()
  while current_symbol in first('TypeDefinition'):
    type_definition()

def type_definition():
  #print 'type_definition'
  type_name = name()
  expect('=')
  new_type(type_name)
  expect(';')

def new_type(type_name):
  #print 'new_type'
  if current_symbol in first('NewArrayType'):
    new_array_type(type_name)
  elif current_symbol in first('NewRecordType'):
    new_record_type(type_name)
  else:
    error("Expecting a type definition")

def new_record_type(type_name):
  #print 'new_record_type'
  expect("record")
  _field_list = field_list()
  fields = {}
  for names, type in _field_list:
    for name in names:
      fields[name] = type
  add_type(type_name, RecordType(type_name, fields))
  expect("end")

def field_list():
  #print 'field_list'
  records = []
  names, type = record_section()
  records.append((names, type))
  while check(';'):
    next_symbol()
    names, type = record_section()
    records.append((names, type))
  return records

def record_section():
  #print 'record_section'
  names = []
  field_name = name()
  names.append(field_name)
  while check(','):
    next_symbol()
    field_name = name()
    names.append(field_name)
  expect(':')
  type_name = name()
  return names, type_name

def expression():
  simple_expression()
  if current_symbol in first('RelationalOperator'):
    relational_operator()
    simple_expression()

def simple_expression():
  if current_symbol in first('SignOperator'):
    sign_operator()
  term()
  while current_symbol in first('AddingOperator'):
    adding_operator()
    term()

def relational_operator():
  if any(map(check, ['<', '=', '<=', '<>', '>='])):
    next_symbol()
  else:
    error('expected relational operator')

def sign_operator():
  if check('+') or check('-'):
    next_symbol()
  else:
    error('Expected sign operator')

def adding_operator():
  if check('+') or check('-') or check('or'):
    next_symbol()
  else:
    error('expected adding operator')

def term():
  factor()
  while current_symbol in first('MultiplyingOperator'):
    multiplying_operator()
    factor()

def multiplying_operator():
  if any(map(check, ['*', 'div', 'mod', 'and'])):
    next_symbol()
  else:
    error('expected multiplying operator')

def factor():
  if current_symbol in first('Constant'):
    constant()
  elif current_symbol in first('VariableAccess'):
    variable_access()
  elif check('('):
    expect('(')
    expression()
    expect(')')
  elif check('not'):
    expect('not')
    factor()

def name():
  expect('name')
  name = current_symbol
  next_symbol()
  return name

def numeral():
  #print 'numeral'
  expect('numeral')
  return next_symbol()

def new_array_type(type_name):
  #print 'new_array_type'
  expect('array')
  expect('[')
  lower, upper = index_range()
  expect(']')
  expect('of')
  type_of = name()
  add_type(type_name, ArrayType(type_name, type_of, lower, upper))

def index_range():
  #print 'index_range'
  lower = constant()
  expect('..')
  upper = constant()
  return lower, upper

def constant():
  #print 'constant'
  if current_symbol in first('Numeral'):
    constant = numeral()
    return get('type', integer_type), constant
  elif current_symbol in first('Name'):
    constant_name = name()
    constant = get('const', constant_name)
    if constant is None:
      error('Failed to find constant %s in scope' % constant_name)
    return constant.type, constant.value
  else:
    error("Expecting a constant - either a Numeral or a named constant")
    
def pass2():
  next_symbol()
  program()
