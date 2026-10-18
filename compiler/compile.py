import os
from compiler.compsol import _compsol
from compiler.compasl.entry import _compasl

debug = True
# FUNCAO DE DEBUG
def listprint(string, list: list[list]):
    list[0].append(string)

def dbgprint(string, list: list[list]):
    global debug
    if debug:
        listprint('DEBUG: ' + string, list)

# HELPERS
def multifind(string: str, *args): # Return a list with args occurence in string
    out = []

    for a in args:
        if a in string:
            out.append([string.find(a), a])

    return out

# LOGIC
def comp(path, file, output, buffer: list[list]):
    if not os.path.exists(path):
        os.mkdir(path)
        listprint(f'build dir not found, created in {path}', buffer)

    if path and file and output:
        dbgprint(f'passed args: {path}, {file}, {output}', buffer)
    else:
        listprint('use help for more info', buffer)
        return

    # o check de argv == 1 é pra caso o cara não passe o output name
    if 'help' in file or multifind(file, '.sol', '.asl') == []:
        listprint('use of this compiler:', buffer)
        listprint('comp file_target.format output_name', buffer)
        return

    target_file = f'./{file}'
    output_name = f'./build/{output}.hex'

    if not os.path.exists(target_file):
        listprint(f'error, file {target_file} not exists', buffer)
        return

    if '.asl' in target_file:
        listprint(f'compiling a .asl file to .sol file...', buffer)
        output_name = f'./build/{output}.sol'

        with open(target_file, 'r', encoding='utf-8') as f_target, \
            open(output_name, 'r+', encoding='utf-8') as f_output:
            _compasl(target_file, f_target, f_output)

    if '.sol' in target_file:
        listprint(f'compiling {target_file} to {output_name}', buffer)

        with open(target_file, 'r', encoding='utf-8') as f_target, \
            open(output_name, 'w', encoding='utf-8') as f_output:
            _compsol(f_target, f_output)
