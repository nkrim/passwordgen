import setuptools
from distutils.core import setup
from os import path

# Helper functions
# ----------------
def readFile(file):
	with open(file) as f:
		return f.read()

# Arguments
# ------------
CLASSIFIERS = []

# Dynamic info
# ------------
VERSION 			= '0.2'
CLASSIFIERS 		+= [
						'Development Status :: 3 - Alpha',
					]

# Package/Dependency info
# ---------------
PACKAGES			= [	'passwordgen'	]
PACKAGE_DIR 		= {	'passwordgen': 'src'	}
PACKAGE_DATA 		= {	'passwordgen': ['words/words.txt', 'words/defaults/*.txt']	}
DATA_FILES			= [ ('', ['README.rst','LICENSE']), ]
INSTALL_REQUIRES 	= [	'pyperclip>=1.5.27' ]

# Static info
# -----------
NAME 				= 'passwordgen'
DESCRIPTION 		= 'A generator for safe and random passwords defined by a user-defined pattern'
LONG_DESCRIPTION 	= readFile(path.join(path.dirname(path.abspath(__file__)), 'README.rst'))
AUTHOR 				= 'Noah Krim'
AUTHOR_EMAIL 		= 'nkrim62@gmail.com'
LICENSE 			= 'MIT License'
URL 				= 'https://github.com/nkrim/passwordgen'
KEYWORDS 			= 'passwordgen password generator safe random pattern'
ENTRY_POINTS		= { 'console_scripts': [ 'passwordgen = passwordgen.__main__:main' ] }
CLASSIFIERS 		+= [
						'Environment :: Console',
						'Intended Audience :: End Users/Desktop',
						'License :: OSI Approved :: MIT License',
						'Natural Language :: English',
						'Operating System :: OS Independent',
						'Programming Language :: Python',
						'Programming Language :: Python :: 2',
						'Programming Language :: Python :: 3',
						'Topic :: Security',
						'Topic :: Utilities',
					]
INC_PKG_DATA		= True
ZIP_SAFE			= False

# Setup call
# ----------
setup(
	name=NAME,
	version=VERSION,
	description=DESCRIPTION,
	long_description=LONG_DESCRIPTION,
	author=AUTHOR,
	author_email=AUTHOR_EMAIL,
	license=LICENSE,
	url=URL,
	keywords=KEYWORDS,
	entry_points=ENTRY_POINTS,
	packages=PACKAGES,
	package_dir=PACKAGE_DIR,
	package_data=PACKAGE_DATA,
	data_files=DATA_FILES,
	install_requires=INSTALL_REQUIRES,
	classifiers=CLASSIFIERS,
	include_package_data=INC_PKG_DATA,
	zip_safe=ZIP_SAFE )