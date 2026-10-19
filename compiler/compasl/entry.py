# entry.py

# Advanced Sol Language
# This compile makes your life more easy
# For more see examples or sintaxe.txt

# Resolve sequence:
# (Macros and expressions) -> Labels

from typing import TextIO

# Compiler components
from compiler.compasl.macro import resolve_macro
from compiler.compasl.expr import resolve_expr

def _compasl(target_path, f_target: TextIO, f_output: TextIO):
    f_output.flush()
    f_output.seek(0)
    f_output.truncate() # Clear output
    f_output.flush()
    f_output.writelines(f_target.readlines())
    f_output.flush()
    f_output.seek(0)
    dic_ptr = [{}]
    def_ptr = [{}]

    while True:
        macro_processed = resolve_macro(target_path, f_output, dic_ptr, def_ptr)
        f_output.flush()
        f_output.seek(0)
        expr_processed = resolve_expr(f_output)
        f_output.flush()
        f_output.seek(0)

        if macro_processed or expr_processed:
            continue
        break

    f_output.flush()
    f_output.seek(0)