symbols = ['and', 'array', '*', ':=', 'begin', ':', ',', 'const', 'div', 'do', '..', 'else', 'end', 'endtext', '=', '>', 'if', '[', '(', '<', '-', 'mod', 'name', '\n', 'not', '<>', '<=', '>=', 'numeral', 'of', 'or', '.', '+', 'procedure', 'program', 'record', ']', ')', ';', 'then', 'type', 'var', 'while', 'unknown']
symbols = {x: symbols.index(x) + 1 for x in symbols}
reverse_symbols = {y:x for x, y in symbols.items()}

