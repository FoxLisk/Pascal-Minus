from bytecodes import Op, reverse_bytecodes, bytecodes, code_lengths
from administration_functions import debug
import sys

skip_codes = {
  Op.ADD,
  Op.AND,
  Op.ASSIGN,
  Op.CONSTANT,
  Op.DIVIDE,
  Op.ENDPROG,
  Op.ENDPROC,
  Op.EQUAL,
  Op.FIELD,
  Op.GREATER,
  Op.INDEX,
  Op.LESS,
  Op.LOCALVAR,
  Op.MINUS,
  Op.MODULO,
  Op.MULTIPLY,
  Op.NOT,
  Op.NOTEQUAL,
  Op.NOTGREATER,
  Op.NOTLESS,
  Op.OR,
  Op.SHORTVALUE,
  Op.SUBTRACT,
  Op.VALUE,
  Op.VARIABLE,
  Op.VARPARAM,
  Op.READ,
  Op.WRITE,
}

class Assembler:
  def __init__(self, bytecodes):
    self.bytecodes = bytecodes
    self.labels = {}

  def handle_pseudos(self):
    ''' grabs code emitted by the parser and builds up a table of labels
    to replace the defaddr and defarg instructions
    '''
    self.pseudos_replaced = []
    i = 0
    address = 0
    while i < len(self.bytecodes):
      op = self.bytecodes[i]
      #print 'handling opcode %s' % reverse_bytecodes[op]
      if op == Op.DEFADDR:
        label_no = self.bytecodes[i + 1]
        self.labels[label_no] = address
        debug('label %d: %d' % (label_no, address))
        i += 2
      elif op == Op.DEFARG:
        label_no = self.bytecodes[i + 1]
        value = self.bytecodes[i + 2]
        self.labels[label_no] = value
        debug('label %d: %d' % (label_no, value))
        i += 3
      else:
        #if we're skipping it just emit all the codes until the next instruction
        for j in range(code_lengths[op]):
          #we're storing the code without defaddr/defarg instructions in new_code
          #so we can just do another pass to put in jump displacements later
          self.pseudos_replaced.append(self.bytecodes[i + j])
        i += code_lengths[op]
        address += code_lengths[op]

  def insert_labels(self):
    self.assembled = []
    i = 0
    while i < len(self.pseudos_replaced):
      op = self.pseudos_replaced[i]
      if op in skip_codes:
        #if we're skipping it just emit all the codes until the next instruction
        for j in range(code_lengths[op]):
          #we're storing the code without defaddr/defarg instructions in new_code
          #so we can just do another pass to put in jump displacements later
          self.assembled.append(self.pseudos_replaced[i+j])
        i += code_lengths[op]
      elif op == Op.PROGRAM or op == Op.PROCEDURE:
        #for these blocks the emitted code is
        #op, VAR_LABEL, BEGIN_LABEL
        #var_label will be a DEFARG instruction that is later defined
        #as the length of vars in the procedure
        #BEGIN_LABEL is a DEFADDR instruction that points to the next instruction
        #after the proc definition
        var_label = self.pseudos_replaced[i + 1]
        begin_label = self.pseudos_replaced[i + 2]
        var_length = self.labels[var_label]
        begin_displ = self.labels[begin_label] - i
        debug('Handling block: var label %d, length %d | being label %d, displ %d' % (var_label, var_length, begin_label, begin_displ))
        self.assembled.append(op)
        self.assembled.append(var_length)
        self.assembled.append(begin_displ)
        i += 3
      elif op == Op.DO or op == Op.GOTO:
        label = self.pseudos_replaced[i + 1]
        displ = self.labels[label] - i
        self.assembled.append(op)
        self.assembled.append(displ)
        i += 2
      elif op == Op.PROCCALL:
        level = self.pseudos_replaced[i + 1]
        label = self.pseudos_replaced[i + 2]
        displ = self.labels[label] - i
        self.assembled.append(op)
        self.assembled.append(level)
        self.assembled.append(displ)
        i += 3
      else:
        raise Exception("Found unexpected operation %s" % bytecodes[op])

  def emit_all(self):
    i = 0
    while i < len(self.assembled):
      op = self.assembled[i]
      l = code_lengths[op]
      emit_code(*self.assembled[i:i+l])
      i += l

  def assemble(self):
    self.handle_pseudos()
    self.insert_labels()
    return self.assembled
