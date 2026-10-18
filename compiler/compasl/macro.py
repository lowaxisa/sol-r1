# macro.py

# Idea:
# Scan a file and read macros

import copy
import os
from typing import TextIO

def search_macros(buffer):
    macros_dic: dict = {} # macro_name: [[line0], [line1], [...]]
    no_macro_buffer = [] # code buffer, but without macros define

    macro_context = stack() # MACRO context stack
    for line in buffer: # Load all macros
        elements: list = line.split()

        elements_no_comment: list = []
        for e in elements:
            if e == ';':    break
            if e.find(';') != -1: break
            elements_no_comment.append(e)
        elements = elements_no_comment

        len_arr = len(elements)
        if len_arr == 0: continue
        first_element = elements[0]

        if not macro_context.is_empty():
            curr_macro = macro_context.top()
            # PUSH line into macro source
            if len_arr == 1 and first_element == '#MACRO':
                macro_context.pop()
            else:
                macros_dic[curr_macro].append(elements)
            continue

        if first_element == '#MACRO': # #MACRO NAME
            macros_dic[elements[1]] = []
            macro_context.push(elements[1])
            continue
        no_macro_buffer.append(elements)
    return macros_dic, no_macro_buffer

def check_import(target_path, buffer, locks: list):
    curr_path: str = os.path.dirname(os.path.abspath(target_path))
    tempbuffer = buffer
    in_protected_file = False
    last_index = 0

    while True:
        find_import = False

        for i in range(last_index, len(tempbuffer)):            
            line = tempbuffer[i]
            elements: list = line.split()

            elements_no_comment: list = []
            for e in elements:
                if e == ';':    break
                if e.find(';') != -1: break
                elements_no_comment.append(e)
            elements = elements_no_comment

            len_arr = len(elements)

            if len_arr == 0:
                if in_protected_file:
                    tempbuffer = tempbuffer[:i] + tempbuffer[i + 1:]
                    last_index = i
                    find_import = True
                    break
                else:
                    continue
            
            first_element = elements[0]

            if first_element == '#LOCK':
                if len_arr == 2: # If is LOCK NAME
                    if not (elements[1] in locks):
                        locks.append(elements[1])
                    else:
                        in_protected_file = True
                else:
                    in_protected_file = False
                
                tempbuffer = tempbuffer[:i] + tempbuffer[i + 1:]
                last_index = i
                find_import = True
                break

            if in_protected_file:
                tempbuffer = tempbuffer[:i] + tempbuffer[i + 1:]
                last_index = i
                find_import = True
                break

            if first_element == '#IMPORT':
                import_path = os.path.join(curr_path, elements[1])
                with open(import_path, 'r', encoding='utf-8') as f_import:
                    tempbuffer = tempbuffer[:i] + check_import(import_path, f_import.readlines(), locks) + tempbuffer[i + 1:]
                find_import = True
                break # Its dangeours use array after changes

        if not find_import:
            return tempbuffer

def resolve_macro(target_path, f_target: TextIO, f_output: TextIO):
    output_buffer = ''
    nomacrodef_buffer: list = []
    buffer = f_target.readlines() # File buffer
    buffer = check_import(target_path, copy.deepcopy(buffer), [])
    macros_dic, nomacrodef_buffer = search_macros(buffer) # macros_dic: {macro_name: [[line0], [line1], [...]]}

    while True: # Expand all macros
        expand_target = None
        encountred_macro =  None
        macro_args = {}

        for i in range(len(nomacrodef_buffer)):
            line = nomacrodef_buffer[i]

            if line[0] in macros_dic:
                expand_target = i
                encountred_macro = line[0]

                argc = 1
                for arg in line:
                    if arg == line[0]: continue
                    macro_args['#ARG' + str(argc)] = arg
                    argc += 1

                break

        if expand_target != None:
            nomacrodef_buffer_part1 = nomacrodef_buffer[:expand_target]
            nomacrodef_buffer_part2 = nomacrodef_buffer[expand_target + 1:]

            macrosource: list[list[str]] = copy.deepcopy(macros_dic[encountred_macro])
            for i in range(len(macrosource)):
                arr = macrosource[i]
                for k in range(len(arr)):
                    line = arr[k]

                    if line in macro_args:
                        macrosource[i][k] = macro_args[line]

            nomacrodef_buffer = nomacrodef_buffer_part1 + macrosource + nomacrodef_buffer_part2
        else:
            break

    for elements_arr in nomacrodef_buffer:
        line = ' '.join(elements_arr)
        output_buffer += line + '\n'

    f_output.write(output_buffer)

class stack:
    def __init__(self):
        self.src: list = []

    def is_empty(self):
        return not len(self.src)

    def top(self):
        return self.src[-1]

    def push(self, element):
        self.src.append(element)

    def pop(self):
        return self.src.pop()