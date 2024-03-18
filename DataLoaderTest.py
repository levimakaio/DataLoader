import sys, os 
import json
import ctypes

currentPath = os.path.dirname(os.path.abspath(__file__))

sys.path.append(fr'{currentPath}\module')
from DataLoader import DataLoader_typ

D = ctypes.c_double


class myClass(DataLoader_typ):
	cfgExclude   = ['var1']
	types = {}
#	types['var3'] = (list,int)
	
	def var3_str_(self, key, value):
		return f'{value[0]}\n'
	
	printException  = {}
	printException['var3'] = var3_str_


	def __init__(self):
		self.Var2 = myClass2()
		self.var3 = [myClass2(),myClass2()]
		self.var1 = 10

class myClass2():
	cfgExclude   = ['var2']

	def __init__(self):
		self.var1 = 15
		self.var2 = 15

testClass = myClass()
#print(ctypes.pointer(D))
#testClass.newVar = ctypes.pointer(D)




#print(testClass.jsonDumps())
testClass.saveJson(fr'{currentPath}\\test.json')

testClass.load_cfg_kwargs(cfgFile=fr'{currentPath}\\test.json')

#with open(fr'{currentPath}\\test.json') as fp:
#	cfg = json.load(fp)

#print(cfg)

#testClass.load_cfg_kwargs(cfgFile=None, Var2={'var2':2})

print(testClass)

	# cfgExclude   = []
	# types        = {}
	# printException  = {}
