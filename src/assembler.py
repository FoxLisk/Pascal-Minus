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
  Op.MINUS,
  Op.MODULO,
  Op.MULTIPLY,
  Op.NOT,
  Op.NOTEQUAL,
  Op.NOTGREATER,
  Op.NOTLESS,
  Op.OR,
  Op.SUBTRACT,
  Op.VALUE,
  Op.VARIABLE,
  Op.VARPARAM,
  Op.READ,
  Op.WRITE,
}

def handle_pseudos(code):
  ''' grabs code emitted by the parser and builds up a table of labels
  to replace the defaddr and defarg instructions
  '''
  new_code = []
  tmp_labels = {}
  i = 0
  address = 0
  while i < len(code):
    op = code[i]
    if op == Op.DEFADDR:
      label_no = code[i+1]
      tmp_labels[label_no] = address
      debug('label %d: %d' % (label_no, address))
      i += 2
    elif op == Op.DEFARG:
      label_no = code[i+1]
      value = code[i+2]
      tmp_labels[label_no] = value
      debug('label %d: %d' % (label_no, value))
      i += 3
    else:
      #if we're skipping it just emit all the codes until the next instruction
      for j in range(code_lengths[op]):
        #we're storing the code without defaddr/defarg instructions in new_code
        #so we can just do another pass to put in jump displacements later
        new_code.append(code[i+j])
      i += code_lengths[op]
      address += code_lengths[op]
  return new_code, tmp_labels

def insert_labels(code, labels):
  new_code = []
  i = 0
  while i < len(code):
    op = code[i]
    if op in skip_codes:
      #if we're skipping it just emit all the codes until the next instruction
      for j in range(code_lengths[op]):
        #we're storing the code without defaddr/defarg instructions in new_code
        #so we can just do another pass to put in jump displacements later
        new_code.append(code[i+j])
      i += code_lengths[op]
    elif op == Op.PROGRAM or op == Op.PROCEDURE:
      #for these blocks the emitted code is
      #op, VAR_LABEL, BEGIN_LABEL
      #var_label will be a DEFARG instruction that is later defined
      #as the length of vars in the procedure
      #BEGIN_LABEL is a DEFADDR instruction that points to the next instruction
      #after the proc definition
      var_label = code[i + 1]
      begin_label = code[i + 2]
      var_length = labels[var_label]
      begin_displ = labels[begin_label] - i
      new_code.append(op)
      new_code.append(var_length)
      new_code.append(begin_displ)
      i += 3
    elif op == Op.DO or op == Op.GOTO:
      label = code[i + 1]
      displ = labels[label] - i
      new_code.append(op)
      new_code.append(displ)
      i += 2
    elif op == Op.PROCCALL:
      level = code[i + 1]
      label = code[i + 2]
      displ = labels[label] - i
      new_code.append(op)
      new_code.append(level)
      new_code.append(displ)
      i += 3
    else:
      raise Exception("Found unexpected operation %s" % bytecodes[op])
  return new_code

def emit_all(code):
  i = 0
  while i < len(code):
    op = code[i]
    l = code_lengths[op]
    emit_code(*code[i:i+l])
    i += l

def assemble(bytecodes):
  new_code, labels = handle_pseudos(bytecodes)
  new_code = insert_labels(new_code, labels)
  return new_code
