# This comment is in PT-BR
# Ideia do resolvedor de labels:
# Usar readlines que ja me retorna a array de cada linha
# Buscar pela definição ALGO: em inicio de linhas (split e depois ver se [-1] == ':')
# Adicionar ao dicionario LABELADDRLOW lABELADDRHIGH LABELPAGELOW LABELPAGEHIGH
# Passar mais um loop que faz replace

from typing import TextIO

def resolve_label(f_target: TextIO):
    lines = f_target.readlines()
    f_target.seek(0)
    f_target.truncate()
    f_target.flush()

    while True:
        processed_anything = False

        for i in range(len(lines)): # Sugar for LABEL: ...
            line = lines[i].split()
            first_element = line[0]

            if first_element[-1] == ':' and len(line) > 1:
                lines[i] = first_element
                lines.insert(i + 1, ' '.join(line[1:]))
                processed_anything = True
                break

        if not processed_anything: break

    labels_dic = {} # FORMAT LABELNAME + ADDR/PAGE + LOW/HIGH
    new_lines: list[str] = []

    labels_count = 0
    labels_in_sequence = False
    label_resolved_last_idx = None
    label_resolved_last_count = None
    for i in range(len(lines)): # Detect labels
        line = lines[i]
        first_element = line.split()[0]

        if first_element[-1] == ':':
            label_name = first_element[:len(first_element) - 1]

            if label_resolved_last_idx != None and label_resolved_last_idx + 1 == i:
                labels_in_sequence = True
            else:
                labels_in_sequence = False

            addr, page = int_to_addr_page((i - labels_count) if not labels_in_sequence else label_resolved_last_count)

            labels_dic[label_name + 'ADDR' + 'LOW'] = addr[1]
            labels_dic[label_name + 'ADDR' + 'HIGH'] = addr[0]
            labels_dic[label_name + 'PAGE' + 'LOW'] = page[1]
            labels_dic[label_name + 'PAGE' + 'HIGH'] = page[0]

            if not labels_in_sequence:
                label_resolved_last_count = i - labels_count # Resolve multiplas labels em sequencia
            labels_count += 1 # Resolve o alinhamento do codigo
            label_resolved_last_idx = i
        else: new_lines.append(line)

    for i in range(len(new_lines)):
        line_content: list[str] = new_lines[i].split()

        for k in range(len(line_content)):
            content = line_content[k]

            for label in labels_dic:
                if content == label:
                    line_content[k] = labels_dic[label]
                    break
        new_lines[i] = ' '.join(line_content) + '\n'

    f_target.writelines(new_lines)

# HELPERS
def int_to_addr_page(num):
    num_addr = num % 256
    num_page = num // 256

    return hex(num_addr)[2:].zfill(2).upper(), hex(num_page)[2:].zfill(2).upper() # Return ADDR:PAGE IN FORMAT FOR EX: 1F:0A
