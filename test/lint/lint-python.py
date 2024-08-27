#!/usr/bin/env python3
#
# Copyright (c) 2022 The Bitcoin Core developers
# Distributed under the MIT software license, see the accompanying
# file COPYING or http://www.opensource.org/licenses/mit-license.php.

"""
Check for specified flake8 and mypy warnings in python files.
"""

import os
from pathlib import Path
import subprocess
import sys

from importlib.metadata import metadata, PackageNotFoundError

# Customize mypy cache dir via environment variable
cache_dir = Path(__file__).parent.parent / ".mypy_cache"
os.environ["MYPY_CACHE_DIR"] = str(cache_dir)

DEPS = ['flake8', 'lief', 'mypy', 'pyzmq']

# All .py files, except those in src/ (to exclude subtrees there)
FLAKE_FILES_ARGS = ['git', 'ls-files', '*.py', ':!:src/*.py']

# Only .py files in test/functional and contrib/devtools have type annotations
# enforced.
MYPY_FILES_ARGS = ['git', 'ls-files', 'test/functional/*.py', 'contrib/devtools/*.py']

ENABLED = (
    'E101,'  # indentation contains mixed spaces and tabs
    'E401,'  # multiple imports on one line
    'E402,'  # module level import not at top of file
    'E701,'  # multiple statements on one line (colon)
    'E702,'  # multiple statements on one line (semicolon)
    'E703,'  # statement ends with a semicolon
    'E711,'  # comparison to None should be 'if cond is None:'
    'E714,'  # test for object identity should be "is not"
    'E721,'  # do not compare types, use "isinstance()"
    'E722,'  # do not use bare 'except'
    'E742,'  # do not define classes named "l", "O", or "I"
    'E743,'  # do not define functions named "l", "O", or "I"
    'F401,'  # module imported but unused
    'F402,'  # import module from line N shadowed by loop variable
    'F403,'  # 'from foo_module import *' used; unable to detect undefined names
    'F404,'  # future import(s) name after other statements
    'F405,'  # foo_function may be undefined, or defined from star imports: bar_module
    'F406,'  # "from module import *" only allowed at module level
    'F407,'  # an undefined __future__ feature name was imported
    'F601,'  # dictionary key name repeated with different values
    'F602,'  # dictionary key variable name repeated with different values
    'F621,'  # too many expressions in an assignment with star-unpacking
    'F631,'  # assertion test is a tuple, which are always True
    'F632,'  # use ==/!= to compare str, bytes, and int literals
    'F811,'  # redefinition of unused name from line N
    'F821,'  # undefined name 'Foo'
    'F822,'  # undefined name name in __all__
    'F823,'  # local variable name … referenced before assignment
    'F841,'  # local variable 'foo' is assigned to but never used
    'W191,'  # indentation contains tabs
    'W291,'  # trailing whitespace
    'W292,'  # no newline at end of file
    'W293,'  # blank line contains whitespace
    'W605,'  # invalid escape sequence "x"
)


def check_dependencies():
    for dep in DEPS:
        try:
            metadata(dep)
        except PackageNotFoundError:
            print(f"Skipping Python linting since {dep} is not installed.")
            exit(0)


def main():
    check_dependencies()

    if len(sys.argv) > 1:
        flake8_files = sys.argv[1:]
    else:
        flake8_files = subprocess.check_output(FLAKE_FILES_ARGS).decode("utf-8").splitlines()

    flake8_args = ['flake8', '--ignore=B,C,E,F,I,N,W', f'--select={ENABLED}'] + flake8_files
    flake8_env = os.environ.copy()
    flake8_env["PYTHONWARNINGS"] = "ignore"

    try:
        subprocess.check_call(flake8_args, env=flake8_env)
    except subprocess.CalledProcessError:
        exit(1)

    mypy_files = subprocess.check_output(MYPY_FILES_ARGS).decode("utf-8").splitlines()
    mypy_args = ['mypy', '--show-error-codes'] + mypy_files

    try:
        subprocess.check_call(mypy_args)
    except subprocess.CalledProcessError:
        exit(1)


if __name__ == "__main__":
    main()
