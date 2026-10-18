# entry.py

# Advanced Sol Language
# This compile makes your life more easy
# For more see examples or sintaxe.txt

# Resolve sequence:
# Macros -> Labels -> Expressions

from typing import TextIO

# Compiler components
from compiler.compasl.macro import resolve_macro
from compiler.compasl.expr import resolve_expr

def _compasl(target_path, f_target: TextIO, f_output: TextIO):
    f_output.truncate() # Clear output
    f_output.flush()

    # This is just a repass
    resolve_macro(target_path, f_target, f_output)
    # label.py not implemented now...
    f_output.flush()
    f_output.seek(0)
    resolve_expr(f_output)