import random
import re
from itertools import repeat

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
					raise ValueError('Attempted to use the `W` signifier while no word dictionary is loaded, load a dictionary with the `-w` or `-l` command options')
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