from bytecodes import Op, reverse_bytecodes, bytecodes
from administration_functions import get_code, emit_code
import sys

#map from codes to skip to the length (number of codes to skip when one is encountered)
code_lengths = {
  Op.ADD: 1,
  Op.AND: 1,
  Op.ASSIGN: 2,
  Op.CONSTANT: 2,
  Op.DIVIDE: 1,
  Op.DO: 2,
  Op.ENDPROC: 2,
  Op.ENDPROG: 1,
  Op.EQUAL: 1,
  Op.FIELD: 2,
  Op.GOTO: 2, 
  Op.GREATER: 1,
  Op.INDEX: 4, 
  Op.LESS: 1,
  Op.MINUS: 1,
  Op.MODULO: 1,
  Op.MULTIPLY: 1,
  Op.NOT: 1,
  Op.NOTEQUAL: 1,
  Op.NOTGREATER: 1,
  Op.NOTLESS: 1,
  Op.OR: 1,
  Op.PROCCALL: 3,
  Op.PROCEDURE: 3,
  Op.PROGRAM: 3,
  Op.SUBTRACT: 1,
  Op.VALUE: 2,
  Op.VARIABLE: 3,
  Op.VARPARAM: 3,
  Op.READ: 1,
  Op.WRITE: 1,
}

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

def handle_pseudos():
  ''' grabs code emitted by the parser and builds up a table of labels
  to replace the defaddr and defarg instructions
  '''
  tmp_code = get_code('temp2')
  new_code = []
  tmp_labels = {}
  i = 0
  address = 0
  while i < len(tmp_code):
    op = tmp_code[i]
    if op == Op.DEFADDR:
      label_no = tmp_code[i+1]
      tmp_labels[label_no] = address
      print 'label %d: %d' % (label_no, address)
      i += 2
    elif op == Op.DEFARG:
      label_no = tmp_code[i+1]
      value = tmp_code[i+2]
      tmp_labels[label_no] = value
      print 'label %d: %d' % (label_no, value)
      i += 3
    else:
      #if we're skipping it just emit all the codes until the next instruction
      for j in range(code_lengths[op]):
        #we're storing the code without defaddr/defarg instructions in new_code
        #so we can just do another pass to put in jump displacements later
        new_code.append(tmp_code[i+j])
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

def pass3():
  new_code, labels = handle_pseudos()
  new_code = insert_labels(new_code, labels)
  emit_all(new_code)
