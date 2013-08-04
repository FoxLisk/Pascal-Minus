class Op:
  ADD = 1
  AND = 2
  ASSIGN = 3
  CONSTANT = 4
  DIVIDE = 5
  DO = 6
  ENDPROC = 7
  ENDPROG = 8
  EQUAL = 9
  FIELD = 10
  GOTO = 11
  GREATER = 12
  INDEX = 13
  LESS = 14
  MINUS = 15
  MODULO = 16
  MULTIPLY = 17
  NOT = 18
  NOTEQUAL = 19
  NOTGREATER = 20
  NOTLESS = 21
  OR = 22
  PROCCALL = 23
  PROCEDURE = 24
  PROGRAM = 25
  SUBTRACT = 26
  VALUE = 27
  VARIABLE = 28
  VARPARAM = 29
  READ = 30
  WRITE = 31
  DEFADDR = 32
  DEFARG = 33
  LOCALVAR = 34
  SHORTVALUE = 35
  BITAND = 36
  BITOR = 37
  BITLSHIFT = 38
  BITRSHIFT = 39
  RETURN = 40
  FUNCTION = 41
  FUNCCALL = 42
  RETURNSPACE = 44

reverse_bytecodes = {
  1: 'ADD',
  2: 'AND',
  3: 'ASSIGN',
  4: 'CONSTANT',
  5: 'DIVIDE',
  6: 'DO',
  7: 'ENDPROC',
  8: 'ENDPROG',
  9: 'EQUAL',
  10: 'FIELD',
  11: 'GOTO',
  12: 'GREATER',
  13: 'INDEX',
  14: 'LESS',
  15: 'MINUS',
  16: 'MODULO',
  17: 'MULTIPLY',
  18: 'NOT',
  19: 'NOTEQUAL',
  20: 'NOTGREATER',
  21: 'NOTLESS',
  22: 'OR',
  23: 'PROCCALL',
  24: 'PROCEDURE',
  25: 'PROGRAM',
  26: 'SUBTRACT',
  27: 'VALUE',
  28: 'VARIABLE',
  29: 'VARPARAM',
  30: 'READ',
  31: 'WRITE',
  32: 'DEFADDR',
  33: 'DEFARG',
  34: 'LOCALVAR',
  35: 'SHORTVALUE',
  36: 'BITAND',
  37: 'BITOR',
  38: 'BITLSHIFT',
  39: 'BITRSHIFT',
  40: 'RETURN',
  41: 'FUNCTION',
  42: 'FUNCCALL',
  44: 'RETURNSPACE'
}

bytecodes = {y:x for x, y in reverse_bytecodes.items()}

#map from codes to skip to the length (number of codes to skip when one is encountered)
code_lengths = {
  Op.ADD: 1,
  Op.AND: 1,
  Op.ASSIGN: 2,
  Op.CONSTANT: 2,
  Op.DIVIDE: 1,
  Op.DO: 2,
  Op.DEFADDR: 2, 
  Op.DEFARG: 3,
  Op.ENDPROC: 2,
  Op.ENDPROG: 1,
  Op.EQUAL: 1,
  Op.FIELD: 2,
  Op.GOTO: 2, 
  Op.GREATER: 1,
  Op.INDEX: 5, 
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
  Op.SHORTVALUE: 1,
  Op.SUBTRACT: 1,
  Op.VALUE: 2,
  Op.VARIABLE: 3,
  Op.VARPARAM: 3,
  Op.READ: 1,
  Op.WRITE: 1,
  Op.LOCALVAR: 2, #op displ
  Op.BITAND: 1,
  Op.BITOR: 1,
  Op.BITLSHIFT: 1,
  Op.BITRSHIFT: 1,
  Op.RETURN: 3,
  Op.FUNCTION: 4,
  Op.FUNCCALL: 4,
  Op.RETURNSPACE: 2
}
