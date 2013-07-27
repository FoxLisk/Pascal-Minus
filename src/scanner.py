from sets import Set
from errors import Errors
from administration_functions import error
from symbols import symbols, reverse_symbols

class WordType:
  def __init__(self, text, is_name, index):
    self.text = text
    self.is_name = is_name
    self.index = index
  def __str__(self):
    return self.text

class Scanner:
  ETX = -1
  invisible = Set([chr(x) for x in range(0, 40) if chr(x) not in ' \n'])
  letters = list('abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ_')
  separators = [' ', '\n', '{']
  standard_names = ['Integer', 'Boolean', 'False', 'True', 'Read', 'Write']
  digits = [str(x) for x in range(10)]


  def __init__(self, source):
    self.ch = None
    self.seen_proc = False
    self.line_no = 1
    self.tokens = []
    self.symbol_table = {}
    self.next_name_index = 1

    for symbol, idx in symbols.items():
      self.insert_word(False, symbol)
    for name in Scanner.standard_names:
      self.insert_word(True, name)

    #setup all the code in memory
    f = open(source)
    self.code = f.read()
    f.close()
    def chars():
      for c in self.code:
        yield c
    self.chars = chars()
   
  def emit(self, *vals):
    map(lambda v: self.tokens.append(v), vals)

  def begin_line(self, new_line_no):
    self.line_no = new_line_no
    #print 'new line, emitting %d, %d' % (symbols['\n'], new_line_no)
    self.emit(symbols['\n'], new_line_no)

  def end_line(self):
    self.line_no += 1
    self.begin_line(self.line_no)

  def insert_word(self, is_name, name):
    if is_name:
      index = self.next_name_index
      self.next_name_index += 1
    else:
      index = symbols[name]
    self.symbol_table[name] = WordType(name, is_name, index)

  def search(self, name):
    if name in self.symbol_table:
      sym = self.symbol_table[name]
      return sym.is_name, sym.index
    else:
      #if it's a new identifer it's definitely a name (not a reserved word)
      self.insert_word(True, name)
      return self.search(name)

  def next_char(self):
    try:
      self.ch = self.chars.next()
      if self.ch in Scanner.invisible:
        self.next_char() #TODO make this not recursive guhh
    except StopIteration:
      self.ch = Scanner.ETX

  def skip_separators(self):
    while self.ch in Scanner.separators:
      if self.ch == ' ':
        self.next_char()
      elif self.ch == '\n':
        self.end_line()
        self.next_char()
      elif self.ch == '{':
        self.comment()

  def comment(self):
    #ch = '{'
    self.next_char()
    while self.ch not in ['}', Scanner.ETX]:
      if self.ch == '{':
        self.comment()
      elif self.ch == '\n':
        self.end_line()
      self.next_char()
    if self.ch == '}':
      self.next_char()
    else:
      error(Errors.COMMENT)

  def next_symbol(self):
    self.skip_separators()
    if self.ch in Scanner.letters:
      self.scan_word()
    elif self.ch in Scanner.digits:
      self.scan_numeral()
    elif self.ch == '<':
      self.scan_less()
    elif self.ch == '>':
      self.scan_greater()
    elif self.ch == '.':
      self.scan_dots()
    elif self.ch == ':':
      self.scan_colon()
    elif self.ch in symbols:
      self.scan_symbol()
    elif self.ch != Scanner.ETX:
      self.scan_unknown()

  def scan_numeral(self):
    acc = ''
    while self.ch in Scanner.digits:
      acc += self.ch
      self.next_char()
    self.emit(symbols['numeral'], int(acc))

  def scan_word(self):
    #print 'scanning word'
    accum = ''
    while self.ch in Scanner.letters or self.ch in Scanner.digits:
      accum += self.ch
      self.next_char()
    #print 'found word %s' % accum
    is_name, index = self.search(accum)
    if is_name:
      #print 'is name: emitting %d, %d' % (symbols['name'], index)
      self.emit(symbols['name'], accum)
    else:
      #print 'is reserved word, emitting %d' % index
      self.emit(index)

  def scan_symbol(self):
    self.emit(symbols[self.ch])
    self.next_char()

  def scan_less(self):
    #assume ch = '<'
    self.next_char()
    if self.ch == '=':
      self.emit(symbols['<='])
      self.next_char()
    elif self.ch == '>':
      self.emit(symbols['<>'])
      self.next_char()
    else:
      self.emit(symbols['<'])

  def scan_greater(self):
    #assume ch = '>'
    self.next_char()
    if self.ch == '=':
      self.emit(symbols['>='])
      self.next_char()
    else:
      self.emit(symbols['>'])

  def scan_dots(self):
    #assume ch = '.'
    self.next_char()
    if self.ch == '.':
      self.emit(symbols['..'])
      self.next_char()
    else:
      self.emit(symbols['.'])

  def scan_colon(self):
    #assume ch = ':'
    self.next_char()
    if self.ch == '=':
      self.emit(symbols[':='])
      self.next_char()
    else:
      self.emit(symbols[':'])

  def scan_unknown(self):
    self.emit(symbols['unknown'])
    self.next_char()

  def scan(self):
    #keep the scanner always one character ahead
    #this allows us to handle scanning multi-char symbols (<=)
    #without having to deal with remember whether we're ahead
    #or not
    #this works bc LL1
    self.next_char()
    while self.ch != Scanner.ETX:
      self.next_symbol()
    self.emit(symbols['endtext'])
    return self.tokens
