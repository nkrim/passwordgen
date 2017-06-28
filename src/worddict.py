import os
import re
from shutil import copyfileobj
from tempfile import TemporaryFile, mkstemp

from .utils import *

class WordDictionary:
	class LengthSetMap:
		def __init__(self):
			self._words = [{''}]

		def __bool__(self):
			return self.maxlength() > 0

		def __getitem__(self, length):
			return self._words[length]

		def __iter__(self):
			return self._words.__iter__()

		def __len__(self):
			return len(self._words)

		def __str__(self):
			return '\n'.join(','.join(sorted(word_set)) for word_set in self._words[1:])

		def add(self, word, length=-1):
			if length < 0:
				length = len(word)
			while length >= len(self._words):
				self._words.append(set())
			self._words[length].add(word)

		def maxlength(self):
			for i in reversed(range(len(self._words))):
				if len(self._words[i]) > 0:
					return i
			return 0


	def __init__(self, words_file, wordmap=None):
		self.words_file = words_file
		if not wordmap:
			wordmap = WordDictionary.parse(self.words_file, formatted=True)
		self.wordmap = wordmap

	def getWordPool(self, length_lower=None, length_upper=None):
		if not length_upper:
			length_upper = length_lower

		if length_lower != None:
			pool = {w for lenset in self.wordmap[length_lower:length_upper+1] for w in lenset}
		else:
			pool = set()

		if not pool:
			pool = {w for lenset in self.wordmap[1:] for w in lenset}
			if not pool:
				pool = {w for w in self.wordmap[0]}
		return pool

	@staticmethod
	def parse(file_path, formatted=False):
		wordmap = WordDictionary.LengthSetMap()
		if formatted:
			length = 1
			with open(file_path, 'r') as f:
				for line in f:
					for w in line.split(','):
						w = w.strip()
						if w:
							wordmap.add(w, length)
					length += 1
		else:
			sub_re = re.compile(r'[\-\']')
			split_re = re.compile(r'[^a-zA-Z]+')
			with open(file_path, 'r') as f:
				for line in f:
					for w in split_re.split(sub_re.sub('', line)):
						if w:
							wordmap.add(w)
		return wordmap

	@staticmethod
	def backup(words_file):
		# Copy old `words.txt` to `words.txt.old`
		try:
			with open(words_file, 'r') as f:
				with open(words_file+'.old', 'w') as old:
					copyfileobj(f, old)
		except IOError:
			printerr('No formatted words file could be found at %r, skipping backup' % words_file)
		except:
			printerr('Could not backup words file from %r to %r' % (words_file, words_file+'.old'))
		else:
			return True
		return False

	@staticmethod
	def revert(words_file):
		# Revert `words.txt.old` to `words.txt`
		_, temp_file = mkstemp()
		old_file = words_file+'.old'
		try: 
			with open(old_file, 'r') as old:
				with open(temp_file, 'w') as temp:
					copyfileobj(old, temp)
		except IOError:
			printerr('No backup file found at %r' % old_file)
		except:
			printerr('Could not load backup file %r' % old_file)
		else:
			if WordDictionary.backup(words_file):
				try:
					with open(temp_file, 'r') as temp:
						with open(words_file, 'w') as f:
							copyfileobj(temp, f)
				except IOError:
					printerr('No words file found at %r' % words_file)
				except:
					printerr('Could not revert backup to %r, attempting to restore overwritten backup' % words_file)
					try: 
						with open(temp_file, 'r') as temp:
							with open(old_file, 'w') as old:
								copyfileobj(temp, old)
					except:
						printerr('Could not restore the overwritten backup. Backup is lost.')
				else:
					os.remove(temp_file)
					return True
		os.remove(temp_file)
		return False

	@staticmethod
	def setWordsFile(words_file, file_path, backup=True, formatted=False):
		# Read input file
		try:
			wordmap = WordDictionary.parse(file_path, formatted)
		except FileNotFoundError:
			printerr('Could not find file %r' % file_path)
			return None
		# Backup words file
		if backup:
			WordDictionary.backup(words_file)
		# Write new words file
		try: 
			with open(words_file, 'w') as f:
				f.write(str(wordmap))
		except Exception as e:
			printerr('Could not write new words file: %s' % e)
			return None
		# Return wordmap
		return WordDictionary(words_file, wordmap)