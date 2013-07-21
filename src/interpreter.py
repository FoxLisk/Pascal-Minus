from bytecodes import Op, reverse_bytecodes
import sys

_store = []
_p = 0
_b = 0
_s = 0

def get_code():
  '''
  returns a list of opcodes
  '''

  '''
  fn = sys.argv[1]
  f = open(fn)
  code = f.read()
  f.close()
  return code
  or whatever
  '''
  return [Op.PROGRAM, 0, 3, Op.CONSTANT, 65, Op.WRITE, Op.ENDPROG]

def error(msg):
  raise Exception(msg)

def store(loc, val = None):
  global _store
  diff = loc - len(_store) + 1 #0-based indexing
  while diff > 0:
    _store.append(0)
    diff -= 1
  if val is None:
    return _store[loc]
  else:
    _store[loc] = val

def p(inc = None):
  '''
  program pointer
  '''
  global _p
  if inc is None:
    return _p
  else:
    _p += inc

def b(inc = None):
  '''
  base pointer of current activation record (stack frame)
  '''
  global _b
  if inc is None:
    return _b
  else:
    _b += inc

def s(inc = None):
  '''
  top of stack pointer
  '''
  global _s
  if inc is None:
    return _s
  else:
    _s += inc
    return _s

def variable(level, displ):
  s(1) #move to next free stack space
  x = b() #grab current base pointer
  while level > 0: #move through the static links as many levels as necessary to find the variable in the correct stack frame
    x = store(x)
    level -= 1
  store(s, x + displ) #set the top of the stack to the address of the sought variable
  p(3) #move program three blocks forward (variable instruction is VARIABLE, LEVEL, DISPL)

def var_param(level, displ):
  s(1) #move to next free stack space
  x = b() #grab current base pointer
  while level > 0: #move through the static links as many levels as necessary to find the variable in the correct stack frame
    x = store(x)
    level -= 1
  var_loc = store(x + displ) #we need to grab the location of the variable that was passed in as a parameter TODO understand this
  store(s(), var_loc)
  p(3) #move program three blocks forward (variable instruction is VARIABLE, LEVEL, DISPL)

def index(lower, upper, length, line_no):
  #we'll have something like ARRAY_VAR_ADDR, 5, OP.INDEX meaning to take the 5th element from the array pointed to by ARRAY_VAR_ADDR
  #length is the length of an element of the array, not the length of the array
  #so we want the top of the stack to be the ADDRESS of the 5th element of array_var_value
  i = store(s()) #this is the index to dereference
  if i < lower or i > upper:
    error('Trying to dereference past the bounds of an array on line %d' % line_no)
  s(-1)
  #the address of the indexed variable is the displacement from the index (i - lower) times the length of an element
  #s() stores the address of the array to access currently, so we're replacing the location of the array with the location of the specific element
  addr = s() + (i - lower) * length 
  store(addr, s())
  p(5)

def field(displ):
  #the displ is the distance from the start of a record to the element we need, which makes this very simple
  #the complicated part is the code emission part :D
  store(s(), store(s()) + displ)
  p(2)

def constant(val):
  s(1)
  store(s(), val)
  p(2)

def value(length):
  #TODO this is probably broken
  i = store(s()) #the value in store(s()) is the address of the variable we want so i is now the actual variable
  s(1)
  while length > 0: #so for each element in the var (possibly only the one) 
    store(s(), i) #we copy the value at i into the store
    s(1) #move the stack pointer forward
    i += 1 #and move the pointer from the source var forward
    length -= 1
  p(2)

def assign(length):
  #TODO this is probably broken
  #s() is pointing to the last value (out of total $length values) that we want to copy
  #so s() - length is the address of the variable we're copying into
  #and s() - length + 1 is the beginning of the values to copy
  val_addr = s() - length + 1
  var_addr = store(s() - length)
  while length > 0: #so for each element in the var (possibly only the one) 
    store(var_addr, store(val_addr))
    var_addr += 1
    val_addr += 1
    length -= 1
  p(2)

def goto(displ):
  p(displ)

def do(displ):
  if store(s()) == 1: #store(s()) is the result of whatever expression we're evaluating
    p(2) #move past the DISPL, DO instruction into the loop body
  else:
    p(displ) #jump to the end of the body

'''
#if statements like if B then S1 [else S2] compiles into: B DO(L1) S1 GOTO(L2) L1: S2, L2
#basically just a do loop with an unconditional break at the end
#thus no def if()
'''

def proc_call(level, displ):
  '''
  level is the number of levels back in the static link to follow
  displ is the displacement from p to the end of the proc call instruction (taking into account all the parameter lengths, etc)
  '''
  s(1)
  #trace static link back to the base
  static_link = b() 
  while level > 0:
    static_link = store(x)
    level -= 1
  store(s(), static_link)
  store(s() + 1, b()) #store the current base address as the new dynamic link
  store(s() + 2, p() + 3) #current program instruction + 3 as new return address (3 because the proc call instr, level, displ and its the one AFTER those.)
  b(s() - b()) # b = s
  s(b() - s() + 2)
  p(displ)

def procedure(var_length, displ):
  s(var_length) #move top of stack past the variable part
  p(displ) #move the program pointer past displ (the number of instructions to invoke the proedure)

def end_proc(param_length):
  p(p() - stack(b() + 2)) #move p to the value stored in b() + 2, which is the return address
  s(s() - b()) #move the stack pointer back to b()
  s(-(param_length + 1)) #move the stack pointer back past all the params
  b(stack(b() + 1)) #move the static link back to where the dynamic link points

def program(var_length, displ):
  s(2 + var_length)
  p(displ)

def write():
  #print 'writing'
  val = store(s())
  #print 'val: %d chr: %s' % (val, chr(val))
  sys.stdout.write(chr(val))
  s(-1)
  p(1)
      
def read():
  #address of the variable is the top of the stack
  var_addr = store(s())
  stack(var_addr, int(raw_input()))
  s(-1)
  p(1)

#######
# BINARY OPERATIONS
#######

def binary_op(operation):
  s(-1)
  x = store(s())
  y = store(s() + 1)
  store(s(), operation(x, y))
  p(1)

def add():
  binary_op(lambda x, y: x + y)

def multiply():
  binary_op(lambda x, y: x * y)

def subtract():
  binary_op(lambda x, y: x - y)

def mod():
  binary_op(lambda x, y: x % y)

def log_and():
  binary_op(lambda x, y: y == 1 if x == 1 else 0)

def log_or():
  binary_op(lambda x, y: y == 1 if x == 0 else 1)

def lt():
  binary_op(lambda x, y: 1 if x < y else 0)

def lte():
  binary_op(lambda x, y: 1 if x <= y else 0)

def eq():
  binary_op(lambda x, y: 1 if x == y else 0)

def gte():
  binary_op(lambda x, y: 1 if x >= y else 0)

def gt():
  binary_op(lambda x, y: 1 if x > y else 0)

def ne():
  binary_op(lambda x, y: 1 if x != y else 0)

######
# UNARY OPERATIONS
######

def unary_op(operation):
  x = store(s())
  store(s(), operation(x))
  p(1)

def log_not():
  unary_op(lambda x: 1 if x == 0 else 0)

def minus():
  unary_op(lambda x: -x)

def setup():
  global _store
  _store = get_code()
  b(len(_store))
  s(len(_store))

def run():
  setup()
  while True:
    op = store(p())
    #print 'Handling operation %s' % reverse_bytecodes[op]
    if op == Op.ADD:
      add()
    elif op == Op.AND:
      log_and()
    elif op == Op.ASSIGN:
      assign(store(p() + 1))
    elif op == Op.CONSTANT:
      constant(store(p() + 1))
    elif op == Op.DIVIDE:
      div()
    elif op == Op.DO:
      do(store(p() + 1))
    elif op == Op.ENDPROC:
      end_proc(p() + 1)
    elif op == Op.ENDPROG:
      break
    elif op == Op.EQUAL:
      eq()
    elif op == Op.FIELD:
      field(store(p() + 1))
    elif op == Op.GOTO:
      goto(store(p() + 1))
    elif op == Op.GREATER:
      gt()
    elif op == Op.INDEX:
      _p = p()
      index(store(_p + 1), store(_p + 2), store(_p + 3), store(_p + 4))
    elif op == Op.LESS:
      lt()
    elif op == Op.MINUS:
      minus()
    elif op == Op.MODULO:
      mod()
    elif op == Op.MULTIPLY:
      multiply()
    elif op == Op.NOT:
      log_not()
    elif op == Op.NOTEQUAL:
      ne()
    elif op == Op.NOTGREATER:
      lte()
    elif op == Op.NOTLESS:
      gte()
    elif op == Op.OR:
      log_or()
    elif op == Op.PROCCALL:
      proc_call(store(p() + 1), store(p() + 2))
    elif op == Op.PROCEDURE:
      procedure(store(p() + 1), store(p() + 2))
    elif op == Op.PROGRAM:
      program(store(p() + 1), store(p() + 2))
    elif op == Op.SUBTRACT:
      subtract()
    elif op == Op.VALUE:
      value(store(p() + 1))
    elif op == Op.VARIABLE:
      variable(store(p() + 1), store(p() + 2))
    elif op == Op.VARPARAM:
      var_param(store(p() + 1), store(p() + 2))
    elif op == Op.READ:
      read()
    elif op == Op.WRITE:
      write()
    elif op == Op.DEFADDR:
      pass
    elif op == Op.DEFARG:
      pass
      
if __name__ == '__main__':
  run()
