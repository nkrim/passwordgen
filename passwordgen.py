#!/usr/bin/env python3

import argparse
import os
import random
import re
import sys
from itertools import repeat
from shutil import copyfileobj

# Argument Defaults
# =================
DEFAULT_PATTERN = '%d[4]%s=[2]%W[6-10]'
# Relavent Paths
# ==============
WORDS_FILE = 'words.txt'

def main():
	args = parser().parse_args()

	# Word Dictionary ops
	worddict = None
	if args.worddict:
		print('Generating new words file from file: %r' % args.worddict)
		worddict = WordDictionary.setWordsFile(args.worddict)
	if not worddict:
		try: 
			worddict = WordDictionary()
		except FileNotFoundError:
			worddict = None
			print('Could not find words file at %r, can continue as long as pattern does not use the `W` signifier' % WORDS_FILE, file=sys.stderr)

	# Parse pattern
	try:
		pattern = Pattern(args.pattern, worddict)
	except ValueError as e:
		print('Error when generating pattern: {}'.format(e), file=sys.stderr)
		return 1

	# Generate password(s)
	if args.interactive:
		print('Entering interactive mode. Enter `q` to quit. Enter anything to generate new password. Enter a new pattern at any time to use instead, if valid.')
		print('Generating using pattern: `%s`' % pattern)
		quit = False
		while not quit:
			out = pattern.generate()
			print(out)
			instr = input('>').strip()
			if instr:
				if instr == 'q':
					quit = True
				else:
					try:
						newpattern = Pattern(instr, worddict)
					except Exception as e:
						print('Failed to set new pattern: %s' % e)
					else:
						pattern = newpattern
						print('Generating using pattern: `%s`' % pattern)


	else:
		print('Generating using pattern: `%s`' % pattern)
		out = pattern.generate()
		print(out)

def parser():
	parser = argparse.ArgumentParser(	description='Generate random passwords using a pattern ot specify the general format.',
										epilog=howto(),
										formatter_class=argparse.RawDescriptionHelpFormatter)
	parser.add_argument(	'pattern',
							nargs='?',
							default=DEFAULT_PATTERN,
							help='The pattern to use to generate the password (defaults to `%(default)s`)')
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
	return parser	

class Pattern:
	all_sigs = {'d', 's', 'w', 'W', 'c'}
	all_flags = {'~', '=', '+', '^'}
	expression_re = re.compile((	r'%(?:'
										+r'(?P<sig>{0})(?P<flags>{1}*)'
										+r'|\{{(?P<sigm>{0}+)(?P<flagsm>{1}*)\}}'
									+r')'
									+r'(?:\['
										+r'(?P<length_lower>\d+)(?:-(?P<length_upper>\d+))?'
									+r'\])?'
								).format(	
									'[{}]'.format(''.join(all_sigs)),
									'[{}]'.format(''.join('\\'+f for f in all_flags))
								))
	pools_dict = {
		'd': {str(n) for n in range(0,10)},
		's': {'!', '@', '#', '$', '%', '^', '&', '*', '(', ')', '[', ']', '-', '+', '<', '>', '/', '?'},
		'w': {chr(ord('a')+i) for i in range(0,26)},
	}
	pools_dict['c'] = {c for _, pool in pools_dict.items() for c in pool}

	class Expression:
		def __init__(self, signifiers, flags='', length_lower=1, length_upper=None, word_any_length=False, worddict=None):
			# Fix defaults
			# ------------
			if length_upper == None:
				length_upper = lenth_lower

			# Check values
			# ------------
			if not signifiers:
				raise ValueError('Expression must include at least one signifier')
			if len(signifiers) > 1 and 'W' in signifiers and not (flags and '~' in flags):
				raise ValueError('Expression cannot contain multiple signifiers when the `W` signifier is included, unless the `~` flag is used')
			if not (length_lower >= 0 and length_upper > 0 and length_upper >= length_lower):
				raise ValueError('Length values must satisfy: `lower` >= 0 AND `upper` > 0 AND `upper` >= `lower`')

			# Set values
			# ----------
			self.signifiers = {sig for sig in signifiers if sig in Pattern.all_sigs}
			if len(self.signifiers) != len(signifiers):
				raise ValueError('An invalid or duplicate signifier was used. Only one of each of these signifiers are valid: {}'.format(', '.join(['`%s`'%s for s in Pattern.all_sigs])))
			self.flags = {f for f in flags if f in Pattern.all_flags}
			if len(self.flags) != len(flags):
				raise ValueError('An invalid or duplicate flag was used. Only one of each of these flags are valid: {}'.format(', '.join(['`%s`'%f for f in Pattern.all_flags])))
			self.length_lower = length_lower
			self.length_upper = length_upper
			self.word_any_length = word_any_length
			self.worddict = worddict

		def __str__(self):
			out = '%{}{}'.format(''.join(self.signifiers), ''.join(self.flags))
			if len(self.signifiers) > 1:
				out = '{'+out+'}'
			if self.length_lower != 1:
				out += '['+str(self.length_lower)
				if self.length_lower != self.length_upper:
					out += '-'+str(self.length_upper)
				out += ']'
			return out

		def generate(self):
			# Set flag mode variables
			CHOOSE_SIG = '~' in self.flags
			REPEAT_EQ = '=' in self.flags
			CAP_MODE = 0 + (1 if '^' in self.flags else 0) + (2 if '+' in self.flags else 0)
			# Apply the '~' (choose sig) flag
			if CHOOSE_SIG:
				sigs = {random.choice(tuple(self.signifiers))}
			else:
				sigs = self.signifiers
			# Decide whether to use WordGenerator
			if 'W' in sigs:
				if not self.worddict:
					raise ValueError('Attempted to use the `W` signifier while no word dictionary is loaded, load a dictionary with the `-w` or `--worddict` command options')
				if self.word_any_length:
					wordpool = self.worddict.getWordPool()
				else:
					wordpool = self.worddict.getWordPool(self.length_lower, self.length_upper)
				out = random.choice(tuple(wordpool))
			else:
				# Choose length
				length = random.randint(self.length_lower, self.length_upper)
				# Collect pools
				pool = {c for sig in sigs for c in Pattern.pools_dict[sig]}
				# Apply the '=' (repeat same) flag
				if REPEAT_EQ:
					c = random.choice(tuple(pool))
					if CAP_MODE == 1 or CAP_MODE == 2 or CAP_MODE == 3 and random.randrange(2):
						CAP_MODE = 2
					else:
						CAP_MODE = 0
					out = ''.join(repeat(c,length))
				# Generate sequence normally
				else:
					out = ''
					for _ in range(length):
						c = random.choice(tuple(pool))
						out += c
			# Apply the '+' and '^' (capitalization) flags
			if CAP_MODE == 3:
				def randcap(matchobj):
					c = matchobj.group()
					return c.upper() if random.randrange(2) else c
				out = re.sub(r'[a-z]', randcap, out)
			elif CAP_MODE == 2:
				out = out.upper()
			elif CAP_MODE == 1:
				start, c = random.choice([(m.start(), m.group()) for m in re.finditer(r'[a-z]', out)])
				out = out[0:start]+(c.upper())+out[start+1:]
			# Return generated sequence
			return out

	def __init__(self, pattern, worddict=None):
		def compile_expression(match, worddict=None):
			if match:
				gdict = match.groupdict()
				signifiers = gdict['sig'] or gdict['sigm'] or ''
				flags = gdict['flags'] or gdict['flagsm'] or ''
				length_lower = int(gdict['length_lower'] or 1)
				length_upper = int(gdict['length_upper'] or length_lower)
				word_any_length = not bool(gdict['length_lower'])
				try:
					return Pattern.Expression(signifiers, flags, length_lower, length_upper, word_any_length, worddict)
				except ValueError:
					raise ValueError('Failed to compile expression: `{}`'.format(match.group()))
			return None
		# Parse and compile expressions
		self.expressions = []
		pos = 0
		while pos < len(pattern):
			match = Pattern.expression_re.match(pattern, pos)
			exp = compile_expression(match, worddict)
			if not exp:
				raise ValueError('Pattern `{}` failed to compile at index: {}'.format(pattern, pos))
			self.expressions.append(exp)
			pos = match.end()
		# Set word dictionary
		self.worddict = worddict

	def __str__(self):
		return ''.join(str(exp) for exp in self.expressions)

	def generate(self):
		return ''.join(e.generate() for e in self.expressions)

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
			return '\n'.join(','.join(sorted(word_set)) for word_set in self._words[1:self.maxlength()+1])

		def add(self, word, length=-1):
			if length < 0:
				length = len(word)
			if length+1 > len(self._words):
				self._words += [set()] * (length+1-len(self._words))
			self._words[length].add(word)

		def maxlength(self):
			for i in reversed(range(len(self._words))):
				if len(self._words[i]) > 0:
					return i
			return 0


	def __init__(self, wordmap=None):
		if not wordmap:
			wordmap = WordDictionary.parse(WORDS_FILE, formatted=True)
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
						if w:
							wordmap.add(w, length)
					length += 1
		else:
			sub_re = re.compile(r'[\-\']')
			split_re = re.compile(r'\W+')
			with open(file_path, 'r') as f:
				for line in f:
					for w in split_re.split(sub_re.sub('', line)):
						if w:
							wordmap.add(w)
		return wordmap

	@staticmethod
	def backup():
		# Copy old `words.txt` to `words.txt.old`
		try:
			with open(WORDS_FILE, 'r') as f:
				with open(WORDS_FILE+'.old', 'w') as old:
					copyfileobj(f, old)
		except FileNotFoundError:
			print('No formatted words file could be found at %r, skipping backup' % WORDS_FILE, file=sys.stderr)
		except:
			print('Could not backup words file from %r to %r' % (WORDS_FILE, WORDS_FILE+'.old'), file=sys.stderr)

	@staticmethod
	def setWordsFile(file_path):
		# Read input file
		try:
			wordmap = WordDictionary.parse(file_path)
		except FileNotFoundError:
			print('Could not find file %r' % file_path, file=sys.stderr)
			return None
		# Backup words file
		WordDictionary.backup()
		# Write new words file
		try: 
			with open(WORDS_FILE, 'w') as f:
				f.write(str(wordmap))
		except Exception as e:
			print('Could not write new words file: %s' % e)
			return None
		# Return wordmap
		return WordDictionary(wordmap)

def howto():
	return '''
How to Use
----------
#### Pattern Basics
A full pattern is comprised of one or more signifier expressions, ~~interspersed with zero or more literal characters around them, if defined~~.  A signifier expression is composed of three parts, one or more **signifiers**, zero or more **flags**, and zero or one **length specifier**.  All signifier expressions follows this basic pattern `%'sig''flags'['length']` (more complex examples will be shown after the following definitions).  All signifiers and flags are singular characters, while the length specifier can be defined as `[n]` where `n > 0` or `[n-N]` where `n > 0` and `N >= n`.
#### Signifiers
Signifiers can appear alone, to represent one character (or one word) from it's respective pool of possibilities. Every signifier expression must contain at least one signifier, preceeded by a `%` character.  
**Multiple signifiers**  
If multiple signifiers are used for the same expression, they must be wrapped by curly-brackets along with their flags (but not their length specifier), for example: `%{'sig1''sig2''sigN''flags'}['length']`. When multiple signifiers are used, each character in the expression's sequence is picked randomly from the pool of all available characters defined by the union of the sets of characters each signifier represents (therefore a `c` signifier used in a multiple signifier expression is redundant, as `c` is defined as including all charaters from the other signifier pools, unless used with the `~` flag to include the chance of using the pool of all characters).  
**Note:** The `W` signifier **cannot** be included in an expression with multiple signifiers unless the `~` flag is present (raises an error).
| Character | Definition                                         |
| :-------: | -------------------------------------------------- |
| `d`       | Random digit(s)                                    |
| `s`       | Random symbol(s).                                  |
| `w`       | Random word character (`[a-z]`).                   |
| `W`       | Random word (from dictionary,                      |
|           | defaults to lowercase).                            |
| `c`       | Random character (excluding whitespace;            |
|           | word characters are of random capitalization).     |
#### Flags
Flags are ways to manipulate the default action of each signifier. Certain flags can only interact with certain signifiers. If a flag is present but no signifiers that it can interact with are present, then it produces no effect.
| Character   | Relevant Signifiers | Definition                                         |
| :---------: | :-----------------: | -------------------------------------------------- |
| `~`         | (any)               | When used in an expresion with multiple            |
|             |                     | signifiers, one signifier from the given set is    |
|             |                     | randomly chosen (without bias) to represent the    |
|             |                     | sole signifier of the entire expression.           |
| `=`         | `d`, `s`, `w`, `c`  | Expression will produce a sequence of a single     |
|             |                     | random character repeated a number of times        |
|             |                     | (defined by it's length specifier) from it's pool  |
|             |                     | of characters (defined by it's signifiers).        |
| `+`         | `w`, `W`            | Word characters will be upper-case instead of      |
|             |                     | their default of lowercase.                        |
| `^`         | `w`, `W`            | One word character of the sequence will be         |
|             |                     | uppercase (equivalent to `+` when the `=` flag is  |
|             |                     | present).                                          |
| `+` and `^` | `w`, `W`            | Word character capitalization is randomized (this  |
|             |                     | does not double the chance of getting a character  |
|             |                     | when using the `c` signifier or a multiple         |
|             |                     | signifier expression; when the `=` flag is present | 
|             |                     | there is a 50/50 chance between the whole sequence |
|             |                     | being lowercase or uppercase).                     |
#### Length Specifier
The length specifier represents the length of the character sequence the signifier expression will produce. A length specifier can represent an explicit number, an inclusive range of numbers, or it can be absent. The length specifier, if present, is always surrounded by square brackets. The explicit specifier must satisfy `n > 0` where `n` is the explicit length given, and the range specifier must satisfy `n > 0` and `N >= n` where `n` is the lower bound of the range and `N` is the upper bound of the range. If any of these conditions are not satisfied, an error is raised and the program is terminated.  
**With the `W` signifier**  
The generator _does not_ pick the length randomly and then finds a random word of that length, but rather it groups up all words of acceptable length and picks randomly from that set, so whichever word-length is most frequent from that range, that would be the most probable result of the length of the word. Therefore, if part of the range exceeds the maximum word length, it is merely disregarded and the set to choose from is constructed from all available words with minimum length equal to the lower bound of the given range. If no words can be found satisfying the specified length (explicitly or via a range) a warning will be issued and the generator will choose a random word disregarding length.
| Form     | Definition                                         |
| :------: | -------------------------------------------------- |
| `[n]`    | The sequence will be explicitly of length `n.      |
| `[n-N]`  | The length of the sequence will fall between the   |
|          | range of `n` and `N`, inclusively.                 |
| (absent) | The sequence will be either a single character,    |
|          | or, for the `W` signifier, will be a single word   |
|          | of random length.                                  |
#### Signifier Expression Examples
| Expression      | Example Result | Definition                                         |
| --------------- | -------------- | -------------------------------------------------- |
| `%d`            | `6`            | A singule random digit.                            |
| `%W`            | `password`     | A single random lowercase word.                    |
| `%w[4]`         | `dvzv`         | A sequence of random lowercase word characters.    |
| `%W[5]`         | `cakes`        | A random lowercase word of length 5.               |
| `%s[2-6]`       | `@$%#`         | A sequence of random symbols with a length between |
|                 |                | 2 and 6.                                           |
| `%d=[4-6]`      | `22222`        | A sequence of a singular random digit, repeated    |
|                 |                | between 4 and 6 times.                             |
| `%W+`           | `GENERATOR`    | A random uppercase word.                           |
| `%w=^+[3]`      | `fff`          | A sequence of a singular random lowercase or       |
|                 |                | uppercase character, repeated 3 times.             |
| `%W=^[2-4]`     | `gRip`         | A random word with a length between 2 and 4, with  |
|                 |                | one uppercase letter (the `=` flag has no effect). |
| `%c+^[8]`       | `0es#V4uB`     | A random sequence of characters of length 8, with  |
|                 |                | random capitalization.                             |
| `%{ds}[4]`      | `1##8`         | A random sequence of digits and symbols of         |
|                 |                | length 4.                                          |
| `%{wd~}[5]`     | `82535`        | A random sequence of length 5 consisting either of |
|                 |                | word characters or digits.                         |
| `%{ws=^+}[7]`   | `GGGGGGG`      | A sequence of a singular random lowercase or       |
|                 |                | uppercase word character or symbol, repeated 7     |
|                 |                | times.                                             |
| `%{ws=^+~}[7]`  | `$$$$$$$`      | Same as above, except the chance between choosing  |
|                 |                | a word character and a symbol is now equal because |
|                 |                | of the `~` flag, where previously the chance was   |
|                 |                | weighted by the number of word characters vs the   |
|                 |                | number of symbols.                                 |
	'''

def makeWlf(w_min, w_max):
	words = open(WORDS_PATH, 'r')
	wlf_path = WORDFILES_DIR+'-'.join(('words', str(w_min), str(w_max)))+'.txt'
	wlf = open(wlf_path, 'w')
	wlf.write('                    \n')
	wlf_buf = []
	wlf_buf_max_len = 100
	count = 0
	for w in words:
		if len(w)>=w_min and len(w)<=w_max:
			wlf_buf.append(w)
			count += 1
			if len(wlf_buf) >= wlf_buf_max_len:
				wlf.writelines(wlf_buf)
				wlf_buf = []
	wlf.writelines(wlf_buf)
	wlf.flush()
	wlf.seek(0)
	wlf.write(str(count))
	wlf.flush()
	wlf.close()
	return wlf_path

if __name__ == '__main__':
	main()
