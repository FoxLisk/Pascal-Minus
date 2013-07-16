from sets import Set
from errors import Errors
from administration_functions import eof, emit, read, new_line, error
from symbols import symbols, reverse_symbols
ETX = -1
ch = None
invisible = Set([chr(x) for x in range(0, 40) if chr(x) not in ' \n'])
digits = [str(x) for x in range(10)]
letters = list('abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ')
separators = [' ', '\n', '{']

standard_names = ['Integer', 'Boolean', 'False', 'True', 'Read', 'Write']

seen_proc = False
def emit1(stype):
  #print "emitting %s" % reverse_symbols[stype]
  global seen_proc
  emit(stype)

def emit2(stype, val):
  global symbol_table, seen_proc
  emit(stype)
  emit(val)

line_no = 1

def begin_line(new_line_no):
  new_line(new_line_no)
  #print 'new line, emitting %d, %d' % (symbols['\n'], new_line_no)
  emit2(symbols['\n'], new_line_no)

def end_line():
  global line_no
  line_no += 1
  begin_line(line_no)

class WordType:
  def __init__(self, text, is_name, index):
    self.text = text
    self.is_name = is_name
    self.index = index
  def __str__(self):
    return self.text

symbol_table = {}

next_name_index = 1
def insert_word(is_name, name):
  global next_name_index, symbol_table
  if is_name:
    index = next_name_index
    next_name_index += 1
  else:
    index = symbols[name]
  symbol_table[name] = WordType(name, is_name, index)
  #print ['%s:%d' % (x, y.index) for x,y in symbol_table.items()]

for symbol, idx in symbols.items():
  insert_word(False, symbol)
for name in standard_names:
  insert_word(True, name)
 
def search(name):
  if name in symbol_table:
    sym = symbol_table[name]
    return sym.is_name, sym.index
  else:
    #if it's a new identifer it's definitely a name (not a reserved word)
    insert_word(True, name)
    return search(name)

def next_char():
  global ch
  if eof():
    ch = ETX
  else:
    ch = read()
    "  read %s" % ch
    if ch in invisible:
      next_char() #TODO make this not recursive guhh

def skip_separators():
  while ch in separators:
    if ch == ' ':
      next_char()
    elif ch == '\n':
      end_line()
      next_char()
    elif ch == '{':
      comment()

def comment():
  #ch = '{'
  next_char()
  while ch not in ['}', ETX]:
    if ch == '{':
      comment()
    elif ch == '\n':
      end_line()
    next_char()
  if ch == '}':
    next_char()
  else:
    error(Errors.COMMENT)

def next_symbol():
  skip_separators()
  if ch in letters:
    scan_word()
  elif ch in digits:
    scan_numeral()
  elif ch == '<':
    scan_less()
  elif ch == '>':
    scan_greater()
  elif ch == '.':
    scan_dots()
  elif ch == ':':
    scan_colon()
  elif ch in symbols:
    scan_symbol()
  elif ch != ETX:
    scan_unknown()

def scan_numeral():
  acc = ch
  while ch in digits:
    acc += ch
    next_char()
  emit2(symbols['numeral'], int(acc))

def scan_word():
  #print 'scanning word'
  accum = ''
  while ch in letters or ch in digits:
    accum += ch
    next_char()
  #print 'found word %s' % accum
  is_name, index = search(accum)
  if is_name:
    #print 'is name: emitting %d, %d' % (symbols['name'], index)
    emit2(symbols['name'], index)
    #emit2(symbols['name'], accum)
  else:
    #print 'is reserved word, emitting %d' % index
    emit1(index)

def scan_symbol():
  emit1(symbols[ch])
  next_char()

def scan_less():
  #assume ch = '<'
  next_char()
  if ch == '=':
    emit1(symbols['<='])
    next_char()
  elif ch == '>':
    emit1(symbols['<>'])
    next_char()
  else:
    emit1(symbols['<'])

def scan_greater():
  #assume ch = '>'
  next_char()
  if ch == '=':
    emit1(symbols['>='])
    next_char()
  else:
    emit1(symbols['>'])

def scan_dots():
  #assume ch = '.'
  next_char()
  if ch == '.':
    emit1(symbols['..'])
    next_char()
  else:
    emit1(symbols['.'])

def scan_colon():
  #assume ch = ':'
  next_char()
  if ch == '=':
    emit1(symbols[':='])
    next_char()
  else:
    emit1(symbols[':'])

def scan_unknown():
  emit1(symbols['unknown'])
  next_char()

def pass1():
  #keep the scanner always one character ahead
  #this allows us to handle scanning multi-char symbols (<=)
  #without having to deal with remember whether we're ahead
  #or not
  #this works bc LL1
  next_char()
  while ch != ETX:
    next_symbol()
  emit1(symbols['endtext'])
