from symbols import symbols
_firsts = {
  'FieldName': ["name"],
  'Name': ["name"],
  'Numeral': ["numeral"],
  'Constant': ["numeral", "name"],
  'FieldSelector': ["."],
  'IndexedSelector': ["["],
  'Selector': [".", "["],
  'VariableAccess': ["name"],
  'Factor': ["numeral", "name", "(", "not"],
  'Term': ["numeral", "name", "(", "not"],
  'AddingOperator': ["+", "-", "or"],
  'MultiplyingOperator': ["*", "div", "mod", "and", "|", "&", "<<", ">>"],
  'SignOperator': ["+", "-"],
  'SimpleExpression': ["+", "-", "numeral", "name", "(", "not"],
  'RelationalOperator': ["<", "=", ">", "<=", "<>", ">="],
  'Expression': ["+", "-", "numeral", "name", "(", "not"],
  'CompoundStatement': ["begin"],
  'WhileStatement': ["while"],
  'IfStatement': ["if"],
  'ActualParameter': ["+", "-", "numeral", "name", "(", "not"],
  'ActualParameterList': ["+", "-", "numeral", "name", "(", "not"],
  'ProcedureStatement': ["name"],
  'AssignmentStatement': ["name"],
  'Statement': ["name", "if", "while", "begin"],
  'ParameterDefinition': ["var", "name"],
  'FormalParameterList': ["var", "name"],
  'ProcedureBlock': ["(", ";"],
  'ProcedureDefinition': ["procedure"],
  'VariableGroup': ["name"],
  'VariableDefinition': ["name"],
  'VariableDefinitionPart': ["var"],
  'RecordSection': ["name"],
  'FIeldList': ["name"],
  'NewRecordType': ["record"],
  'IndexRange': ["numeral", "name"],
  'NewArrayType': ["array"],
  'NewType': ["array", "record"],
  'TypeDefinition': ["name"],
  'TypeDefinitionPart': ["type"],
  'ConstantDefinition': ["name"],
  'ConstantDefinitionPart': ["const"],
  'BlockBody': ["const", "type", "var", "procedure", "begin"],
  'Program': ["program"],
  'ImportStatement': ["import"],
  'Module': ["import", "program"]
}

_first_symbols = {}

for name, firsts in _firsts.items():
  _first_symbols[name] = []
  for sym in firsts:
    _first_symbols[name].append(symbols[sym])
  

def first(name):
  return _first_symbols[name]
