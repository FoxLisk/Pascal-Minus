import shutil
import os

files = ['administration_functions', 'administration', 'scanner', 'errors', 'symbols', 'parser', 'first']
for f in files:
  shutil.copy('../' + f + '.py', f + '.py')

os.system('python administration.py scantest out scan ')
f = open('temp1')
new = f.read()
f.close
f = open('correct_output')
good = f.read()
f.close()
if new != good:
  print 'Error: regression identified in scanner'

