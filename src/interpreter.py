from copy import copy
from administration_functions import get_code, debug, set_debug
from bytecodes import Op, reverse_bytecodes, bytecodes
from collections import defaultdict
import sys


class Interpreter:
  def __init__(self, out, filename = None, code = None, stack_size = 1000000):
    if (filename is None) == (code is None):
      raise Exception("Must pass in a filename XOR a list of bytecodes")
    if filename is not None:
      self.code = get_code(filename)
    else:
      self.code = copy(code)
    self.p = 0
    self.b = 0
    self.s = 3
    self.out = out

    self.stack_size = stack_size
    self.store = [-99999] * stack_size

  def error(self, msg):
    print 'FATAL ERROR: STACK'
    print self.store[0:self.s + 1]
    raise Exception(msg)

  def set_store(self, loc, val):
    '''
    use this to set values in the stack instead of doing it manually, it handles
    resizing & mis-addressing for you
    '''
    '''
    diff = loc - len(self.store) + 1 #0-based indexing
    if diff > 0:
      self.store.extend([-99999] * diff)
    '''
    if loc > self.stack_size:
      self.error('Out of stack space')

    #This check should really be left in for safety but assuming the interpreter is bug-free (hah hah hah)
    #it's actually safe to leave it out
    #saves about half a second per 7 million calls (non-trivial actually)
    #print 'setting store[%d] to %d' % (loc, val)
    self.store[loc] = val

  def variable(self, level, displ):
    self.s += 1
    x = self.b
    while level > 0: #move through the static links as many levels as necessary to find the variable in the correct stack frame
      x = self.store[x]
      level -= 1
    #debug('storing var location of %d at top of stack %d' % (x + displ, self.s))
    self.set_store(self.s, x + displ) #set the top of the stack to the address of the sought variable
    self.p += 3 #move program three blocks forward (variable instruction is VARIABLE, LEVEL, DISPL)

  def local_var(self, displ):
    self.s += 1
    #debug('storing var location of %d at top of stack %d' % (x + displ, self.s))
    self.set_store(self.s, self.b + displ) #set the top of the stack to the address of the sought variable
    self.p += 2 #move program three blocks forward (variable instruction is VARIABLE, LEVEL, DISPL)

  def var_param(self, level, displ):
    self.s += 1
    x = self.b
    while level > 0: #move through the static links as many levels as necessary to find the variable in the correct stack frame
      x = self.store[x]
      level -= 1
    var_loc = self.store[x + displ] #we need to grab the location of the variable that was passed in as a parameter
    #debug('found var param at %d' % var_loc)
    self.set_store(self.s, var_loc)
    self.p += 3 #move program three blocks forward (variable instruction is VARIABLE, LEVEL, DISPL)

  def index(self, lower, upper, length, line_no):
    #we'll have something like ARRAY_VAR_ADDR, INDEX meaning to take the INDEXth element from the array pointed to by ARRAY_VAR_ADDR
    #length is the length of an element of the array, not the length of the array
    #so we want the top of the stack to be the ADDRESS of the 5th element of array_var_value
    #debug('length(lower: %d, upper: %d, length: %d)' % (lower, upper, length))
    i = self.store[self.s] #this is the index to dereference
    if i < lower or i > upper:
      self.error('Trying to dereference past the bounds of an array on line %d' % line_no)
    self.s -= 1
    #the address of the indexed variable is the displacement from the index (i - lower) times the length of an element
    #s() stores the address of the array to access currently, so we're replacing the location of the array with the location of the specific element
    addr = self.store[self.s] + ((i - lower) * length)
    self.set_store(self.s, addr)
    self.p += 5

  def field(self, displ):
    #the displ is the distance from the start of a record to the element we need, which makes this very simple
    #the complicated part is the code emission part :D
    self.set_store(self.s, self.store[self.s] + displ)
    self.p += 2

  def constant(self, val):
    #print 'Pushing constant %d' % val
    self.s += 1
    self.set_store(self.s, val)
    self.p += 2

  def value(self, length):
    var_addr = self.store[self.s] #the value in store[s] is the address of the variable we want so i is now the location of the variable
    #not moving s because we just want to pop the address of the variable off and replace it with the value
    while length > 0: #so for each element in the var (possibly only the one) 
      self.set_store(self.s, self.store[var_addr]) #we copy the value at i into the store
      self.s += 1
      var_addr += 1 #and move the pointer from the source var forward
      length -= 1
    self.s -= 1 #in the loop we moved one word past the end of the actual value
    self.p += 2

  def short_value(self):
    i = self.store[self.s] #the value in store[s] is the address of the variable we want so i is now the location of the variable
    #not moving s because we just want to pop the address of the variable off and replace it with the value
    self.set_store(self.s, self.store[i]) #we copy the value at i into the store
    self.p += 1

  def assign(self, length):
    #TODO this is probably broken
    #s is pointing to the last value (out of total $length values) that we want to copy
    #so s - length is the address of the variable we're copying into
    #and s - length + 1 is the beginning of the values to copy
    #after this we want the top of stack pointer to point at self.s - length (we've consumed the var address)
    val_addr = self.s - length + 1
    var_addr = self.store[self.s - length]
    self.s -= length + 1
    while length > 0: #so for each element in the var (possibly only the one) 
      self.set_store(var_addr, self.store[val_addr])
      var_addr += 1
      val_addr += 1
      length -= 1
    self.p += 2

  def goto(self, displ):
    self.p += displ

  def do(self, displ):
    if self.store[self.s] == 1: #store[s] is the result of whatever expression we're evaluating
      self.p += 2 #move past the DO, DISPL instruction into the loop body
    else:
      self.p += displ #jump to the end of the body

  '''
  #if statements like if B then S1 [else S2] compiles into: B DO(L1) S1 GOTO(L2) L1: S2, L2
  #basically just a do loop with an unconditional break at the end
  #thus no def if()
  '''

  def proc_call(self, level, displ):
    '''
    level is the number of levels back in the static link to follow
    displ is the displacement from p to the end of the proc call instruction (taking into account all the parameter lengths, etc)
    DEPRECATED: should only use func_call
    '''
    self.s += 1
    #trace static link back to the base
    log = 'Proc call: level %d displ %d ' % (level, displ)
    static_link = self.b
    log += 'static link now %d ' % self.b
    while level > 0:
      static_link = self.store[static_link]
      level -= 1
    self.set_store(self.s, static_link)
    self.set_store(self.s + 1, self.b) #store the current base address as the new dynamic link
    self.set_store(self.s + 2, self.p + 3) #current program instruction + 3 as new return address (3 because the proc call instr, level, displ and its the one AFTER those.)
    #debug(log)
    self.b = self.s
    self.s = self.b + 2
    self.p += displ

  def return_space(self, displ):
    for i in range(displ):
      self.s += 1
      self.store[self.s] = 'return space'
    #self.s += displ #we need enough space at top of stack to accomodate the return value
    self.p += 2

  def _return(self, param_length, return_length):
    #first copy return_length blocks from top of stack to the return address
    #do this in reverse order for convenience

    return_address_last = self.b - (param_length + 1)
    l = return_length
    s = self.s
    while l > 0:
      self.store[return_address_last] = self.store[s]
      return_address_last -= 1
      l -= 1
      s -= 1
   
    #then just go back to the return address as usual
    self.p = self.store[self.b + 2] #move p to the value stored in b + 2, which is the return address
    self.s = self.b #move the stack pointer back to b: b, when a proc call starts, points
                    #to the new activation record (which is the top of the stack), so b
                    #holds the top of the stack [after params were pushed] before the proc call
    self.s -= param_length + 1 #move the stack pointer back past all the params
    self.b = self.store[self.b + 1]

  def func_call(self, level, displ, return_length):
    '''
    level         is the number of levels back in the static link to follow
    displ         is the displacement from p to the end of the proc call instruction (taking into account all the parameter lengths, etc)
    return_length is the length of the return type
    '''
    #self.s += return_length + 1 #push the stack so that it's pointing at the end of the space the var will be returned to
    self.s += 1 #push the stack so that it's pointing at the end of the space the var will be returned to
    #trace static link back to the base
    log = 'Proc call: level %d displ %d ' % (level, displ)
    static_link = self.b
    log += 'static link now %d ' % self.b
    while level > 0:
      static_link = self.store[static_link]
      level -= 1
    self.set_store(self.s, static_link)
    self.set_store(self.s + 1, self.b) #store the current base address as the new dynamic link
    self.set_store(self.s + 2, self.p + 4) #current program instruction + 3 as new return address (3 because the proc call instr, level, displ and its the one AFTER those.)
    #debug(log)
    self.b = self.s
    self.s = self.b + 2
    self.p += displ

  def function(self, var_length, displ, return_length):
    for i in range(var_length):
      self.s += 1
      self.store[self.s] = 'var space'
    self.s += 1 #currently pointing at the return value location; we want to move 1 forward and then past the vars
    #self.s += var_length #move top of stack past the variable part
    self.p += displ #move the program pointer past displ (the number of instructions to invoke the proedure)

  def procedure(self, var_length, displ):
    '''
    DEPRECATED: use function
    '''
    self.s += var_length #move top of stack past the variable part
    self.p += displ #move the program pointer past displ (the number of instructions to invoke the proedure)

  def end_proc(self, param_length):
    '''
    DEPRECATED: only return now
    '''
    log = 'ending proc call, returning to instruction %d ' % self.store[self.b + 2]
    if self.s - param_length != self.b + 2:
      #TODO this check should occur once im sure how to get it right
      #self.error('At end of procedure call stack should be empty')
      pass
    self.p = self.store[self.b + 2] #move p to the value stored in b + 2, which is the return address
    self.s = self.b #move the stack pointer back to b: b, when a proc call starts, points
                    #to the new activation record (which is the top of the stack), so b
                    #holds the top of the stack [after params were pushed] before the proc call
    self.s -= param_length + 1 #move the stack pointer back past all the params
    self.b = self.store[self.b + 1]

  def program(self, var_length, displ):
    log = 'program var length = %d s before = %d ' % (var_length, self.s)
    self.s += var_length - 1 #functions that need to a free stack space will push it forward themselves, so we can actually just move it forward to point at the last variable
    log += 's after = %d' % self.s
    #debug(log)
    self.p += displ

  def write(self):
    val = self.store[self.s]
    print 'Writing %d'  % val
    self.out.write(chr(val))
    self.s -= 1
    self.p += 1
        
  def read(self):
    #address of the variable is the top of the stack
    var_addr = self.store[s]
    self.set_store(var_addr, int(raw_input()))
    self.s -= 1
    self.p += 1

  #######
  # BINARY OPERATIONS
  #######

  def binary_op(self, operation):
    #TODO very slow
    self.s -= 1
    x = self.store[self.s]
    y = self.store[self.s + 1]
    self.set_store(self.s, operation(x, y))
    #debug('storing %d at top of stack' % operation(x, y))
    self.p += 1

  def add(self):
    self.s -= 1
    self.set_store(self.s, self.store[self.s] + self.store[self.s + 1])
    self.p += 1

  def divide(self):
    self.binary_op(lambda x, y: x / y)

  def multiply(self):
    self.binary_op(lambda x, y: x * y)

  def subtract(self):
    self.binary_op(lambda x, y: x - y)

  def mod(self):
    self.binary_op(lambda x, y: x % y)

  def log_and(self):
    self.binary_op(lambda x, y: y == 1 if x == 1 else 0)

  def log_or(self):
    self.binary_op(lambda x, y: y == 1 if x == 0 else 1)

  def lt(self):
    self.s -= 1
    print 'Is %d < %d' % (self.store[self.s], self.store[self.s + 1])
    self.set_store(self.s, 1 if self.store[self.s] < self.store[self.s + 1] else 0)
    self.p += 1

  def lte(self):
    self.binary_op(lambda x, y: 1 if x <= y else 0)

  def eq(self):
    self.binary_op(lambda x, y: 1 if x == y else 0)

  def gte(self):
    self.binary_op(lambda x, y: 1 if x >= y else 0)

  def gt(self):
    self.s -= 1
    self.set_store(self.s, 1 if self.store[self.s] > self.store[self.s + 1] else 0)
    self.p += 1

  def ne(self):
    self.binary_op(lambda x, y: 1 if x != y else 0)

  def bitwise_and(self):
    self.binary_op(lambda x, y: x & y)

  def bitwise_or(self):
    self.binary_op(lambda x, y: x | y)

  def bitwise_lshift(self):
    self.binary_op(lambda x, y: x << y)

  def bitwise_rshift(self):
    self.binary_op(lambda x, y: x >> y)

  ######
  # UNARY OPERATIONS
  ######

  def unary_op(self, operation):
    x = self.store[self.s]
    self.set_store(self.s, operation(x))
    self.p += 1

  def log_not(self):
    self.unary_op(lambda x: 1 if x == 0 else 0)

  def minus(self):
    self.unary_op(lambda x: -x)

  def interpret(self, debug_mode = False):
    no_arg = {
      Op.ADD: self.add,
      Op.AND: self.log_and,
      Op.DIVIDE: self.divide,
      Op.EQUAL: self.eq,
      Op.GREATER: self.gt,
      Op.LESS: self.lt,
      Op.MINUS: self.minus,
      Op.MODULO: self.mod,
      Op.MULTIPLY: self.multiply,
      Op.NOT: self.log_not,
      Op.NOTEQUAL: self.ne,
      Op.NOTGREATER: self.lte,
      Op.NOTLESS: self.gte,
      Op.OR: self.log_or,
      Op.SHORTVALUE: self.short_value,
      Op.SUBTRACT: self.subtract,
      Op.READ: self.read,
      Op.WRITE: self.write,
      Op.BITAND: self.bitwise_and,
      Op.BITOR: self.bitwise_or,
      Op.BITLSHIFT: self.bitwise_lshift,
      Op.BITRSHIFT: self.bitwise_rshift
    }

    one_arg = {
      Op.ASSIGN: self.assign,
      Op.CONSTANT: self.constant,
      Op.DO: self.do,
      Op.ENDPROC: self.end_proc,
      Op.FIELD: self.field,
      Op.GOTO: self.goto,
      Op.LOCALVAR: self.local_var,
      Op.VALUE: self.value
    }

    code = self.code
    while True:
      op = code[self.p]
      try:
        debug('-- %s' % reverse_bytecodes[op])
      except KeyError:
        debug('-- %s' % op)

      if debug_mode:
        debug('STACK: ' + str(self.store[:self.s + 1]))

      if op in no_arg:
        no_arg[op]()
      elif op in one_arg:
        one_arg[op](code[self.p + 1])
      elif op == Op.ENDPROG:
        break
      elif op == Op.INDEX:
        p = self.p
        self.index(code[p + 1],code[p + 2], code[p + 3], code[p + 4])
      elif op == Op.PROCCALL:
        p = self.p
        self.proc_call(code[p + 1], code[p + 2])
      elif op == Op.PROCEDURE:
        p = self.p
        self.procedure(code[p + 1], code[p + 2])
      elif op == Op.PROGRAM:
        p = self.p
        self.program(code[p + 1], code[p + 2])
      elif op == Op.VARIABLE:
        p = self.p
        self.variable(code[p + 1], code[p + 2])
      elif op == Op.VARPARAM:
        p = self.p
        self.var_param(code[p + 1], code[p + 2])
      elif op == Op.FUNCTION:
        p = self.p
        self.function(code[p + 1], code[p + 2], code[p + 3])
      elif op == Op.FUNCCALL:
        p = self.p
        self.func_call(code[p + 1], code[p + 2], code[p + 3])
      elif op == Op.RETURNSPACE:
        self.return_space(code[self.p + 1])
      elif op == Op.RETURN:
        p = self.p
        self._return(code[p + 1], code[p + 2])
      else:
        self.error('Unexpected opcode %d' % op)

if __name__ == '__main__':
  debug_mode = '-d' in sys.argv or '--debug' in sys.argv
  set_debug(debug_mode)
  interp = Interpreter(sys.stdout, filename = sys.argv[1])
  interp.interpret(debug_mode = debug_mode)
