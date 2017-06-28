passwordgen
###########
A generator for safe and random passwords defined by a user-defined pattern. The pattern allows for sequences of random digits, symbols, and characters, as well as whole words, with a multitude of options to customize the generated password.

Installation
============
.. code-block:: console

  $ pip install passwordgen

Options
=======
-h, --help  Display help menu
-c, --copy  Whenever a password is succesfully generated (in either singlue-use mode or interactive mode), the string will be copied to your clipboard (may require external libraries, depending on platform) 
-i, --interactive  Launches in interactive mode, where passwords of the given pattern are continuously printed after each input, and if a valid pattern is given as input at any time, then the new pattern will be used going forward (enter ``q`` to exit)
-w file, --worddict=file  Sets the ``words.txt`` file that is used as the dictionary for the generator when generating whole words. The parser goes line by line, using non-word characters to separate each word (this excludes hyphens and apostrophes, which are removed prior to parsing and the two sides of the word are merged) and a new, formatted ``words.txt`` file will be created (the previous version will be copied to ``words.txt.old``)
-l file, --language=file  Attempts to use a pre-made words file (made from the dictionary of the specified language) and replaces the current words.txt file using that language's words file, if it exists (if there is no default file for your language, please consider making your own file for your language and forking this project to include your language's dictionary; go to `https://github.com/nkrim/passwordgen` for more info)
-R, --revert  Reverts the worddict file at ``words.txt`` with the backup file at ``words.txt.old``, if there is one. This is performed before a new ``words.txt`` file is generated if the ``-w`` command is used with this

How to Use
==========
Pattern Basics
--------------
A full pattern is comprised of one or more signifier expressions.  A signifier expression is composed of three parts, one or more **signifiers**, zero or more **flags**, and zero or one **length specifier**.  All signifier expressions follows this basic pattern ``%'sig''flags'['length']`` (more complex examples will be shown after the following definitions).  All signifiers and flags are singular characters, while the length specifier can be defined as ``[n]`` where ``n > 0`` or ``[n-N]`` where ``n >= 0`` and ``N > 0`` and ``N >= n``.

Signifiers
----------
Signifiers can appear alone, to represent one character (or one word) from it's respective pool of possibilities. Every signifier expression must contain at least one signifier, preceeded by a ``%`` character.

Multiple Signifiers
-------------------
If multiple signifiers are used for the same expression, they must be wrapped by curly-brackets along with their flags (but not their length specifier), for example: ``%{'sig1''sig2''sigN''flags'}['length']``. When multiple signifiers are used, each character in the expression's sequence is picked randomly from the pool of all available characters defined by the union of the sets of characters each signifier represents (therefore a ``c`` signifier used in a multiple signifier expression is redundant, as ``c`` is defined as including all charaters from the other signifier pools, unless used with the ``~`` flag to include the chance of using the pool of all characters).  

**Note:** The ``W`` signifier **cannot** be included in an expression with multiple signifiers unless the ``~`` flag is present (raises an error).

+-----------+---------------------------------------------------------------------------------------+
| Character | Definition                                                                            |
+===========+=======================================================================================+
| ``d``     | Random digit(s)                                                                       |
+-----------+---------------------------------------------------------------------------------------+
| ``s``     | Random symbol(s)                                                                      |
+-----------+---------------------------------------------------------------------------------------+
| ``w``     | Random word character (``[a-z]``)                                                     |
+-----------+---------------------------------------------------------------------------------------+                            
| ``W``     | Random word (from dictionary, defaults to lowercase)                                  |
+-----------+---------------------------------------------------------------------------------------+                  
| ``c``     | Random character (excluding whitespace; word characters are of random capitalization) |
+-----------+---------------------------------------------------------------------------------------+

Flags
-----
Flags are ways to manipulate the default action of each signifier. Certain flags can only interact with certain signifiers. If a flag is present but no signifiers that it can interact with are present, then it produces no effect.

+-----------------+---------------------+----------------------------------------------------------------------------------------------------+
| Character       | Relevant Signifiers | Definition                                                                                         |
+=================+=====================+====================================================================================================+
| ``~``           | *any*               | When used in an expresion with multiple signifiers, one signifier from the given set is randomly   |
|                 |                     | chosen (without bias) to represent the sole signifier of the entire expression                     |
+-----------------+---------------------+----------------------------------------------------------------------------------------------------+
| ``=``           | ``d``, ``s``,       | Expression will produce a sequence of a single random character repeated a number of times         |
|                 | ``w``, ``c``        | (defined by it's length specifier) from it's pool of characters (defined by it's signifiers)       |
+-----------------+---------------------+----------------------------------------------------------------------------------------------------+
| ``+``           | ``w``, ``W``        | Word characters will be upper-case instead of their default of lowercase                           |
+-----------------+---------------------+----------------------------------------------------------------------------------------------------+
| ``^``           | ``w``, ``W``        | One word character of the sequence will be uppercase (equivalent to ``+`` if ``=`` flag is present)|
+-----------------+---------------------+----------------------------------------------------------------------------------------------------+
| ``+`` and ``^`` | ``w``, ``W``        | Word character capitalization is randomized (this does not double the chance of getting a          |
|                 |                     | character when using the ``c`` signifier or a multiple signifier expression; when the ``=`` flag   |
|                 |                     | is present there is a 50/50 chance between the whole sequence being lowercase or uppercase)        |
+-----------------+---------------------+----------------------------------------------------------------------------------------------------+

Length Specifier
----------------
The length specifier represents the length of the character sequence the signifier expression will produce. A length specifier can represent an explicit number, an inclusive range of numbers, or it can be absent. The length specifier, if present, is always surrounded by square brackets. The explicit specifier must satisfy ``n > 0`` where ``n`` is the explicit length given, and the range specifier must satisfy ``n >= 0`` and ``N > 0`` and ``N >= n`` where ``n`` is the lower bound of the range and ``N`` is the upper bound of the range. If any of these conditions are not satisfied, an error is raised and the program is terminated.

Length Specifiers With the ``W`` Signifier
------------------------------------------
The generator *does not* pick the length randomly and then finds a random word of that length, but rather it groups up all words of acceptable length and picks randomly from that set, so whichever word-length is most frequent from that range, that would be the most probable result of the length of the word. Therefore, if part of the range exceeds the maximum word length, it is merely disregarded and the set to choose from is constructed from all available words with minimum length equal to the lower bound of the given range. If no words can be found satisfying the specified length (explicitly or via a range) a warning will be issued and the generator will choose a random word disregarding length.

+-----------+---------------------------------------------------------------------------------------------------------------------+
| Form      | Definition                                                                                                          |
+===========+=====================================================================================================================+
| ``[n]``   | The sequence will be explicitly of length ``n``                                                                     |
+-----------+---------------------------------------------------------------------------------------------------------------------+
| ``[n-N]`` | The length of the sequence will fall between the range of ``n`` and ``N``, inclusively                              |
+-----------+---------------------------------------------------------------------------------------------------------------------+
| (absent)  | The sequence will be either a single character, or, for the ``W`` signifier, will be a single word of random length |
+-----------+---------------------------------------------------------------------------------------------------------------------+

Signifier Expression Examples
=============================
* A single random digit
  
  .. code-block:: console

      $ passwordgen %d
      6

* A single random lowercase word

  .. code-block:: console
	
	  $ passwordgen %W
	  password

* A sequence of random lowercase word characters

  .. code-block:: console

	  $ passwordgen %w[4]
	  dvzv

* A random lowercase word of length 5

  .. code-block:: console
	
	  $ passwordgen %W[5]
	  cakes

* A sequence of random symbols with a length between 2 and 6

  .. code-block:: console
	
	  $ passwordgen %s[2-6]
	  @$$#

* A sequence of a singular random digit, repeated between 4 and 6 times

  .. code-block:: console

	  $ passwordgen %d=[4-6]
	  22222

* A random uppercase word

  .. code-block:: console

	  $ passwordgen %W+
	  GENERATOR

* A sequence of a singular random lowercase or uppercase character, repeated 3 times

  .. code-block:: console

	  $ passwordgen %w=^+[3]
	  fff

* A random word with a length between 2 and 4, with one uppercase letter (the `=` flag has no effect)

  .. code-block:: console

	  $ passwordgen %W=^[2-4]
	  gRip

* A random sequence of characters of length 8, with random capitalization

  .. code-block:: console
	
	  $ passwordgen %c+^[8]
	  0es#V4uB

* A random sequence of digits and symbols of length 4

  .. code-block:: console

	  $ passwordgen %{ds}[4]
	  1##8

* A random sequence of length 5 consisting entirely of either of word characters or digits

  .. code-block:: console

	  $ passwordgen %{wd~}[5]
	  82535

* A sequence of a singular random lowercase or uppercase word character or symbol, repeated 7 times

  .. code-block:: console

	  $ passwordgen %{ws=^+}[7]
	  GGGGGGG

* Same as above, except the chance between choosing a word character and a symbol is now equal because of the `~` flag, where previously the chance was weighted by the number of word characters vs the number of symbols

  .. code-block:: console

	  $ passwordgen %{ws=^+~}[7]
	  $$$$$$$

Contributing
============
Adding languages' dictionaries
------------------------------
If you could not find a particular language in the list of default language dictionaries (which can be used as presets word files for generating random words by using the ``-l`` flag with a valid language name) you can contribue to this project by adding your favorite languages! Please note though that, in it's current form, passwordgen only supports basic alpha-numeric characters, so whichever language you wish to add should be able to be properly represented by this alphabet. 

You can contribute your language's dictionary by following these steps:

1. Fork this project's github repository (https://github.com/nkrim/passwordgen)
2. Find or create a file (with any formatting) with all (or as many as makes practical sense) of words from the language you wish to add (ensure that all characters in the words are basic alphabetic characters with no accents, aka 'ç' should be changed to 'c' and 'é' to 'é', though hyphens and apostrophes are removed prior to parsing by the program so those can be left in)
3. Pre-format the file so it can be quickly loaded in at the user's request. If you have passwordgen installed you can do this by running ``python -c "from passwordgen.worddict import WordDictionary; print(WordDictionary.parse('<path_to_your_source_file>'))" > <path_to_your_output_file>`` with the appropriate subsititions, or if you do not have passwordgen installed, you can do the same command from the root directory of this project by replacing ``passwordgen`` with ``src``
4. Move the formatted dictionary file into the directory ``src/words/defaults`` within this project, and ensure that the file's name is the ``<language_name>.txt`` where ``<language_name>`` is *lowercase* and is the name of the language within its own language (i.e. "deutsch" instead of "german", or "francais" intead of "french")
5. Push your new language file(s) to your fork, and make a pull requst so that it can be reviewed and hopefully added to the project
6. Thank you for contributing n_n
