import argparse
import re
import readline
import pyperclip
import sys
from os import path

from .pattern import Pattern
from .worddict import WordDictionary
from .utils import *

# Argument Defaults
# =================
DEFAULT_PATTERN = '%d[4]%s=[2]%W[6-10]'
DEFAULT_PATTERN_NO_WORDS = re.sub(r'%W', r'%w', DEFAULT_PATTERN)
# Relavent Paths
# ==============
WORDS_FILE = path.join(path.dirname(path.abspath(__file__)), 'words', 'words.txt')
DEFAULT_WORDS_FILES_DIR = path.join(path.dirname(path.abspath(__file__)), 'words', 'defaults')
FALLBACK_WORDS_FILE = path.join(DEFAULT_WORDS_FILES_DIR, 'english.txt')


def main():
	try:
		return _main()
	except KeyboardInterrupt:
		printerr('--INTERRUPTED--')
		return 1
def _main():
	args = parser().parse_args()

	# WordDictionary ops
	worddict = None
	# Revert op `-R`
	if args.revert:
		WordDictionary.revert(WORDS_FILE)
	# New worddict op `-w`
	if args.worddict:
		print('Generating new words file from file: %r' % args.worddict)
		worddict = WordDictionary.setWordsFile(WORDS_FILE, args.worddict)
	# Default language worddict op `-l` 
	elif args.language:
		langdict_path = path.join(DEFAULT_WORDS_FILES_DIR, args.language.lower()+'.txt')
		if path.isfile(langdict_path):
			worddict = WordDictionary.setWordsFile(WORDS_FILE, langdict_path, formatted=True)
		else: 
			printerr('There is currently no dictionary for the language `%s`' % args.language)
			printerr('Make sure you are using the native name of the language ('
					+'i.e. `deutsch` instead of `german`), otherwise if the language you want to use isn\'t currently included, '
					+'try updating with pip, or consider making your own file for your language and forking this project to include '
					+'your language\'s dictionary (go to `https://github.com/nkrim/passwordgen` for more info)')
	# Fallback/current/default worddict compiling
	if not worddict:
		try: 
			worddict = WordDictionary(WORDS_FILE)
		except FileNotFoundError:
			worddict = None
			printerr('Could not find words file at %r...' % WORDS_FILE)
			# Attempt to restore from backup of previous words file
			if path.isfile(WORDS_FILE+'.old'):
				printerr('- Restoring from backup of previous words file:')
				worddict = WordDictionary.setWordsFile(WORDS_FILE, WORDS_FILE+'.old', backup=False, formatted=True)
				if not worddict:
					printerr('Restoration from backup failed.')
			# Attempt to yse
			if not worddict and path.isfile(FALLBACK_WORDS_FILE):
				printerr('- Loading fallback dictionary %r as new words file:' % path.basename(FALLBACK_WORDS_FILE))
				worddict = WordDictionary.setWordsFile(WORDS_FILE, FALLBACK_WORDS_FILE, backup=False, formatted=True)
				if not worddict:
					printerr('Loading from fallback failed.')
			if not worddict:
				printerr('- Could not generate new words file, can continue as long as pattern does not use the `W` signifier')

	# Set pattern as default, if necessary
	if args.pattern is None:
		if worddict:
			args.pattern = DEFAULT_PATTERN 
		else:
			printerr('Using an augmented default pattern to accomadate for the lack of a words file (%W signifiers are changed to %w)')
			args.pattern = DEFAULT_PATTERN_NO_WORDS
	# Throw error for empty-string pattern
	elif args.pattern == '':
		if worddict:
			printerr('Cannot use an empty string as the pattern. Continuing using default pattern: `%s`' % DEFAULT_PATTERN)
			args.pattern = DEFAULT_PATTERN
		else:
			printerr('Cannot use an empty string as the pattern. Continuing using default no-words pattern: `%s`' % DEFAULT_PATTERN_NO_WORDS)
			args.pattern = DEFAULT_PATTERN_NO_WORDS

	# Parse pattern
	try:
		pattern = Pattern(args.pattern, worddict)
	except ValueError as e:
		printerr('Error when compiling pattern with `%s`: %s' % (args.pattern, e))
		return 1

	# Generate password(s)
	if args.interactive:
		print('Entering interactive mode. Press enter to generate a new password. Enter a new pattern at any time to use instead, if valid.')
		print('  Enter `q` to quit')
		print('  Generating using pattern: `%s`' % pattern)
		quit = False
		while not quit:
			try:
				out = pattern.generate()
			except ValueError as e:
				printerr('Error when generating password: %s' % e)
				return 1
			if args.copy:
				pyperclip.copy(out)
				print('  Copying to clipboard')
			print(out)
			if sys.version_info[0] < 3:
				instr = raw_input('> ').strip()
			else:
				instr = input('> ').strip()
			if instr:
				if instr == 'q':
					quit = True
				else:
					try:
						newpattern = Pattern(instr, worddict)
					except ValueError as e:
						print('  Enter `q` to quit')
						printerr('  Error when compiling pattern with `%s`: %s' % (instr, e))
					else:
						pattern = newpattern
						print('  Enter `q` to quit')
						print('  Generating using pattern: `%s`' % pattern)

	else:
		print('  Generating using pattern: `%s`' % pattern)
		out = pattern.generate()
		if args.copy:
			pyperclip.copy(out)
			print('  Copying to clipboard')
		print(out)
	return 0
		

def parser():
	parser = argparse.ArgumentParser(	description='Generate random passwords using a pattern ot specify the general format.',
										epilog=howto(),
										formatter_class=argparse.RawDescriptionHelpFormatter)
	parser.add_argument(	'pattern',
							nargs='?',
							default=None,
							help='The pattern to use to generate the password (defaults to `{}`)'.format(re.sub(r'%',r'%%',DEFAULT_PATTERN)))
	parser.add_argument(	'-c', '--copy',
							action='store_true',
							help='Whenever a password is succesfully generated (in either singlue-use mode or interactive mode), '
								+'the string will be copied to your clipboard (may require external libraries, depending on platform')
	parser.add_argument(	'-i', '--interactive',
							action='store_true',
							help='Launches in interactive mode, where passwords of the given pattern are continuously printed after each input, '
								+'and if a valid pattern is given as input at any time, then the new pattern will be used going forward (enter `q` to exit)')
	worddict_group = parser.add_mutually_exclusive_group()
	worddict_group.add_argument(	'-w', '--worddict',
							type=str,
							help='Sets the `words.txt` file that is used as the dictionary for the generator when generating whole words. '
								+'The parser goes line by line, using non-word characters to separate each word (this excludes hyphens and apostrophes, '
								+'which are removed prior to parsing and the two sides of the word are merged) and a new, formatted `words.txt` '
								+'file will be created (the previous version will be copied to words.txt.old)')
	worddict_group.add_argument(	'-l', '--language',
							type=str,
							help='Attempts to use a pre-made words file (made from the dictionary of the specified language) and replaces the current '
								+'words.txt file using that language\'s words file, if it exists (if there is no default file for your language, please '
								+'consider making your own file for your language and forking this project to include your language\'s dictionary; '
								+'go to `https://github.com/nkrim/passwordgen` for more info)')
	parser.add_argument(	'-R', '--revert',
							action='store_true',
							help='Reverts the worddict file at `words.txt` with the backup file, if there is one '
							+'(this is performed before a new `words.txt` file is generated if the `-w` or `-l` command is also used)')
	return parser	

def howto():
	return 'Go to `https://github.com/nkrim/passwordgen` to see the README for the how-to documentation on writing your own passwordgen patterns\n'

if __name__ == '__main__':
	main()