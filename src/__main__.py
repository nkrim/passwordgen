import argparse
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
# Relavent Paths
# ==============
WORDS_FILE = path.join(path.dirname(path.abspath(__file__)), 'words', 'words.txt')

def main():
	args = parser().parse_args()

	# Word Dictionary ops
	if args.revert:
		WordDictionary.revert(WORDS_FILE)
	worddict = None
	if args.worddict:
		print('Generating new words file from file: %r' % args.worddict)
		worddict = WordDictionary.setWordsFile(WORDS_FILE, args.worddict)
	if not worddict:
		try: 
			worddict = WordDictionary(WORDS_FILE)
		except FileNotFoundError:
			worddict = None
			printerr('Could not find words file at %r, can continue as long as pattern does not use the `W` signifier' % WORDS_FILE)

	# Parse pattern
	try:
		pattern = Pattern(args.pattern, worddict)
	except ValueError as e:
		printerr('Error when compiling pattern with `%s`: %s' % (args.pattern, e))
		sys.exit(1)

	# Generate password(s)
	if args.interactive:
		print('Entering interactive mode. Enter anything to generate new password. Enter a new pattern at any time to use instead, if valid.')
		print('  Enter `q` to quit')
		print('  Generating using pattern: `%s`' % pattern)
		quit = False
		while not quit:
			try:
				out = pattern.generate()
			except ValueError as e:
				printerr('Error when generating password: %s' % e)
				sys.exit(1)
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
	sys.exit(0)
		

def parser():
	parser = argparse.ArgumentParser(	description='Generate random passwords using a pattern ot specify the general format.',
										epilog=howto(),
										formatter_class=argparse.RawDescriptionHelpFormatter)
	parser.add_argument(	'pattern',
							nargs='?',
							default=DEFAULT_PATTERN,
							help='The pattern to use to generate the password (defaults to `%(default)s`)')
	parser.add_argument(	'-c', '--copy',
							action='store_true',
							help='Whenever a password is succesfully generated (in either singlue-use mode or interactive mode), '
								+'the string will be copied to your clipboard (may require external libraries, depending on platform')
	parser.add_argument(	'-i', '--interactive',
							action='store_true',
							help='Launches in interactive mode, where passwords of the given pattern are continuously printed after each input, '
								+'and if a valid pattern is given as input at any time, then the new pattern will be used going forward (enter `q` to exit)')
	parser.add_argument(	'-w', '--worddict',
							type=str,
							nargs='?',
							help='Sets the `words.txt` file that iss used as the dictionary for the generator when generating whole words. '
								+'The parser goes line by line, using non-word characters to separate each word (this excludes hyphens and apostrophes, '
								+'which are removed prior to parsing and the two sides of the word are merged) and a new, formatted `words.txt` '
								+'file will be created (the previous version will be copied to words.txt.old)')
	parser.add_argument(	'-R', '--revert',
							action='store_true',
							help='Reverts the worddict file at `words.txt` with the backup file, if there is one. '
							+'This is performed before a new `words.txt` file is generated if the `-w` command is used with this')
	return parser	

def howto():
	return 'Go to `https://github.com/nkrim/passwordgen` to see the README for the how-to documentation\n'

if __name__ == '__main__':
	main()