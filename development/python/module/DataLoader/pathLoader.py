import os, sys
from . import DataLoader_typ


class PathLoader_typ(DataLoader_typ):

	def normPaths(self):
		for member in self.__dict__:

			if isinstance(self.__dict__[member], PathLoader_typ):
				self.__dict__[member].normPaths()

			if isinstance(self.__dict__[member], str):
				self.__dict__[member] = os.path.normcase(os.path.normpath(self.__dict__[member]))