passwordgen
===========
l

Options
-------
| Flag                  | Argument | Definition |
| :-------------------: | -------- | ---------- |
| `-h`, `--help`        | none     | Display help menu |
| `-i`, `--interactive` | none     | Launches in interactive mode, where passwords of the given pattern are continuously printed after each input, and if a valid pattern is given as input at any time, then the new pattern will be used going forward (enter `q` to exit) |
| ~~`-l`, `--length`~~  | integer  | Sets total max length of the generated password. When this is set, if the pattern will never produce a sequence greater than length there is no effect, if the pattern can produce a sequence greater than length, but can also produce a sequence less than or equal to length then the pattern is fully satisfied within exactly the length (if possible), otherwise if the pattern will always exceed the length, the pattern is processed left-to-right while minimizing all ranges and when the end would be exceeded by the next expression the remaining space is filled with this expression (if this last expression uses the `W` signifier, then a random word is chosen to exactly fill the rest of the space). |
| `-w`, `--worddict`    | file     | Sets the `words.txt` file that iss used as the dictionary for the generator when generating whole words. The parser goes line by line, using non-word characters to separate each word (this excludes hyphens and apostrophes, which are removed prior to parsing and the two sides of the word are merged) and a new, formatted `words.txt` file will be created (the previous version will be copied to words.txt.old) | 

How to Use
----------
#### Pattern Basics
A full pattern is comprised of one or more signifier expressions, ~~interspersed with zero or more literal characters around them, if defined~~.  A signifier expression is composed of three parts, one or more **signifiers**, zero or more **flags**, and zero or one **length specifier**.  All signifier expressions follows this basic pattern `%'sig''flags'['length']` (more complex examples will be shown after the following definitions).  All signifiers and flags are singular characters, while the length specifier can be defined as `[n]` where `n > 0` or `[n-N]` where `n >= 0` and `N > 0` and `N >= n`.
#### Signifiers
Signifiers can appear alone, to represent one character (or one word) from it's respective pool of possibilities. Every signifier expression must contain at least one signifier, preceeded by a `%` character.  
**Multiple signifiers**  
If multiple signifiers are used for the same expression, they must be wrapped by curly-brackets along with their flags (but not their length specifier), for example: `%{'sig1''sig2''sigN''flags'}['length']`. When multiple signifiers are used, each character in the expression's sequence is picked randomly from the pool of all available characters defined by the union of the sets of characters each signifier represents (therefore a `c` signifier used in a multiple signifier expression is redundant, as `c` is defined as including all charaters from the other signifier pools, unless used with the `~` flag to include the chance of using the pool of all characters).  
**Note:** The `W` signifier **cannot** be included in an expression with multiple signifiers unless the `~` flag is present (raises an error).

| Character | Definition                                                                            |
| :-------: | ------------------------------------------------------------------------------------- |
| `d`       | Random digit(s)                                                                       |
| `s`       | Random symbol(s)                                                                      |
| `w`       | Random word character (`[a-z]`)                                                       |
| `W`       | Random word (from dictionary, defaults to lowercase)                                  |
| `c`       | Random character (excluding whitespace; word characters are of random capitalization) |
#### Flags
Flags are ways to manipulate the default action of each signifier. Certain flags can only interact with certain signifiers. If a flag is present but no signifiers that it can interact with are present, then it produces no effect.

| Character   | Relevant Signifiers | Definition |
| :---------: | :-----------------: | ---------- |
| `~`         | (any)               | When used in an expresion with multiple signifiers, one signifier from the given set is randomly chosen (without bias) to represent the sole signifier of the entire expression |
| `=`         | `d`, `s`, `w`, `c`  | Expression will produce a sequence of a single random character repeated a number of times (defined by it's length specifier) from it's pool of characters (defined by it's signifiers) |
| `+`         | `w`, `W`            | Word characters will be upper-case instead of their default of lowercase |
| `^`         | `w`, `W`            | One word character of the sequence will be uppercase (equivalent to `+` when the `=` flag is present) |
| `+` and `^` | `w`, `W`            | Word character capitalization is randomized (this does not double the chance of getting a character when using the `c` signifier or a multiple signifier expression; when the `=` flag is present there is a 50/50 chance between the whole sequence being lowercase or uppercase) |
#### Length Specifier
The length specifier represents the length of the character sequence the signifier expression will produce. A length specifier can represent an explicit number, an inclusive range of numbers, or it can be absent. The length specifier, if present, is always surrounded by square brackets. The explicit specifier must satisfy `n > 0` where `n` is the explicit length given, and the range specifier must satisfy `n >= 0` and `N > 0` and `N >= n` where `n` is the lower bound of the range and `N` is the upper bound of the range. If any of these conditions are not satisfied, an error is raised and the program is terminated.  
**With the `W` signifier**  
The generator _does not_ pick the length randomly and then finds a random word of that length, but rather it groups up all words of acceptable length and picks randomly from that set, so whichever word-length is most frequent from that range, that would be the most probable result of the length of the word. Therefore, if part of the range exceeds the maximum word length, it is merely disregarded and the set to choose from is constructed from all available words with minimum length equal to the lower bound of the given range. If no words can be found satisfying the specified length (explicitly or via a range) a warning will be issued and the generator will choose a random word disregarding length.

| Form     | Definition |
| :------: | ---------- |
| `[n]`    | The sequence will be explicitly of length `n` |
| `[n-N]`  | The length of the sequence will fall between the range of `n` and `N`, inclusively |
| (absent) | The sequence will be either a single character, or, for the `W` signifier, will be a single word of random length |
### Signifier Expression Examples
| Expression      | Example Result | Definition |
| --------------- | -------------- | ---------- |
| `%d`            | `6`            | A singule random digit |
| `%W`            | `password`     | A single random lowercase word |
| `%w[4]`         | `dvzv`         | A sequence of random lowercase word characters |
| `%W[5]`         | `cakes`        | A random lowercase word of length 5 |
| `%s[2-6]`       | `@$$#`         | A sequence of random symbols with a length between 2 and 6 |
| `%d=[4-6]`      | `22222`        | A sequence of a singular random digit, repeated between 4 and 6 times |
| `%W+`           | `GENERATOR`    | A random uppercase word |
| `%w=^+[3]`      | `fff`          | A sequence of a singular random lowercase or uppercase character, repeated 3 times |
| `%W=^[2-4]`     | `gRip`         | A random word with a length between 2 and 4, with one uppercase letter (the `=` flag has no effect) |
| `%c+^[8]`       | `0es#V4uB`     | A random sequence of characters of length 8, with random capitalization |
| `%{ds}[4]`      | `1##8`         | A random sequence of digits and symbols of length 4 |
| `%{wd~}[5]`     | `82535`        | A random sequence of length 5 consisting either of word characters or digits |
| `%{ws=^+}[7]`   | `GGGGGGG`      | A sequence of a singular random lowercase or uppercase word character or symbol, repeated 7 times |
| `%{ws=^+~}[7]`  | `$$$$$$$`      | Same as above, except the chance between choosing a word character and a symbol is now equal because of the `~` flag, where previously the chance was weighted by the number of word characters vs the number of symbols |

