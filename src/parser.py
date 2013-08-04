from errors import Errors
from administration_functions import error
from symbols import symbols, reverse_symbols, standard_types, standard_procs
from first import first
from bytecodes import Op, code_lengths, reverse_bytecodes
from scanner import Scanner
from copy import copy
import os
import traceback

class Labeler:
  def __init__(self):
    self.label_no = 0

  def new_label(self):
    tmp = self.label_no
    self.label_no += 1
    return tmp

bytecodes = []

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
  def __init__(self):
    super(IntegerType, self).__init__('Integer')

  def length(self):
    return 1

class BooleanType(Type):
  def __init__(self):
    super(BooleanType, self).__init__('Boolean')

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
    { field_name: type }
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

class VoidType(Type):
  def __init__(self):
    super(VoidType, self).__init__('void')

  def length(self):
    return 0

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
  def __init__(self, name, params, block_level, label, return_type):
    '''
    params should be a list of Parameter objects
    '''
    self.name = name
    self.params = params
    self.level = block_level
    self.label = label
    self.return_type = return_type

  def return_length(self):
    if self.return_type is None:
      return 0
    else:
      return self.return_type.length()

  def param_length(self):
    param_length = sum(map(lambda p: 1 if p.is_var_param else p.length(), self.params))
    return param_length

def error(msg, line_no = None):
  if line_no is not None:
    msg += ' on line %d' % line_no
  raise Exception(msg)

class Scope:
  INTEGER_TYPE = IntegerType()
  BOOLEAN_TYPE = BooleanType()
  VOID_TYPE    = VoidType()

  def __init__(self, parent = None):
    self.vars = {}
    self.consts = {}
    self.procs = {}
    self.types = {}
    self.parent = parent

  def __str__(self):
    out = 'Scope:\n'
    out += '  vars: ' + str(self.vars)
    out += '\n  consts: ' + str(self.consts)
    out += '\n procs: ' + str(self.procs)
    out += '\n types: ' + str(self.types)
    out += '\n Parent: \n' + str(self.parent)
    return out

  @staticmethod
  def default_scope():
    scope = Scope()
    scope.add_const('False', Scope.BOOLEAN_TYPE, 0)
    scope.add_const('True', Scope.BOOLEAN_TYPE, 1)
    #giving these negative labels to avoid interfering with labeling in the parser
    scope.add_proc('Write', [Parameter('x', Scope.INTEGER_TYPE, False)], 0, -1, Scope.VOID_TYPE)
    scope.add_proc('Read', [Parameter('x', Scope.INTEGER_TYPE, True)], 0, -2, Scope.VOID_TYPE)
    
    scope.add_type('Integer', Scope.INTEGER_TYPE)
    scope.add_type('Boolean', Scope.BOOLEAN_TYPE)
    scope.add_type('void', Scope.VOID_TYPE)
    return scope

  def get_copy_for_import(self):
    scope = Scope()
    scope.types = self.types
    scope.procs = self.procs
    return scope

  def get_type(self, name):
    if name in self.types:
      return self.types[name]

  def get_func(self, name):
    return self.get('proc', name)

  def get(self, t, name):
    '''
    t is the type: var, proc, const
    use get_type for type

    returns the saught value if found, or None
    '''
    if t == 'var':
      lookup = self.vars
    elif t == 'type':
      lookup = self.types
    elif t == 'proc':
      lookup = self.procs
    elif t == 'const':
      lookup = self.consts

    if name in lookup:
      return lookup[name]

    if self.parent is None:
      return None
    return self.parent.get(t, name)

  def is_var(self, name):
    f = self.get('var', name)
    return f is not None

  def is_const(self, name):
    f = self.get('const', name)
    return f is not None

  def is_func(self, name):
    f = self.get_func(name)
    return f is not None

  def add_type(self, name, type):
    if name in self.types:
      error('Cannot redefine type %s' % name)
    self.types[name] = type
    return type

  def add_const(self, name, type, value):
    if name in self.consts:
      error('Cannot redefine constant %s' % name)
    self.consts[name] = Constant(name, type, value)

  def add_var(self, name, type):
    if name in self.vars:
      error('Cannot redefine variable %s' % name)
    var = Variable(name, type)
    self.vars[name] = var
    return var

  def add_proc(self, name, params, level, label, return_type = None):
    if name in self.procs:
      error('Cannot redefine procedure %s' % name)
    proc = Proc(name, params, level, label, return_type)
    self.procs[name] = proc
    return proc

  def add_param(self, param):
    '''
    adds a parameter object as a variable for the current scope
    '''
    if param.name in self.vars:
      error('Cannot redefine variable %s' % name)
    self.vars[param.name] = param

class Parser:
  def __init__(self, symbol_list, filename, lib = ['.']):
    self.filename = filename
    self.lib = lib
    self.is_import = False
    self.symbols = self._next_symbol(symbol_list)
    self.scope = Scope.default_scope() #this is unnecessary but fairly painless
    self.labeler = Labeler() #same
    self.block_level = 0 #this will be fine even for import sub_parsers, because those will always happen at top level
    self.bytecodes = []
    self.current_symbol = None
    self.line_no = 0
    self.imported = set()
    self.current_proc = []

  def create_sub_parser(self, tokens, filename):
    sub_parser = Parser(tokens, filename)
    sub_parser.labeler = self.labeler #no repeat labels
    sub_parser.is_import = True
    sub_parser.lib = self.lib
    sub_parser.imported = self.imported
    sub_parser.scope = self.scope.get_copy_for_import() #we want to add any new functions to our existing scope
    return sub_parser


  def push_scope(self):
    #print 'push_scope'
    self.scope = Scope(self.scope)
    self.block_level += 1

  def pop_scope(self):
    #print 'pop_scope'
    self.block_level -= 1
    if self.block_level < 0:
      self.error('Parser error: reached negative block level', self.line_no)
    self.scope = self.scope.parent

  def emit_code(self, *args):
    if len(args) <> code_lengths[args[0]]:
      error('Error: wrong length of opcodes for instr %s' % reverse_bytecodes[args[0]])
    for arg in args:
      self.bytecodes.append(arg)

  def _next_symbol(self, all_symbols):
    #print '_next_symbol'
    '''
    f = open('temp1')
    all_symbols = f.read()
    f.close()
    all_symbols = [s for s in all_symbols.split(' ') if s != '']
    '''
    is_nl = False
    is_name = False
    is_int = False
    for s in all_symbols:
      if is_nl:
        self.line_no = int(s)
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

  def next_symbol(self):
    #print 'next_symbol'
    try:
      self.current_symbol = self.symbols.next()
      return self.current_symbol
    except StopIteration:
      error('out of symbols', self.line_no)

  def expect(self, symbol):
    code = symbols[symbol]
    if self.current_symbol != code:
      if self.current_symbol in reverse_symbols:
        error("Expected %s, found %s" % (symbol, reverse_symbols[self.current_symbol]), self.line_no)
      else:
        error("Expected %s, found unknown symbol %d" % (symbol, self.current_symbol), self.line_no)
    else:
      self.next_symbol()

  def check(self, symbol):
    code = symbols[symbol]
    return self.current_symbol == code

  def module(self):
    var_label = self.labeler.new_label()
    begin_label = self.labeler.new_label()
    if not self.is_import:
      self.emit_code(Op.PROGRAM, var_label, begin_label)
    while self.current_symbol in first('ImportStatement'):
      self.import_statement()
    self.program(var_label, begin_label)

  def is_imported(self, import_path):
    return '.'.join(import_path) in self.imported

  def add_imported_path(self, import_path):
    self.imported.add('.'.join(import_path))

  def import_statement(self):
    self.expect('import');
    #for now you can only import .pm files from the same directory
    import_path = [self.name()]
    while self.check('.'):
      self.expect('.')
      import_path.append(self.name())
    if not self.is_imported(import_path):
      self.import_lib(import_path)
    self.expect(';')

  def import_lib(self, import_path):
    '''
    import_path is a list of part names, like:
    ['lib', 'writeint']
    '''
    tokens = None
    for loc in self.lib:
      path = os.path.join(loc, *import_path) + '.pm'
      if os.path.isfile(path):
        tokens = Scanner(path).scan()
        break
    if tokens is None:
      error('Unable to find `%s` in any libraries (checked %s)' % ('.'.join(import_path), ':'.join(self.lib)))
    parser = self.create_sub_parser(tokens, path)
    code, success = parser.parse()
    if not success:
      error('Parsing error in import %s' % '.'.join(import_path))
    self.bytecodes.extend(code)
    self.add_imported_path(import_path)

  def program(self, var_label, begin_label):
    #print 'program'
    self.expect('program')
    program_name = self.name()
    prog = Proc(program_name, [], 0, begin_label, self.scope.get_type('void'))
    self.current_proc.append(prog)
    self.expect(';')
    self.block_body(var_label, begin_label)
    self.expect('.')
    if not self.is_import:
      self.emit_code(Op.ENDPROG)

  def block_body(self, var_label, begin_label):
    #print 'block_body'
    if self.current_symbol in first('ConstantDefinitionPart'):
      #print "trying constant definition part"
      self.constant_definition_part()
    if self.current_symbol in first('TypeDefinitionPart'):
      self.type_definition_part()
    if self.current_symbol in first('VariableDefinitionPart'):
      vars = self.variable_definition_part()
    else:
      vars = []
    while self.current_symbol in first('ProcedureDefinition') \
        or self.current_symbol in first('FunctionDefinition'):
          if self.current_symbol in first('ProcedureDefinition'):
            self.procedure_definition()
          else:
            self.function_definition()
    self.emit_code(Op.DEFADDR, begin_label)
    var_length = sum(map(lambda var: var.length(), vars))
    self.emit_code(Op.DEFARG, var_label, var_length)
    self.compound_statement()

  def function_definition(self):
    self.expect('function')
    func_name = self.name()
    params = []
    if self.check('('):
      self.expect('(')
      params = self.formal_parameter_list()
      self.expect(')')
    self.expect(':')

    return_type_name = self.name()
    return_type = self.scope.get_type(return_type_name);

    func = self.scope.add_proc(func_name, params, self.block_level, self.labeler.new_label(), return_type)
    self.current_proc.append(func)
    #print 'vars before pushing scope: ' + str(scope.vars)
    self.push_scope()

    self.parameter_addressing(params)
    for param in params:
      self.scope.add_param(param)
    
    self.expect(';')

    var_length_label = self.labeler.new_label()
    begin_label = self.labeler.new_label()

    self.emit_code(Op.DEFADDR, func.label)
    self.emit_code(Op.FUNCTION, var_length_label, begin_label, return_type.length())

    self.block_body(var_length_label, begin_label)
    self.expect(';')

    param_length = sum(map(lambda p: 1 if p.is_var_param else p.length(), params))

    self.emit_code(Op.RETURN, param_length, return_type.length())
    #TODO this will just leave junk values if user doesn't RETURN explicitly...
    self.current_proc.pop()
    self.pop_scope()

  def procedure_definition(self):
    self.expect('procedure')
    proc_name = self.name()
    self.procedure_block(proc_name)
    self.expect(';')
    self.current_proc.pop()

  def procedure_block(self, proc_name):
    params = []
    if self.check('('):
      self.expect('(')
      params = self.formal_parameter_list()
      self.expect(')')
    proc = self.scope.add_proc(proc_name, params, self.block_level, self.labeler.new_label(), self.scope.get_type('void'))
    self.current_proc.append(proc)
    self.push_scope()
    self.parameter_addressing(params)
    for param in params:
      self.scope.add_param(param)
    self.expect(';')
    var_length_label = self.labeler.new_label()
    begin_label = self.labeler.new_label()
    #proc.label should be the address of the beginning of the procedure code
    #that's what's passed in to block body so we use that here
    self.emit_code(Op.DEFADDR, proc.label)
    self.emit_code(Op.FUNCTION, var_length_label, begin_label, 0)
    #print "%s: var %d begin %d" % (proc_name, var_length_label, begin_label
    self.block_body(var_length_label, begin_label)

    param_length = sum(map(lambda p: 1 if p.is_var_param else p.length(), params))

    self.emit_code(Op.RETURN, param_length, 0)
    self.pop_scope()

  def formal_parameter_list(self):
    params = self.parameter_definition()
    while self.check(';'):
      self.expect(';')
      map(lambda x: params.append(x), self.parameter_definition())
    return params

  def parameter_addressing(self, params):
    displ = 0
    for param in reversed(params):
      l = 1 if param.is_var_param else param.length()
      displ -= l
      param.displ = displ
      param.level = self.block_level
      
  def parameter_definition(self):
    '''
    returns list of Parameter objects
    '''
    is_var = False
    if self.check('var'):
      self.expect('var')
      is_var = True
    vars = self.variable_group()
    params = map(lambda v: Parameter(v[0], v[1], is_var), vars)
    return params

  def variable_definition_part(self):
    '''
    returns the variables defined
    '''
    #print 'variable_definition_part'
    self.expect('var')
    vars = self.variable_definition()
    all_vars = []
    for v, t in vars:
      var = self.scope.add_var(v, t)
      all_vars.append(var)
    while self.current_symbol in first('VariableDefinition'):
      vars = self.variable_definition()
      for v, t in vars:
        var = self.scope.add_var(v, t)
        all_vars.append(var)
    self.variable_addressing(all_vars)
    return all_vars

  def variable_addressing(self, vars):
    displ = 3 #we start addressing variables after the static context, dynamic context, and return address
    for var in vars:
      var.displ = displ
      var.level = self.block_level
      displ += var.length()

  def variable_definition(self):
    vars = self.variable_group()
    self.expect(';')
    return vars

  def variable_group(self):
    '''
    Returns list of tuples like [(name, type), (name, type)]
    '''
    names = []
    names.append(self.name())
    while self.check(','):
      self.expect(',')
      names.append(self.name())
    self.expect(':')
    t = self.name()
    type = self.scope.get('type', t)
    #print 'variable group: name returned type %d' % t
    if type is None:
      error("Trying to declare variables of undeclared type %s" % t, self.line_no)
    ret = []
    for n in names:
      ret.append((n, type))
    return ret
    
  def compound_statement(self):
    #print 'compound_statement'
    self.expect('begin')
    self.statement()
    while self.check(';'):
      self.next_symbol()
      self.statement()
    self.expect('end')

  def statement(self):
    #print 'statement'
    if self.check('name'):
      name = self.next_symbol()
      self.next_symbol()
      if self.scope.get('var', name):
        self.assignment_statement(name)
      elif self.scope.get('proc', name):
        self.procedure_statement(name)
      else:
        #this is okay because, even though statements can be empty, a name cannot follow a statement
        #anywhere so if we find a name we dont need to backtrack - it's just game over
        error('Found name `%s` not associated with a var or proc in a statement' % name, self.line_no)
    elif self.check('if'):
      self.if_statement()
    elif self.check('while'):
      self.while_statement()
    elif self.check('begin'):
      self.compound_statement()
    elif self.check('return'):
      self.return_statement()

  def assignment_statement(self, name):
    #print 'assignment_statement'
    #name has already been consumed in figuring out whether we're in
    #assignment or procedure statement
    #we now do something gross and mostly reproduce variable_access() here
    #because we have consumed name
    type = self.variable_access(name)
    self.expect(':=')
    self.expression()
    self.emit_code(Op.ASSIGN, type.length())

  def variable_access(self, var_name):
    #name has already been consumed
    '''
    returns type of variable being accessed
    '''
    var = self.scope.get('var', var_name)
    if var is None:
      error('Cannot assign to missing var %s' % var_name, self.line_no)
    level = self.block_level - var.level
    if var.is_var_param:
      self.emit_code(Op.VARPARAM, level, var.displ)
    else:
      if level == 0:
        self.emit_code(Op.LOCALVAR, var.displ)
      else:
        self.emit_code(Op.VARIABLE, level, var.displ)
    type = var.type

    while self.current_symbol in first('Selector'):
      type = self.selector(var.name, type)
    return type

  def selector(self, var_name, type):
    '''
    var should be a Variable instance

    returns type that was selected
    '''
    if self.check('['):
      if not type.is_array:
        error('Trying to use an indexed selector on non-array variable %s' % var_name, self.line_no)
      self.expect('[')
      self.expression()
      self.expect(']')
      self.emit_code(Op.INDEX, type.lower, type.upper, type.type_of.length(), self.line_no)
      return type.type_of
    elif self.check('.'):
      if not type.is_record:
        error('Trying to use a field selector on non-record variable %s' % var_name, self.line_no)
      self.expect('.')
      field_name = self.name()
      if not field_name in type.fields:
        error('Trying to access missing field %s from type %s' % (field_name, type.name), self.line_no)
      self.emit_code(Op.FIELD, type.field_displ(field_name))
      return type.fields[field_name]
    else:
      error('Expected selector', self.line_no)

  def procedure_statement(self, proc_name):
    #print 'procedure_statement'
    #name has already been consumed in figuring out whether we're in
    #assignment or procedure statement
    proc = self.scope.get_func(proc_name)
    if proc is None:
      error('trying to call nonexistent procedure %s' % proc_name, self.line_no)
    params = []
    self.emit_code(Op.RETURNSPACE, proc.return_length())
    if self.check('('):
      self.expect('(')
      params = self.actual_parameter_list(proc)
      self.expect(')')
    if len(params) != len(proc.params):
      error('`%s` takes %d parameters; %d given' % (proc_name, len(proc.params), len(params)), self.line_no)
    for i in range(len(params)):
      if params[i] != proc.params[i].type: 
        error('Parameter %d passed to `%s` is of type `%s`; expecting `%s`' % (i + 1, proc_name, params[i], proc.params[i].type), self.line_no)
    if proc.name == 'Write':
      self.emit_code(Op.WRITE)
      return self.scope.get_type('void')
    elif proc.name == 'Read':
      self.emit_code(Op.READ)
      #error('Read not implemented', self.line_no)
      return self.scope.get_type('void')
    else:
      self.emit_code(Op.FUNCCALL, self.block_level - proc.level, proc.label, proc.return_length())
      return proc.return_type #TODO probably want a real void type

  def actual_parameter_list(self, proc):
    '''
    returns the list of parameter types
    '''
    param_types = []
    first = True
    for param in proc.params:
      if not first:
        self.expect(',')
      if param.is_var_param:
        if not self.check('name'):
          error('Var params must be passed a variable', self.line_no)
        var_name = self.name()
        var = self.variable_access(var_name)
      else:
        var = self.expression()
      param_types.append(var)
      first = False
    return param_types

  def actual_parameter(self):
    type = self.expression()
    return type

  def if_statement(self):
    #print 'if_statement'
    self.expect('if')
    stmt_label = self.labeler.new_label()
    else_label = self.labeler.new_label()
    end_label = self.labeler.new_label()
    type = self.expression()
    if type.name != 'Boolean':
      error('Condition of an if statement must return a Boolean', self.line_no)

    self.emit_code(Op.DO, else_label) #if (expression from above), go to the statement; else jump to else_label
    self.expect('then')
    self.statement()
    #if there's no else, this is redundant, and could be cleaned up to avoid a 0-displ jump
    self.emit_code(Op.GOTO, end_label)

    if self.check('else'):
      self.expect('else')
      #if there's an else, else_label is the beginning of the else block
      self.emit_code(Op.DEFADDR, else_label)
      self.statement()
    else:
      #if there's no else, else_label is just right after the then statement
      self.emit_code(Op.DEFADDR, else_label)
    self.emit_code(Op.DEFADDR, end_label)

  def while_statement(self):
    #print 'while_statement'
    self.expect('while')
    start_label = self.labeler.new_label()
    jump_label = self.labeler.new_label()

    self.emit_code(Op.DEFADDR, start_label)
    type = self.expression()
    #expression has to evaluate before DO
    if type.name != 'Boolean':
      error('Condition of an if statement must return a Boolean', self.line_no)

    self.emit_code(Op.DO, jump_label)

    self.expect('do')
    self.statement()
    self.emit_code(Op.GOTO, start_label)
    self.emit_code(Op.DEFADDR, jump_label)

  def get_current_proc(self):
    return self.current_proc[-1]

  def return_statement(self):
    self.expect('return')
    return_type = self.scope.get_type('void')
    if self.current_symbol in first('Expression'):
      return_type = self.expression()

    proc = self.get_current_proc()
    expected_type = proc.return_type
    if expected_type != return_type:
      error('Expected type %s does not match return type %s' % (str(expected_type), str(return_type)))
    self.emit_code(Op.RETURN, proc.param_length(), return_type.length())


  def constant_definition_part(self):
    #print 'constant_definition_part'
    self.expect('const')
    self.constant_definition()
    while self.current_symbol in first('ConstantDefinition'):
      self.constant_definition()

  def constant_definition(self):
    #print 'constant_definition'
    const_name = self.name()
    self.expect('=')
    type, val = self.constant()
    self.expect(';')
    self.scope.add_const(const_name, type, val)

  def type_definition_part(self):
    #print 'type_definition_part'
    self.expect('type')
    self.type_definition()
    while self.current_symbol in first('TypeDefinition'):
      self.type_definition()

  def type_definition(self):
    #print 'type_definition'
    type_name = self.name()
    self.expect('=')
    self.new_type(type_name)
    self.expect(';')

  def new_type(self, type_name):
    #print 'new_type'
    if self.current_symbol in first('NewArrayType'):
      self.new_array_type(type_name)
    elif self.current_symbol in first('NewRecordType'):
      self.new_record_type(type_name)
    else:
      error("Expecting a type definition", self.line_no)

  def new_record_type(self, type_name):
    #print 'new_record_type'
    self.expect('record')
    _field_list = self.field_list()
    fields = {}
    for names, type in _field_list:
      for name in names:
        fields[name] = type
    self.scope.add_type(type_name, RecordType(type_name, fields))
    self.expect('end')

  def field_list(self):
    #print 'field_list'
    records = []
    names, type = self.record_section()
    records.append((names, type))
    while self.check(';'):
      self.next_symbol()
      names, type = self.record_section()
      records.append((names, type))
    return records

  def record_section(self):
    #print 'record_section'
    names = []
    field_name = self.name()
    names.append(field_name)
    while self.check(','):
      self.next_symbol()
      field_name = self.name()
      names.append(field_name)
    self.expect(':')
    type_name = self.name()
    type = self.scope.get('type', type_name)
    return names, type

  def expression(self):
    '''
    returns resulting type
    '''
    type = self.simple_expression()
    if self.current_symbol in first('RelationalOperator'):
      op = self.current_symbol
      self.relational_operator()
      other_type = self.simple_expression()

      if op in ['<', '<=', '>=']:
        if type.name != 'Integer' or other_type.name != 'Integer':
          error('Comparisons must be with Integer type variables', self.line_no)
      else:
        if type.name != other_type.name:
          error('Equality checks must be between equivalent types', self.line_no)
      type = self.scope.get('type', 'Boolean')

      if op == '<':
        self.emit_code(Op.LESS)
      elif op == '>':
        self.emit_code(Op.GREATER)
      elif op == '=':
        self.emit_code(Op.EQUAL)
      elif op == '<=':
        self.emit_code(Op.NOTGREATER)
      elif op == '>=':
        self.emit_code(Op.NOTLESS)
      elif op == '<>':
        self.emit_code(Op.NOTEQUAL)
    return type

  def simple_expression(self):
    sign = None
    if self.current_symbol in first('SignOperator'):
      sign = self.current_symbol
      self.sign_operator()
    type = self.term()

    if sign == '-':
      self.emit_code(Op.MINUS)
      
    while self.current_symbol in first('AddingOperator'):
      op = self.current_symbol
      self.adding_operator()
      other_type = self.term()
      if op == 'or':
        if type.name != 'Boolean' or other_type.name != 'Boolean':
          error('Can only use `or` operator with Boolean types', self.line_no)
        else:
          type = self.scope.get('type', 'Boolean')
        self.emit_code(Op.OR)
      else:
        if type.name != 'Integer' or other_type.name != 'Integer':
          error('Can only use adding `%s` operator with Integers; found %s and %s' % (op, type.name, other_type.name), self.line_no)
        else:
          type = self.scope.get('type', 'Integer')
        if op == '+':
          self.emit_code(Op.ADD)
        elif op == '-':
          self.emit_code(Op.SUBTRACT)
    return type

  def relational_operator(self):
    if any(map(self.check, ['<', '=', '<=', '<>', '>=', '>'])):
      self.next_symbol()
    else:
      error('expected relational operator; found %s' % self.current_symbol, self.line_no)

  def sign_operator(self):
    if self.check('+') or self.check('-'):
      self.next_symbol()
    else:
      error('Expected sign operator', self.line_no)

  def adding_operator(self):
    if self.check('+') or self.check('-') or self.check('or'):
      self.next_symbol()
    else:
      error('expected adding operator', self.line_no)

  def term(self):
    '''
    returns type of term
    '''
    type = self.factor()
    while self.current_symbol in first('MultiplyingOperator'):
      op = self.current_symbol
      self.multiplying_operator()
      other_type = self.factor()
      if op == 'and':
        if type.name != 'Boolean' or other_type.name != 'Boolean':
          error('Can only use `and` on Boolean operands', self.line_no)
        self.emit_code(Op.AND)
      else:
        if type.name != 'Integer' or other_type.name != 'Integer': 
          error('Can only use `%s` on Integer operands' % op, self.line_no)
        if op == '*':
          self.emit_code(Op.MULTIPLY)
        elif op == 'div':
          self.emit_code(Op.DIVIDE)
        elif op == 'mod':
          self.emit_code(Op.MODULO)
        elif op == '&':
          self.emit_code(Op.BITAND)
        elif op == '|':
          self.emit_code(Op.BITOR)
        elif op == '<<':
          self.emit_code(Op.BITLSHIFT)
        elif op == '>>':
          self.emit_code(Op.BITRSHIFT)
    return type

  def multiplying_operator(self):
    if any(map(self.check, ['*', 'div', 'mod', 'and', '|', '&', '<<', '>>'])):
      self.next_symbol()
    else:
      error('expected multiplying operator', self.line_no)

  def factor(self):
    '''
    returns type of factor
    '''
    if self.check('name'):
      factor_name = self.name()
      if self.scope.is_const(factor_name):
        c = self.scope.get('const', factor_name)
        self.emit_code(Op.CONSTANT, c.value)
        #we found our constant, we're good
        return c.type
      elif self.scope.is_var(factor_name):
        type = self.variable_access(factor_name)
        #variable_access is used in both assignment and expressions, so if we're
        #getting the value of a variable here factor has to emit the value part
        l = type.length()
        if l == 1:
          self.emit_code(Op.SHORTVALUE)
        else:
          self.emit_code(Op.VALUE, l)
        return type
      elif self.scope.is_func(factor_name):
        return self.procedure_statement(factor_name)
      else:
        error("Cannot find constant or variable named %s" % factor_name, self.line_no)
    elif self.current_symbol in first('Numeral'):
      num = self.numeral()
      self.emit_code(Op.CONSTANT, num)
      return self.scope.get('type', 'Integer')
    elif self.check('('):
      self.expect('(')
      type = self.expression()
      self.expect(')')
      return type
    elif self.check('not'):
      self.expect('not')
      fact = self.factor()
      self.emit_code(Op.NOT)
      return fact
    else:
      error('Expected a constant, variable, parenthesized expression, or `not`; found %s' % self.current_symbol, self.line_no)

  def name(self):
    self.expect('name')
    name = self.current_symbol
    self.next_symbol()
    return name

  def numeral(self):
    #print 'numeral'
    self.expect('numeral')
    num = self.current_symbol
    self.next_symbol()
    return int(num)

  def new_array_type(self, type_name):
    #print 'new_array_type'
    self.expect('array')
    self.expect('[')
    lower, upper = self.index_range()
    #lower and upper are (type, val) tuples
    self.expect(']')
    self.expect('of')
    type_of_name = self.name()
    type_of = self.scope.get('type', type_of_name)
    self.scope.add_type(type_name, ArrayType(type_name, type_of, lower[1], upper[1]))

  def index_range(self):
    #print 'index_range'
    lower = self.constant()
    self.expect('..')
    upper = self.constant()
    return lower, upper

  def constant(self):
    #print 'constant'
    if self.current_symbol in first('Numeral'):
      constant = self.numeral()
      return self.scope.get('type', 'Integer'), constant
    elif self.current_symbol in first('Name'):
      constant_name = self.name()
      constant = self.scope.get('const', constant_name)
      if constant is None:
        error('Failed to find constant %s in scope' % constant_name, self.line_no)
      return constant.type, constant.value
    else:
      error("Expecting a constant - either a Numeral or a named constant", self.line_no)
      
  def parse(self):
    self.next_symbol()
    try:
      self.module()
    except:
      print 'Caught exception parsing %s on line %d: %s' % (self.filename, self.line_no, traceback.format_exc())
      return self.bytecodes, False

    return self.bytecodes, True
