from errors import Errors
from administration_functions import error, emit_code
from symbols import symbols, reverse_symbols
from first import first
from bytecodes import Op

block_level = 0
label_no = 0

def new_label():
  global label_no
  tmp = label_no
  label_no += 1
  return tmp

class Type(object):
  def __init__(self, name):
    self.name = name
    self.is_record = False
    self.is_array = False

  def length(self):
    raise Exception("Length has not been implemented by this subclass of Type")

  def __str__(self):
    return self.name

class IntegerType(Type):
  def __init__(self, name):
    super(IntegerType, self).__init__(name)

  def length(self):
    return 1

class BooleanType(Type):
  def __init__(self, name):
    super(BooleanType, self).__init__(name)

  def length(self):
    return 1

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

  def length(self):
    element_length = self.type_of.length()
    return (self.upper - self.lower + 1) * element_length

class RecordType(Type):
  def __init__(self, name, fields):
    '''
    fields should be a dict of the form
    { field_name: type_name }
    '''
    super(RecordType, self).__init__(name)
    self.fields = fields
    self.is_record = True

  def length(self):
    return sum(map(lambda t: t.length(), self.fields.values()))

  def field_displ(self, field_name):
    '''
    returns the displacement from this record to the start of field_name
    '''
    displ = 0
    for name, type in self.fields.items():
      if name == field_name:
        return displ
      else:
        displ += type.length()

class Constant:
  def __init__(self, name, type, value):
    self.name = name
    self.type = type
    self.value = value

class Variable:
  def __init__(self, name, type):
    self.name = name
    self.type = type
    self.displ = None
    self.level = None
    self.is_var_param = False

  def length(self):
    return self.type.length()

  def __str__(self):
    return '%s : %s' % (self.name, self.type.name)

class Parameter:
  def __init__(self, name, type, is_var):
    self.name = name
    self.type = type
    self.is_var_param = is_var
    self.displ = None
    self.level = None

  def length(self):
    return self.type.length()

  def __str__(self):
    return 'Parameter %s : %s | level %d | displ %d' % (self.name, self.type.name, self.level, self.displ)

class Proc:
  def __init__(self, name, params):
    global block_level
    '''
    params should be a list of Parameter objects
    '''
    self.name = name
    self.params = params
    self.level = block_level
    self.label = new_label()

line_no = 0
current_symbol = None

#the standard types, Integer and Boolean, are 1 and 2
#the standard values, False and True, are 3 and 4
#the standard procs, Read and Write, are 5 and 6
scope = {'var': {}, 'const': {'False': Constant(3, 2, False), 'True': Constant(4, 2, False)},  'proc': {}, 'type': {'Integer': IntegerType('Integer'), 'Boolean': BooleanType('Boolean')}}

parsed_so_far = []

def error(msg):
  #print '  '.join(parsed_so_far)
  error_msg = msg + ' on line %d' % line_no
  #print error_msg
  raise Exception(error_msg)


def push_scope():
  #print 'push_scope'
  global scope, block_level
  temp = scope
  scope = {'parent': temp, 'var': {}, 'const': {}, 'proc': {}, 'type': {}}
  block_level += 1

def pop_scope():
  #print 'pop_scope'
  global scope, block_level
  block_level -= 1
  if block_level < 0:
    error('Parser error: reached negative block level')
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
  var = Variable(name, type)
  scope['var'][name] = var
  return var

def add_proc(name, params):
  if name in scope['proc']:
    error('Cannot redefine procedure %s' % name)
  proc = Proc(name, params)
  scope['proc'][name] = proc
  return proc

def add_param(param):
  '''
  adds a parameter object as a variable for the current scope
  '''
  if param.name in scope['var']:
    error('Cannot redefine variable %s' % name)
  scope['var'][param.name] = param

add_proc('Write', [Parameter('x', get('type', 'Integer'), False)])
add_proc('Read', [Parameter('x', get('type', 'Integer'), True)])

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
  var_label = new_label()
  begin_label = new_label()
  emit_code(Op.PROGRAM, var_label, begin_label)
  program_name = name()
  expect(';')
  block_body(var_label, begin_label)
  expect('.')
  emit_code(Op.ENDPROG)

def block_body(var_label, begin_label):
  #print 'block_body'
  if current_symbol in first('ConstantDefinitionPart'):
    #print "trying constant definition part"
    constant_definition_part()
  if current_symbol in first('TypeDefinitionPart'):
    type_definition_part()
  if current_symbol in first('VariableDefinitionPart'):
    vars = variable_definition_part()
  else:
    vars = []
  while current_symbol in first('ProcedureDefinition'):
    procedure_definition()
  emit_code(Op.DEFADDR, begin_label)
  var_length = sum(map(lambda var: var.length(), vars))
  emit_code(Op.DEFARG, var_label, var_length)
  compound_statement()

def procedure_definition():
  expect('procedure')
  proc_name = name()
  print 'PROC %s' % proc_name
  procedure_block(proc_name)
  expect(';')

def procedure_block(proc_name):
  if check('('):
    expect('(')
    params = formal_parameter_list()
    expect(')')
  proc = add_proc(proc_name, params)
  push_scope()
  parameter_addressing(params)
  for param in params:
    add_param(param)
  expect(';')
  var_length_label = new_label()
  begin_label = proc.label
  block_body(var_length_label, begin_label)

  param_length = sum(map(lambda p: 1 if p.is_var_param else p.length(), params))

  emit_code(Op.ENDPROC, param_length)
  pop_scope()

def formal_parameter_list():
  params = parameter_definition()
  while check(';'):
    expect(';')
    map(lambda x: params.append(x), parameter_definition())
  return params

def parameter_addressing(params):
  global block_level
  displ = 0
  for param in reversed(params):
    l = 1 if param.is_var_param else param.length()
    displ -= l
    param.displ = displ
    param.level = block_level
    
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
  '''
  returns the variables defined
  '''
  #print 'variable_definition_part'
  expect('var')
  vars = variable_definition()
  all_vars = []
  for v, t in vars:
    var = add_var(v, t)
    all_vars.append(var)
  while current_symbol in first('VariableDefinition'):
    vars = variable_definition()
    for v, t in vars:
      var = add_var(v, t)
      all_vars.append(var)
  variable_addressing(all_vars)
  return all_vars

def variable_addressing(vars):
  global block_level
  displ = 3 #we start addressing variables after the static context, dynamic context, and return address
  for var in vars:
    var.displ = displ
    var.level = block_level
    displ += var.length()

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
  type = get('type', t)
  #print 'variable group: name returned type %d' % t
  if type is None:
    error("Trying to declare variables of undeclared type %s" % t)
  ret = []
  for n in names:
    ret.append((n, type))
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
  type = variable_access(name)
  expect(':=')
  expression()
  emit_code(Op.ASSIGN, type.length())

def variable_access(var_name):
  global block_level
  #name has already been consumed
  '''
  returns type of variable being accessed
  '''
  var = get('var', var_name)
  if var is None:
    error('Cannot assign to missing var %s' % var_name)
  level = block_level - var.level
  op = Op.VARPARAM if var.is_var_param else Op.VARIABLE
  emit_code(op, level, var.displ)
  type = var.type

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
    emit_code(Op.INDEX, type.lower, type.upper, type.type_of.length(), line_no)
    return type.type_of
  elif check('.'):
    if not type.is_record:
      error('Trying to use a field selector on non-record variable %s' % var_name)
    expect('.')
    field_name = name()
    if not field_name in type.fields:
      error('Trying to access missing field %s from type %s' % (field_name, type.name))
    emit_code(Op.FIELD, type.field_displ(field_name))
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
  params = []
  if check('('):
    expect('(')
    params = actual_parameter_list(proc)
    expect(')')
  if len(params) != len(proc.params):
    error('`%s` takes %d parameters; %d given' % (proc_name, len(proc.params), len(params)))
  for i in range(len(params)):
    if params[i] != proc.params[i].type: 
      error('Parameter %d passed to `%s` is of type `%s`; expecting `%s`' % (i + 1, proc_name, params[i], proc.params[i].type))
  if proc.name == 'Write':
    emit_code(Op.WRITE)
  elif proc.name == 'Read':
    error('Read not implemented')
  else:
    emit_code(Op.PROCCALL, block_level - proc.level, proc.label)

def actual_parameter_list(proc):
  '''
  returns the list of parameter types
  '''
  param_types = []
  first = True
  for param in proc.params:
    if not first:
      expect(',')
    if param.is_var_param:
      if not check('name'):
        error('Var params must be passed a variable')
      var_name = name()
      var = variable_access(var_name)
    else:
      var = expression()
    param_types.append(var)
    first = False
  return param_types

def actual_parameter():
  type = expression()
  return type

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

    if op == '<':
      emit_code(Op.LESS)
    elif op == '>':
      emit_code(Op.GREATER)
    elif op == '=':
      emit_code(Op.EQUAL)
    elif op == '<=':
      emit_code(Op.NOTGREATER)
    elif op == '>=':
      emit_code(Op.NOTLESS)
    elif op == '<>':
      emit_code(Op.NOTEQUAL)
  return type

def simple_expression():
  sign = None
  if current_symbol in first('SignOperator'):
    sign = current_symbol
    sign_operator()
  type = term()

  if sign == '-':
    emit_code(Op.MINUS)
    
  while current_symbol in first('AddingOperator'):
    op = current_symbol
    adding_operator()
    other_type = term()
    if op == 'or':
      if type.name != 'Boolean' or other_type.name != 'Boolean':
        error('Can only use `or` operator with Boolean types')
      else:
        type = get('type', 'Boolean')
      emit_code(Op.OR)
    else:
      if type.name != 'Integer' or other_type.name != 'Integer':
        error('Can only use adding `%s` operator with Integers; found %s and %s' % (op, type.name, other_type.name))
      else:
        type = get('type', 'Integer')
      if op == '+':
        emit_code(Op.ADD)
      elif op == '-':
        emit_code(Op.SUBTRACT)
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
      emit_code(Op.AND)
    else:
      if type.name != 'Integer' or other_type.name != 'Integer': 
        error('Can only use `%s` on Integer operands' % op)
      if op == '*':
        emit_code(Op.MULTIPLY)
      elif op == 'div':
        emit_code(Op.DIVIDE)
      elif op == 'mod':
        emit_code(Op.MODULO)
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
      emit_code(Op.CONSTANT, c.value)
      #we found our constant, we're good
      return c.type
    elif is_var(factor_name):
      type = variable_access(factor_name)
      #variable_access is used in both assignment and expressions, so if we're
      #getting the value of a variable here factor has to emit the value part
      emit_code(Op.VALUE, type.length())
      return type
    else:
      error("Cannot find constant or variable named %s" % factor_name)
  elif current_symbol in first('Numeral'):
    num = numeral()
    emit_code(Op.CONSTANT, num)
    return get('type', 'Integer')
  elif check('('):
    expect('(')
    type = expression()
    expect(')')
    return type
  elif check('not'):
    expect('not')
    fact = factor()
    emit_code(Op.NOT)
    return fact
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
  num = current_symbol
  next_symbol()
  return int(num)

def new_array_type(type_name):
  #print 'new_array_type'
  expect('array')
  expect('[')
  lower, upper = index_range()
  #lower and upper are (type, val) tuples
  expect(']')
  expect('of')
  type_of_name = name()
  type_of = get('type', type_of_name)
  add_type(type_name, ArrayType(type_name, type_of, lower[1], upper[1]))

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
    return get('type', 'Integer'), constant
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
  try:
    pass
  except Exception as e:
    raise(e)
    error(str(e))
