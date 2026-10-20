# Idea: a recursive function with a sliding window
# Receive a (line, start_idx, idx) and return success, result, start_index, end_index

from typing import TextIO

def expr_handler(args: list[str]): # return success, result
    success = False
    result = ''
    cmd = args[0]

    if cmd in ('CONCAT', 'AT', 'FILTER', 'ESPACE', 'ENDLINE', 'UPPER', 'LOWER', 'JOIN', 'IFEQ', 'NONE'):
        if cmd == 'CONCAT':
            result = args[1] + args[2] # CONCAT STR_A STR_B ex: CONCAT A B out: AB
        if cmd == 'AT':
            result = args[1][int(args[2])] # AT STRING INDEX ex: AT Hello 1 out: e
        if cmd == 'FILTER':
            result = args[1] if args[1] in args[2:len(args) - 1] else args[-1] # FILTER STR LIST DEFAULT ex: FILTER 2 1 2 3 4 0 out: 2, if str is for example 6 out is 0 
        if cmd == 'ESPACE':
            result = ' '
        if cmd == 'ENDLINE':
            result = '\n'
        if cmd == 'UPPER':
            result = args[1].upper()
        if cmd == 'LOWER':
            result = args[1].lower()
        if cmd == 'JOIN': # JOIN STR SEPARATOR
            result = args[-1].join(args[1:-1])
        if cmd == 'IFEQ': # IFEQ A B IFTRUE IFFALSE example: IFEQ A A Y N -> Y, another ex: IFEQ A B Y N -> N
            result = args[3] if args[1] == args[2] else args[4]
        if cmd == 'NONE': # MAKE NOTHING
            pass
        success = True

    return success, result

def expr_find(line, first_find_idx, idx):
    cmd_list = []
    find = False
    buffer = ''
    start_index = 0
    end_index = 0

    while True:
        resolved = True

        for i in range(idx, len(line)):
            c = line[i]

            if c == '(' and not find:
                find = True
                start_index = i
                continue
            elif c == '(' and find:
                discard1, result, discard2, end_index = expr_find(line, start_index, i)
                cmd_list.append(result)
                idx = end_index + 1 # Starts after )
                resolved = False
                break
            elif c == ')' and find:
                end_index = i
                if buffer != '':
                    cmd_list.append(buffer)
                break

            if not find: continue

            if c != ' ':
                buffer += c
            elif buffer != '':
                cmd_list.append(buffer)
                buffer = ''

        if resolved:
            success = False
            result = ''
            if len(cmd_list) >= 1:
                success, result = expr_handler(cmd_list)
            return success, result, start_index, end_index

def resolve_expr(f_target: TextIO):
    something_processed = False
    output_buffer = ''
    buffer = f_target.readlines() # File buffer

    for i in range(len(buffer)):
        line = buffer[i]
        end_index = 0

        while True:
            success, result, start_index, end_index = expr_find(line, 0, end_index)

            if success:
                buffer[i] = buffer[i][:start_index] + result + buffer[i][end_index + 1:]
                end_index = start_index + len(result) # Return in next cycle in next expr
                something_processed = True
                line = buffer[i]
            else:
                break

    for line in buffer:
        output_buffer += line

    f_target.seek(0)
    f_target.truncate()
    f_target.flush()
    f_target.write(output_buffer)
    return something_processed