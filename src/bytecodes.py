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
  33: 'DEFARG'
}

bytecodes = {y:x for x, y in reverse_bytecodes.items()}
