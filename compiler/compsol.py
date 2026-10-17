from typing import TextIO

def _compsol(f_target: TextIO, f_output: TextIO):
    target_content = f_target.readlines()
    output_buffer = ''

    for line in target_content:
        line_arr = line.split()
        arr_size = len(line_arr)

        if not arr_size: continue

        # Code to suport comments with ; comment or ;comment
        newlinearr = []
        for string in line_arr:
            if string == ';': break
            if string.find(';') != -1: break
            newlinearr.append(string)
        
        line_arr = newlinearr
        arr_size = len(line_arr)

        if not arr_size: continue

        if arr_size == 1:
            if line_arr[0] in mnemonicos_op:
                output_buffer += mnemonicos_op.get(line_arr[0])
            elif line_arr[0] in mnemonicos_reg:
                output_buffer += mnemonicos_reg.get(line_arr[0])
            else:
                output_buffer += hex(int(line_arr[0]))[2:].zfill(2)

        if arr_size == 2:
            if line_arr[0] in mnemonicos_op:
                output_buffer += mnemonicos_op.get(line_arr[0])

            if line_arr[1] in mnemonicos_reg:
                output_buffer += mnemonicos_reg.get(line_arr[1])
            else:
                output_buffer += line_arr[1]

    f_output.write(output_buffer)

mnemonicos_op = {
    'NOP': '00',
    'ADC': '01',
    'SBB': '02',
    'ROL': '03',
    'ROR': '04',
    'RCL': '05',
    'RCR': '06',
    'NEG': '07',
    'INCACC': '08',
    'DECACC': '09',
    'CMPEQ': '0A',
    'CLFN': '0B',
    'CLFZ': '0C',
    'CLFO': '0D',
    'CLFC': '0E',
    'CLF': '0F',

    'IMMH': '1',
    'IMML': '2',
    'IMM': '3',

    'LOADSFP': '4',
    'STORESFP': '5',
    'LOADP1': '6',
    'STOREP2': '7',

    'MOVA': '8',
    'MOVC': '9',

    'AGET': 'A',
    'BGET': 'B',
    'CGET': 'C',

    'SUM': 'D0',
    'SUB': 'D1',
    'SHL': 'D2',
    'SHR': 'D3',
    'NOT': 'D4',
    'AND': 'D5',
    'OR': 'D6',
    'XOR': 'D7',
    'JMP': 'D8',
    'JNEG': 'D9',
    'JZ': 'DA',
    'JPOS': 'DB',
    'JO': 'DC',
    'JC': 'DD',
    'JNZ': 'DE',
    'JINP': 'DF',

    'INCRFP': 'E0',
    'DECRFP': 'E1',
    'INCSFP': 'E2',
    'DECSFP': 'E3',
    'INCP1F': 'E4',
    'DECP1F': 'E5',
    'INCP2F': 'E6',
    'DECP2F': 'E7',
    'INCCOUNT': 'E8',
    'DECCOUNT': 'E9',
    'MOV1': 'EA',
    'MOV2': 'EB',
    'SEND': 'EC',
    'RECEIVE': 'ED',
    'CLA': 'EE',
    'PC': 'EF',

    'HALT': 'FF',
}

mnemonicos_reg = {
    'ACC':   '0',
    'BASE':  '1',
    'COUNT': '2',
    'RP':    '3',
    'RA':    '4',
    'SP':    '5',
    'SA':    '6',
    'P1H':   '7',
    'P1L':   '8',
    'P2H':   '9',
    'P2L':   'A',
    'H1':    'B',
    'H2':    'C',
    'H3':    'D',
    'H4':    'E',
    'FL':    'F',
}