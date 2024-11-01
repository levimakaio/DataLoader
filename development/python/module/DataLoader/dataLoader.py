#==================================================================================================
#
#Copyright 2024, LM Robotics , All rights reserved
#
# release Notes
#
#DataLoaded is a python class modifier to make saving, loading and displaying class configurations
#easier. DataLoader is desiged to be a parent class to any custom class. and provides methods to
# save and load cfgs in a .json format.
#
#    static Variables
#        cfgExclude      = []
#        types           = {}
#        printException  = {}
#        printIndentSize = 4
#
#    members:
#        None
#
#    Methods:
#        loadKW()
#        loadJson()
#        load_cfg_kwargs()
#        jsonOutput()
#        jsonOutputFormat()
#        jsonDumps()
#        saveJson(self, file)
#        DL_str(self)
#        __str__(self)
#
#    Example:
#
#        class myNewClass(DataLoader):
#
#            def __init__(self, args, **kwargs):
#
#                code for my class goes here
#
#                load_cfg_kwargs(cfgFile=None, **kwargs)
#
#
#
# 2024/03/05 version 0.8.0 Initial Release
#
#
#==================================================================================================
import json, os, ctypes

#TODO: see if there is a build in way to get this list
ctypesList = (
ctypes.c_bool,
ctypes.c_char,
ctypes.c_wchar,
ctypes.c_byte,
ctypes.c_ubyte,
ctypes.c_short,
ctypes.c_ushort,
ctypes.c_int,
ctypes.c_uint,
ctypes.c_long,
ctypes.c_ulong,
ctypes.c_longlong,
ctypes.c_ulonglong,
ctypes.c_size_t,
ctypes.c_ssize_t,
ctypes.c_float,
ctypes.c_double,
ctypes.c_longdouble,
ctypes.c_char_p,
ctypes.c_wchar_p,
ctypes.c_void_p)


def createMember(name, classType, jsonData):

	if jsonData is None:
		return classType()

	if name in jsonData:
		return classType(**jsonData[name])

	return classType()

def createDataLoaderClassfromDict(DataLoaderStruct, inDict):
#create nested dataLoader class from a dictionary object

	for key, value in inDict.items():

		#if value is a dictionary recursivly create subClasses
		if isinstance(value,dict):
			#input(value)
			#print(''.center(3,'\n'))
			DataLoaderStruct.__dict__[key] = DataLoader_typ()
			createDataLoaderClassfromDict(DataLoaderStruct.__dict__[key], value)
			continue

		#if value is a list check if list item is a dictionary
		if isinstance(value,list):
#			input(value)
			DataLoaderStruct.__dict__[key] = []
			for index, item in enumerate(value):
				if isinstance(item,dict):
					DataLoaderStruct.__dict__[key].append(createDataLoaderClassfromDict(DataLoader_typ(), item))
				else:
					DataLoaderStruct.__dict__[key].append(item)
			continue

		#add value to key
		DataLoaderStruct.__dict__[key] = value


	return DataLoaderStruct

def indentString(string, indentSize = 4):
	#add whiteSpace at the begining of each line of a string

	if string == '':
		return ''

	whiteSpace  = ' '*indentSize

	splitString = (whiteSpace + string).split('\n')
	if string[-1] == '\n':
		return ('\n' + whiteSpace).join(splitString[:-1]) + '\n'
	else:
		return ('\n' + whiteSpace).join(splitString)  + '\n'

def formatedString(key,value, lspace = 30):
	return f'{(key +":").ljust(lspace,"-")} {value} \n'

def subString(key, value, indentSize):

		#return a formated string of each of the members in this class and indent it one level.
		# If there are structures as members this will recursivly create a string and add an indent for each level
		return f'{(key +":")} \n' + indentString(value.__str__(), indentSize)

def valueString(key, value, indentSize=4, maxArrayLen = 10):

		#if this is a cTypes array
		if isinstance(value, ctypes.Array):

				#loop Though each value of ths array 
				string = ''
				for index, item in enumerate(value):

					#if array is longer then 10 values then after the 10th
					#value displaythe last value and break 
					if index > maxArrayLen:
						string += '.....'.center(30) + '\n'
						string += valueString(f'{key}[{len(value)-1}]',item, indentSize)
						break

					#if the value in the array is of type DataLoader_typ then display the contents of the structure 
					if isinstance(item,DataLoader_typ):
						string += subString(f'{key}[{index}]',item, indentSize)

					#display the value of each item in the array
					else:
						string += valueString(f'{key}[{index}]',item, indentSize)

				#return the array with the contents indented one level from the name
				return f'{key}:\n' + indentString(string, indentSize)

#		if isinstance(value, (ctypes._SimpleCData) ):
#			return f'{(key +":").ljust(30,"-")} Pointer \n'

		if isinstance(value, (ctypes._Pointer) ):
			return pointerString(key, value)

		#if not an array then return a string with a formated name and value
		return formatedString(key,value)

def pointerString(key, value, indentSize=4):

	if value:
		if isinstance(value.contents, ctypes.Array):
			return 'Array'
		else:
			return subString(f'*{key}', value.contents, indentSize)
	else:
		return f'*{(key +":").ljust(30,"-")} Null \n'

def getMembers(structure):

	#TODO: findout if there is a build in function that does this
		
	#check if the structure is Ctypes.  If it is create a dictionary from the _feilds_ list
	#otherwise use the build in vale of __dict__
	if isinstance(structure, ctypes.Structure):
		return dict( (f[0], getattr(structure, f[0]) ) for f in structure._fields_)
	else:
		return structure.__dict__


def printException_expandDict(self, key, value):
	string = ''
	for eventKey, event in value.items():
		string+= subString(eventKey, event, self.printIndentSize)
	return f'{(key +":")} \n' + indentString(string, 4)


#This should go in my json lib and is a fragile function right now so I need to monitor it when I use it
class MyJSONEncoder(json.JSONEncoder):

	def __init__(self, arrLen = 10, *args, **kwargs):
		super(MyJSONEncoder, self).__init__(*args, **kwargs)
		self.depth   = 0
		self.spacing = 4 #TODO I not sure how to dynamicly change this right now
		self.arrLen  = arrLen   # max array length that will display on a single row, if linger it will become a column vector for display

	#Chagne indenting of dict values in the json format
	def encode(self, obj):

		#handle Dictionary objects
		if isinstance(obj, dict):
			output = []
			self.depth += 1

			string = "{\n"
			for key, value in obj.items():
				output.append(''.center(self.depth*self.indent + (self.depth-1)*self.spacing) +  (json.dumps(key) + ": ").ljust(self.spacing) + self.encode(value))
			string += ",\n".join(output)
			string += "\n"
			string += ''.center((self.depth-1)*self.indent + (self.depth-1)*self.spacing) + "}"

			self.depth -=1

			return string
			
		#handle lsit objects
		if isinstance(obj, list):
			output = []
			self.depth += 1

			if len(obj) < self.arrLen:
				string = "["
				for value in obj:
					output.append(self.encode(value))
				string += ", ".join(output)
#				string += "\n"
				string += "]"

				self.depth -=1

			else:
				string = "[\n"
				for value in obj:
					output.append(''.center(self.depth*self.indent + (self.depth-1)*self.spacing) +  self.encode(value))
				string += ",\n".join(output)
				string += "\n"
				string += ''.center((self.depth-1)*self.indent + (self.depth-1)*self.spacing) + "]"

				self.depth -=1

			return string


		#handle all other
		else:
			return json.dumps(obj, indent = self.indent)

class DataLoader_typ():

	#list of class members to exclude when saving out a jsonCfg.
	#Examples of values to exclude would be pointer values as
	#these will not save to jsonFormat or variable data that
	#will be diffrent each session or that is saved in a different
	#file and uploaded
	cfgExclude   = []

	#Member data types.  this list will not load values from kwargs if the type is not correct
	# Example:
	#    types['memberName'] = str
	types        = {}

	#print method exception for class member.  provide an alternitive string return for this member
	# Example:
	#    printException['memberName'] = StrFunc(self, key, value)
	printException  = {}

	#indent size for printing
	printIndentSize = 4

	def __init__(self, cfgFile=None, createNew=False, **kwargs):
		self.load_cfg_kwargs(cfgFile=cfgFile, createNew=createNew, **kwargs)

#cfg Loading
	def loadKW(self,**kwargs):

		members = getMembers(self)

		#loop through given key words 
		for key, value in kwargs.items():

			#if key words is not of the specified type give warning and continue with next key
			if key in self.types:
				if not isinstance(value, self.types[key]):
					input(f'"{value}" must be of type {self.types[key]} for member "{key}"')
					continue 

			if key in members:

				#recusivly handle members of DataLoader type
				if isinstance(members[key], DataLoader_typ):
					members[key].loadKW(**value)
					continue

				#handle ctype arrays
				if isinstance(members[key], ctypes.Array):

					#handle values in array are dataLaoder Type
					if isinstance(members[key][0], DataLoader_typ):

						for index in range(members[key].__len__()):
							members[key][index].loadKW(**value[index])
						continue

					#load array values
					arr = (members[key]._type_ * members[key].__len__())(*value)
					self.__setattr__(key,arr)
					continue

				#handle basic types
				self.__setattr__(key,value)
				continue

			#if key is not a member strucutre then give warning and move on
			input(f'"{key}" not a member of {type(self)}')
			continue

	def loadJson(self, file):

		#Check if file exits
		if os.path.isfile(file):

			# Open JSON file
			with open(file) as fp: 
				jsonData = json.load(fp)

			self.loadKW(**jsonData)

		else:
			value = input(f'file:\n\n\t "{file}" \n\ndoes not exist. Would you like to create it? Y/N:\n\n\t' )

			if value.lower() in ['y', 'yes']:
				self.saveJson(file)

	def load_cfg_kwargs(self, cfgFile=None, createNew=False, **kwargs):

		#Load configuration file if specified
		if cfgFile is not None:

			#Check if file exits
			if os.path.isfile(cfgFile):
				with open(cfgFile) as fp:
					jsonData = json.load(fp)

#				self.loadJson(cfgFile)
			else:
				input(f'cfgFile:\n\n\t "{cfgFile}" \n\ndoes not exist.')
				jsonData = {}

		else:
			jsonData = {}

		#append kwargs to cfg values
		#kwargs will overwrite cfg values
		jsonData.update(kwargs)

		#Overwrite cfg values for key words that are provided
		if not createNew:
			#will only write data to existing members
			self.loadKW(**jsonData)
		else:
			#will create members that do not exist
			createDataLoaderClassfromDict(self, jsonData)

		return self

#jsonOutputs

	def jsonOutput(self, cfgExclude = []):
		output = {}

		for key, value in getMembers(self).items():

			if key in cfgExclude:
				continue

			if isinstance(value, DataLoader_typ):
				output[key] = value.jsonOutput(value.cfgExclude)
				continue

			if isinstance(value, (ctypes._Pointer) ):
				output[key] = None
				continue

			output[key] = self.jsonOutputFormat(value)
#			input(output[key])

			try:
				json.dumps(output[key])
			except:
				output[key] = str(value)


		return output

	def jsonOutputFormat(self, value):

		if isinstance(value, dict):
			output = {}
			for key, dictValue in value.items():
#				print(key)
#				input(dictValue)
				if isinstance(dictValue, DataLoader_typ):
					output[key] = dictValue.jsonOutput(dictValue.cfgExclude)
				else:
					output[key] = self.jsonOutputFormat(dictValue)

			return output

		if isinstance(value, list):
			output = []
			for listValue in value:
				if isinstance(listValue, DataLoader_typ):
					output.append(listValue.jsonOutput(listValue.cfgExclude))
				else:
					output.append(self.jsonOutputFormat(listValue))

			return output



		#if this is a cTypes array
		if isinstance(value, ctypes.Array):

			arr = []
			for index, item in enumerate(value):

				#handle nested 
				if isinstance(item,DataLoader_typ):
					arr.append(item.jsonOutput(item.cfgExclude))

				#display the value of each item in the array
				else:
					arr.append(item)

			#return the array with the contents indented one level from the name
			return arr

		#if not an array then return a string with a formated name and value
		return value

	def jsonDumps(self, indent = 4):
		return json.dumps(self.jsonOutput(self.cfgExclude), indent=indent, cls=MyJSONEncoder)

	def saveJson(self, file, overWrite=False):


		if overWrite==False:
			#Check if file exits
			if os.path.isfile(file):
				overWrite = input(f'file:\n\n\t"{file}"\n\n already exists, do you want to overwrite it? y/n')
				if overWrite.lower() in ['y', 'yes']:
					overWrite = True
				else:
					overWrite = False
			else:
				overWrite=True

		if overWrite:
			with open(file, 'w') as fp:
				fp.write(self.jsonDumps(indent = 4))

#Print outputs

	def DL_str(self):
		string = ''

		for key, value in getMembers(self).items():

			if key in self.printException:
				string += self.printException[key](self, key, value)
				continue

			# recursivly get the all the members for this currrent member in this class
			#and return a string with each nested depth indented
			if isinstance(value, DataLoader_typ):
				string += subString(key,value, self.printIndentSize)
				continue

			# get a foramted string of the name and value
			# of the current member of this class 
			string += valueString(key, value, self.printIndentSize)

		return string

	def __str__(self):
		return self.DL_str()


#Copyright 2024, LM Robotics , All rights reserved