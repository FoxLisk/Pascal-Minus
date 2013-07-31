symbols = ['and', 'array', '*', ':=', 'begin', ':', ',', 'const', 'div', 'do', '..', 'else', 'end', 'endtext', '=', '>', 'if', '[', '(', '<', '-', 'mod', 'name', '\n', 'not', '<>', '<=', '>=', 'numeral', 'of', 'or', '.', '+', 'procedure', 'program', 'record', ']', ')', ';', 'then', 'type', 'var', 'while', 'unknown', 'import']
symbols = {x: x for x in symbols}
reverse_symbols = {y:x for x, y in symbols.items()}

standard_types = ['Integer', 'Boolean']
standard_procs = ['Read', 'Write']
