# entry.py

# Advanced Sol Language
# This compile makes your life more easy
# For more see examples or sintaxe.txt

# Resolve sequence:
# Macros -> Labels -> Expressions

from typing import TextIO
from compiler.compasl.macro import resolve_macro

def _compasl(target_path, f_target: TextIO, f_output: TextIO):
    # This is just a repass
    resolve_macro(target_path, f_target, f_output)
    # label.py and expr.py not implemented now...