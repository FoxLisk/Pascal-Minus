from errors import Errors
from administration_functions import error
from symbols import symbols, reverse_symbols
from first import first

integer_type = 1
boolean_type = 2

class Type(object):
  def __init__(self, name):
    self.name = name
    self.is_record = False
    self.is_array = False

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
    self.is_array = True

class RecordType(Type):
  def __init__(self, name, fields):
    '''
    fields should be a dict of the form
    { field_name: type_name }
    '''
    super(RecordType, self).__init__(name)
    self.fields = fields
    self.is_record = True

class Constant:
  def __init__(self, name, type, value):
    self.name = name
    self.type = type
    self.value = value

class Variable:
  def __init__(self, name, type):
    self.name = name
    self.type = type

class Parameter:
  def __init__(self, name, type, is_var):
    self.name = name
    self.type = type
    self.is_var = is_var

class Proc:
  def __init__(self, name, params):
    '''
    params should be a list of Parameter objects
    '''
    self.name = name
    self.params = params

line_no = 0

current_symbol = None


#the standard types, Integer and Boolean, are 1 and 2
#the standard values, False and True, are 3 and 4
#the standard procs, Read and Write, are 5 and 6
scope = {'var': {}, 'const': {'False': Constant(3, 2, False), 'True': Constant(4, 2, False)},  'proc': {'Read': None, 'Write': None}, 'type': {'Integer': IntegerType('Integer'), 'Boolean': BooleanType('Boolean')}}

parsed_so_far = []

def error(msg):
  #print '  '.join(parsed_so_far)
  error_msg = msg + ' on line %d' % line_no
  #print error_msg
  raise Exception(error_msg)

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

def is_var(name):
  f = get('var', name)
  return f is not None

def is_const(name):
  f = get('const', name)
  return f is not None

def add_type(name, type):
  if name in scope['type']:
    error('Cannot redefine type %s' % name)
  scope['type'][name] = type

def add_const(name, type, value):
  if name in scope['const']:
    error('Cannot redefine constant %s' % name)
  scope['const'][name] = Constant(name, type, value)

def add_var(name, type):
  if name in scope['var']:
    error('Cannot redefine variable %s' % name)
  scope['var'][name] = Variable(name, type)

def add_proc(name, params):
  if name in scope['proc']:
    error('Cannot redefine procedure %s' % name)
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
  procedure_block(proc_name)
  expect(';')

def procedure_block(proc_name):
  if check('('):
    expect('(')
    params = formal_parameter_list()
    expect(')')
  add_proc(proc_name, params)
  push_scope()
  for param in params:
    add_var(param.name, param.type)
  expect(';')
  block_body()
  pop_scope()

def formal_parameter_list():
  params = parameter_definition()
  while check(';'):
    expect(';')
    map(lambda x: params.append(x), parameter_definition())
  return params

def parameter_definition():
  '''
  returns list of Parameter objects
  '''
  is_var = False
  if check('var'):
    expect('var')
    is_var = True
  vars = variable_group()
  params = map(lambda v: Parameter(v[0], v[1], is_var), vars)
  return params

def variable_definition_part():
  #print 'variable_definition_part'
  expect('var')
  vars = variable_definition()
  for v, t in vars:
    add_var(v, t)
  while current_symbol in first('VariableDefinition'):
    vars = variable_definition()
    for v, t in vars:
      add_var(v, t)

def variable_definition():
  vars = variable_group()
  expect(';')
  return vars

def variable_group():
  '''
  Returns list of tuples like [(name, type), (name, type)]
  '''
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
      error('Found name `%s` not associated with a var or proc in a statement' % name)
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
  variable_access(name)
  expect(':=')
  expression()

def variable_access(var_name):
  #name has already been consumed
  '''
  returns type of variable being accessed
  '''
  var = get('var', var_name)
  if var is None:
    error('Cannot assign to missing var %s' % var_name)
  type = get('type', var.type)
  while current_symbol in first('Selector'):
    type = selector(var.name, type)
  return type

def selector(var_name, type):
  '''
  var should be a Variable instance

  returns type that was selected
  '''
  if check('['):
    if not type.is_array:
      error('Trying to use an indexed selector on non-array variable %s' % var_name)
    expect('[')
    expression()
    expect(']')
    return get('type', type.type_of)
  elif check('.'):
    if not type.is_record:
      error('Trying to use a field selector on non-record variable %s' % var_name)
    expect('.')
    field_name = name()
    if not field_name in type.fields:
      error('Trying to access missing field %s from type %s' % (field_name, type.name))
    return get('type', type.fields[field_name])
  else:
    error('Expected selector')

def procedure_statement(proc_name):
  #print 'procedure_statement'
  #name has already been consumed in figuring out whether we're in
  #assignment or procedure statement
  proc = get('proc', proc_name)
  if proc is None:
    error('trying to call nonexistent procedure')
  if check('('):
    expect('(')
    params = actual_parameter_list()
    expect(')')
  if len(params) != len(proc.params):
    error('`%s` takes %d parameters; %d given' % (proc_name, len(proc.params), len(params)))
  for i in range(len(params)):
    if params[i].name != proc.params[i].type: 
      error('Parameter %d passed to `%s` is of type `%s`; expecting `%s`' % (i + 1, proc_name, params[i].name, proc.params[i].name))

def actual_parameter_list():
  '''
  returns the list of parameter types
  '''
  params = [actual_parameter()]
  while check(','):
    expect(',')
    params.append(actual_parameter())
  return params

def actual_parameter():
  return expression()

def if_statement():
  #print 'if_statement'
  expect('if')
  type = expression()
  if type.name != 'Boolean':
    error('Condition of an if statement must return a Boolean')
  expect('then')
  statement()
  if check('else'):
    expect('else')
    statement()

def while_statement():
  #print 'while_statement'
  expect('while')
  type = expression()
  if type.name != 'Boolean':
    error('Condition of an if statement must return a Boolean')
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
  '''
  returns resulting type
  '''
  type = simple_expression()
  if current_symbol in first('RelationalOperator'):
    op = current_symbol
    relational_operator()
    other_type = simple_expression()
    if op in ['<', '<=', '>=']:
      if type.name != 'Integer' or other_type.name != 'Integer':
        error('Comparisons must be with Integer type variables')
    else:
      if type.name != other_type.name:
        error('Equality checks must be between equivalent types')
    type = get('type', 'Boolean')
  return type

def simple_expression():
  if current_symbol in first('SignOperator'):
    sign_operator()
  type = term()
  while current_symbol in first('AddingOperator'):
    op = current_symbol
    adding_operator()
    other_type = term()
    if op == 'or':
      if type.name != 'Boolean' or other_type.name != 'Boolean':
        error('Can only use `or` operator with Boolean types')
      else:
        type = get('type', 'Boolean')
    else:
      if type.name != 'Integer' or other_type.name != 'Integer':
        error('Can only use adding `%s` operator with Integers; found %s and %s' % (op, type.name, other_type.name))
      else:
        type = get('type', 'Integer')
  return type

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
  '''
  returns type of term
  '''
  type = factor()
  while current_symbol in first('MultiplyingOperator'):
    op = current_symbol
    multiplying_operator()
    other_type = factor()
    if op == 'and':
      if type.name != 'Boolean' or other_type.name != 'Boolean':
        error('Can only use `and` on Boolean operands')
    else:
      if type.name != 'Integer' or other_type.name != 'Integer': 
        error('Can only use `%s` on Integer operands' % op)
  return type

def multiplying_operator():
  if any(map(check, ['*', 'div', 'mod', 'and'])):
    next_symbol()
  else:
    error('expected multiplying operator')

def factor():
  '''
  returns type of factor
  '''
  if check('name'):
    factor_name = name()
    if is_const(factor_name):
      c = get('const', factor_name)
      #we found our constant, we're good
      return c.type
    elif is_var(factor_name):
      return variable_access(factor_name)
    else:
      error("Cannot find constant or variable named %s" % factor_name)
  elif current_symbol in first('Numeral'):
    numeral()
    return get('type', 'Integer')
  elif check('('):
    expect('(')
    type = expression()
    expect(')')
    return type
  elif check('not'):
    expect('not')
    return factor()
  else:
    error('Expected a constant, variable, parenthesized expression, or `not`; found %s' % current_symbol)

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
