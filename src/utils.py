from __future__ import print_function
import sys

# Alias FileNotFoundError for python 2
try: 
	FileNotFoundError
except NameError:
	FileNotFoundError = IOError	

# Alias/shortcut for error printing
def printerr(*args, **kwargs):
	print(*args, file=sys.stderr, **kwargs)