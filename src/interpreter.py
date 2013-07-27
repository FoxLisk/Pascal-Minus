from copy import copy
from administration_functions import get_code, debug, set_debug
from bytecodes import Op, reverse_bytecodes, bytecodes
import sys


class Interpreter:
  def __init__(self, out, filename = None, code = None):
    if (filename is None) == (code is None):
      raise Exception("Must pass in a filename XOR a list of bytecodes")
    if filename is not None:
      self.store = get_code(filename)
    else:
      self.store = copy(code)
    debug('loaded %d words of program code' % len(self.store))
    self.code_length = len(self.store)
    self.p = 0
    self.b = self.code_length
    self.s = self.code_length + 3
    self.out = out
    debug('setup done: b: %d s %d' % (self.b, self.s))

  def error(self, msg):
    print 'FATAL ERROR: STACK'
    print self.store[code_length:]
    raise Exception(msg)

  def set_store(self, loc, val):
    '''
    use this to set values in the stack instead of doing it manually, it handles
    resizing & mis-addressing for you
    '''
    diff = loc - len(self.store) + 1 #0-based indexing
    while diff > 0:
      self.store.append(-1)
      diff -= 1
    if loc < self.code_length:
      error('Trying to overwrite program instructions')
    #print 'setting store[%d] to %d' % (loc, val)
    self.store[loc] = val

  def variable(self, level, displ):
    self.s += 1
    x = self.b
    while level > 0: #move through the static links as many levels as necessary to find the variable in the correct stack frame
      x = self.store[x]
      level -= 1
    debug('storing var location of %d at top of stack %d' % (x + displ, self.s))
    self.set_store(self.s, x + displ) #set the top of the stack to the address of the sought variable
    self.p += 3 #move program three blocks forward (variable instruction is VARIABLE, LEVEL, DISPL)

  def var_param(self, level, displ):
    self.s += 1
    x = self.b
    while level > 0: #move through the static links as many levels as necessary to find the variable in the correct stack frame
      x = self.store[x]
      level -= 1
    var_loc = self.store[x + displ] #we need to grab the location of the variable that was passed in as a parameter
    debug('found var param at %d' % var_loc)
    self.set_store(self.s, var_loc)
    self.p += 3 #move program three blocks forward (variable instruction is VARIABLE, LEVEL, DISPL)

  def index(self, lower, upper, length, line_no):
    #we'll have something like ARRAY_VAR_ADDR, 5, OP.INDEX meaning to take the 5th element from the array pointed to by ARRAY_VAR_ADDR
    #length is the length of an element of the array, not the length of the array
    #so we want the top of the stack to be the ADDRESS of the 5th element of array_var_value
    i = self.store[self.s] #this is the index to dereference
    if i < lower or i > upper:
      error('Trying to dereference past the bounds of an array on line %d' % line_no)
    self.s -= 1
    #the address of the indexed variable is the displacement from the index (i - lower) times the length of an element
    #s() stores the address of the array to access currently, so we're replacing the location of the array with the location of the specific element
    addr = self.s + (i - lower) * length 
    self.set_store(addr, self.s)
    self.p += 3

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
    i = self.store[self.s] #the value in store(s()) is the address of the variable we want so i is now the location of the variable
    #not moving s() because we just want to pop the address of the variable off and replace it with the value
    while length > 0: #so for each element in the var (possibly only the one) 
      self.set_store(self.s, self.store[i]) #we copy the value at i into the store
      self.s += 1
      i += 1 #and move the pointer from the source var forward
      length -= 1
    self.s -= 1 #in the loop we moved one word past the end of the actual value
    self.p += 2

  def assign(self, length):
    #TODO this is probably broken
    #s() is pointing to the last value (out of total $length values) that we want to copy
    #so s() - length is the address of the variable we're copying into
    #and s() - length + 1 is the beginning of the values to copy
    val_addr = self.s - length + 1
    var_addr = self.store[self.s - length]
    tmp = var_addr
    log = 'Assigning '
    self.s -= length + 1
    while length > 0: #so for each element in the var (possibly only the one) 
      log += str(self.store[val_addr]) + ' '
      self.set_store(var_addr, self.store[val_addr])
      var_addr += 1
      val_addr += 1
      length -= 1
    log += 'to ' + str(tmp)
    debug(log)
    self.p += 2

  def goto(self, displ):
    self.p += displ

  def do(self, displ):
    debug('displ: %d' % displ)
    debug('Value at top of stack: %d' % self.store[self.s])
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
    '''
    debug('proc call: moving down %d levels of static chain' % level)
    self.s += 1
    #trace static link back to the base
    static_link = self.b
    while level > 0:
      static_link = self.store[static_link]
      level -= 1
    self.set_store(self.s, static_link)
    self.set_store(self.s + 1, self.b) #store the current base address as the new dynamic link
    self.set_store(self.s + 2, self.b + 3) #current program instruction + 3 as new return address (3 because the proc call instr, level, displ and its the one AFTER those.)
    self.b = s
    self.s = b + 2
    self.p += displ

  def procedure(self, var_length, displ):
    self.s += var_length #move top of stack past the variable part
    self.p += displ #move the program pointer past displ (the number of instructions to invoke the proedure)

  def end_proc(self, param_length):
    self.p = self.store[self.b + 2]#move p to the value stored in b() + 2, which is the return address
    self.s = self.b #move the stack pointer back to b()
    self.s -= param_length + 1#move the stack pointer back past all the params
    self.b += self.store[self.b + 1]

  def program(self, var_length, displ):
    log = 'program var length = %d s before = %d ' % (var_length, self.s)
    self.s += var_length - 1 #functions that need to a free stack space will push it forward themselves, so we can actually just move it forward to point at the last variable
    log += 's after = %d' % self.s
    debug(log)
    self.p += displ

  def write(self):
    debug('writing')
    val = self.store[self.s]
    debug('val: %d chr: %s' % (val, chr(val)))
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
    self.s -= 1
    x = self.store[self.s]
    y = self.store[self.s + 1]
    self.set_store(self.s, operation(x, y))
    debug('storing %d at top of stack' % operation(x, y))
    self.p += 1

  def add(self):
    self.binary_op(lambda x, y: x + y)

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
    self.binary_op(lambda x, y: 1 if x < y else 0)

  def lte(self):
    self.binary_op(lambda x, y: 1 if x <= y else 0)

  def eq(self):
    self.binary_op(lambda x, y: 1 if x == y else 0)

  def gte(self):
    self.binary_op(lambda x, y: 1 if x >= y else 0)

  def gt(self):
    self.binary_op(lambda x, y: 1 if x > y else 0)

  def ne(self):
    self.binary_op(lambda x, y: 1 if x != y else 0)

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

  def interpret(self):
    while True:
      try:
        op = int(self.store[self.p])
      except ValueError:
        op = bytecodes[self.store[self.p]]
      try:
        debug('-- %s' % reverse_bytecodes[op])
      except KeyError:
        debug('handling %s' % op)
      if op == Op.ADD:
        self.add()
      elif op == Op.AND:
        self.log_and()
      elif op == Op.ASSIGN:
        self.assign(self.store[self.p + 1])
      elif op == Op.CONSTANT:
        self.constant(self.store[self.p + 1])
      elif op == Op.DIVIDE:
        self.div()
      elif op == Op.DO:
        self.do(self.store[self.p + 1])
      elif op == Op.ENDPROC:
        self.end_proc(p() + 1)
      elif op == Op.ENDPROG:
        break
      elif op == Op.EQUAL:
        self.eq()
      elif op == Op.FIELD:
        self.field(self.store[self.p + 1])
      elif op == Op.GOTO:
        self.goto(self.store[self.p + 1])
      elif op == Op.GREATER:
        self.gt()
      elif op == Op.INDEX:
        p = self.p
        self.index(self.store[p + 1],self.store[p + 2], self.store[p + 3], self.store[p + 4])
      elif op == Op.LESS:
        self.lt()
      elif op == Op.MINUS:
        self.minus()
      elif op == Op.MODULO:
        self.mod()
      elif op == Op.MULTIPLY:
        self.multiply()
      elif op == Op.NOT:
        self.log_not()
      elif op == Op.NOTEQUAL:
        self.ne()
      elif op == Op.NOTGREATER:
        self.lte()
      elif op == Op.NOTLESS:
        self.gte()
      elif op == Op.OR:
        self.log_or()
      elif op == Op.PROCCALL:
        p = self.p
        self.proc_call(self.store[p + 1], self.store[p + 2])
      elif op == Op.PROCEDURE:
        p = self.p
        self.procedure(self.store[p + 1], self.store[p + 2])
      elif op == Op.PROGRAM:
        p = self.p
        self.program(self.store[p + 1], self.store[p + 2])
      elif op == Op.SUBTRACT:
        self.subtract()
      elif op == Op.VALUE:
        self.value(self.store[self.p + 1])
      elif op == Op.VARIABLE:
        p = self.p
        self.variable(self.store[p + 1], self.store[p + 2])
      elif op == Op.VARPARAM:
        p = self.p
        self.var_param(self.store[p + 1], self.store[p + 2])
      elif op == Op.READ:
        self.read()
      elif op == Op.WRITE:
        self.write()
      else:
        error('Unexpected opcode %d' % op)

if __name__ == '__main__':
  set_debug('-d' in sys.argv or '--debug' in sys.argv)
  interp = Interpreter(sys.stdout, filename = sys.argv[1])
  interp.interpret()
