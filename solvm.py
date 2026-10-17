import time
import curses

class sol:
    def __init__(self, filepath, tick):
        self.path = filepath
        self.disk = ['00'] * 256 # small HEX disk
        self.cpu = {
            'regs': {
                'ACC':   '00', 'BASE':  '00',
                'COUNT': '00', 'RP':    '00',
                'RA':    '00', 'SP':    '00',
                'SA':    '00', 'P1H':   '00',
                'P1L':   '00', 'P2H':   '00',
                'P2L':   '00', 'H1':    '00',
                'H2':    '00', 'H3':    '00',
                'H4':    '00', 'FL':    '00',
            },
            'pc_addr': 0,
            'pc_page': 0,
            'imm_buffer': '00',

            'input_ready': False, # Input flag
            'input_data': '00',
            'output_data': '00',
            'send_pin': False,
            'receive_pin': False,

            'last_inst': '',
            'halt': False,
        }
        self.tick = tick

    def init(self):
        with open(self.path, 'r', encoding='utf-8') as file:
            content = file.readline() # So tem uma por padrao
            for i in range(len(content)):
                if i % 2 == 1: continue

                hex_byte = content[i] + content[i + 1]
                self.disk[i // 2] = hex_byte
        return True

    def step(self):
        if self.cpu['halt']: return

        # Input pool
        if self.cpu['receive_pin']:
            self.cpu['receive_pin'] = False
            self.cpu['input_ready'] = True

        op = self.disk_pc_read()
        op_family = op[0]
        op_inst = op[1]
        self.cpu['last_inst'] = op

        if op_family == '0': # NOP
            pass
        if op_family == '1': # IMMH
            self.cpu['imm_buffer'] = op_inst + self.cpu['imm_buffer'][1]
        if op_family == '2': # IMML
            self.cpu['imm_buffer'] = self.cpu['imm_buffer'][0] + op_inst
        if op_family == '3': # IMM
            self.cpu['regs'][mnemonicos_reg[op_inst]] = self.cpu['imm_buffer']

        if op_family == '4': # LOADSFP
            self.cpu['regs'][mnemonicos_reg[op_inst]] = self.diskptr_read(self.cpu['regs']['SA'], self.cpu['regs']['SP'])
        if op_family == '5': # STORESFP
            self.diskptr_write(self.cpu['regs']['SA'], self.cpu['regs']['SP'], self.cpu['regs'][mnemonicos_reg[op_inst]])
        if op_family == '6': # LOADP1
            self.cpu['regs'][mnemonicos_reg[op_inst]] = self.diskptr_read(self.cpu['regs']['P1L'], self.cpu['regs']['P1H'])
        if op_family == '7': # STOREP2
            self.diskptr_write(self.cpu['regs']['P2L'], self.cpu['regs']['P2H'], self.cpu['regs'][mnemonicos_reg[op_inst]])

        if op_family == '8': #MOVA
            self.cpu['regs'][mnemonicos_reg[op_inst]] = self.cpu['regs']['ACC']
        if op_family == '9': #MOVC
            self.cpu['regs'][mnemonicos_reg[op_inst]] = self.cpu['regs']['COUNT']

        if op_family == 'A': # AGET
            self.cpu['regs']['ACC'] = self.cpu['regs'][mnemonicos_reg[op_inst]]
        if op_family == 'B': # BGET
            self.cpu['regs']['BASE'] = self.cpu['regs'][mnemonicos_reg[op_inst]]
        if op_family == 'C': # CGET
            self.cpu['regs']['COUNT'] = self.cpu['regs'][mnemonicos_reg[op_inst]]

        if op_family == 'D':
            alu_flags = self.get_alu_flags()

            # Pre def
            hex_value = None
            bin_value = None
            carryout = False
            msbcarryin = False

            ACCV = self.cpu['regs']['ACC']
            BASEV = self.cpu['regs']['BASE']

            if op_inst == '0': # SUM
                hex_value, bin_value, carryout, msbcarryin = self.alu_sum(ACCV, BASEV, False)
            if op_inst == '1': # SUB
                hex_value, bin_value, carryout, msbcarryin = self.alu_sub(ACCV, BASEV)
            if op_inst == '2': # SHL
                hex_value, bin_value = self.op_leftshift(ACCV)
            if op_inst == '3': # SHR
                hex_value, bin_value = self.op_rightshift(ACCV)
            if op_inst == '4': # NOT
                hex_value, bin_value = self.op_not(ACCV)
            if op_inst == '5': # AND
                hex_value, bin_value = self.op_and(ACCV, BASEV)
            if op_inst == '6': # OR
                hex_value, bin_value = self.op_or(ACCV, BASEV)
            if op_inst == '7': # XOR
                hex_value, bin_value = self.op_xor(ACCV, BASEV)

            if op_inst == '8':                           self.pc_jmp() # JMP
            if op_inst == '9' and alu_flags['negative']: self.pc_jmp() # JNEG
            if op_inst == 'A' and alu_flags['zero']:     self.pc_jmp() # JZ
            if op_inst == 'B' and alu_flags['positive']: self.pc_jmp() # JPOS
            if op_inst == 'C' and alu_flags['overflow']: self.pc_jmp() # JO
            if op_inst == 'D' and alu_flags['carry']:    self.pc_jmp() # JC
            if op_inst == 'E' and alu_flags['notzero']:  self.pc_jmp() # JNZ
            if op_inst == 'F' and self.cpu['input']:     self.pc_jmp() # JINP

            if op_inst in ('0', '1', '2', '3', '4', '5', '6', '7'):
                self.cpu['regs']['ACC'] = hex_value
                self.calc_alu_flags(hex_value, bin_value, carryout, msbcarryin)

        if op_family == 'E': # Input, Misc and hardware aceleration instruction
            if op_inst == '0': self.super_inc_and_upd_flag('RP', 'RA') # INCRFP
            if op_inst == '1': self.super_dec_and_upd_flag('RP', 'RA') # DECRFP
            if op_inst == '2': self.super_inc_and_upd_flag('SP', 'SA') # INCSFP
            if op_inst == '3': self.super_dec_and_upd_flag('SP', 'SA') # DECSFP

            if op_inst == '4': self.super_inc_and_upd_flag('P1H', 'P1L') # INCP1F
            if op_inst == '5': self.super_dec_and_upd_flag('P1H', 'P1L') # DECP1F
            if op_inst == '6': self.super_inc_and_upd_flag('P2H', 'P2L') # INCP2F
            if op_inst == '7': self.super_dec_and_upd_flag('P2H', 'P2L') # DECP2F

            if op_inst == '8': self.inc_and_upd_flag('COUNT') # INCCOUNT
            if op_inst == '9': self.dec_and_upd_flag('COUNT') # DECCOUNT

            if op_inst == 'A': # MOV1
                self.cpu['regs']['RA'] = self.cpu['regs']['P1L']
                self.cpu['regs']['RP'] = self.cpu['regs']['P1H']
            if op_inst == 'B': # MOV2
                self.cpu['regs']['RA'] = self.cpu['regs']['P2L']
                self.cpu['regs']['RP'] = self.cpu['regs']['P2H']
            if op_inst == 'C':
                self.cpu['output_data'] = self.cpu['regs']['ACC']
                self.cpu['send_pin'] = True
            if op_inst == 'D':
                self.cpu['regs']['ACC'] = self.cpu['input_data']
                self.cpu['input_ready'] = False
            if op_inst == 'E': # CLA
                self.cpu['regs']['FL'] = '00'
            
            if op_inst == 'F': # PC
                self.cpu['regs']['RA'] = hex(self.cpu['pc_addr'])[2:].zfill(2)
                self.cpu['regs']['RP'] = hex(self.cpu['pc_page'])[2:].zfill(2)
        
        if op_family == 'F': # HALT
            self.cpu['halt'] = True

        self.pc_inc()

    def run(self):
        curses.endwin()

        while not self.cpu['halt']:
            self.step()

            print('\n----------------------------------')
            print('Instruction: 0x' + self.cpu['last_inst'] + ' | PC: ' + hex(self.cpu['pc_page'])[2:].zfill(2) + ':' + hex(self.cpu['pc_addr'])[2:].zfill(2))

            print('Registers:')
            reglist = [[], [], [], []] # 4x4 matrix view
            for k, v in self.cpu['regs'].items():
                idx = len(reglist[0]) + len(reglist[1]) + len(reglist[2]) + len(reglist[3])
                reglist[idx // 4].append(f'reg: {k},' + ' ' * (6 - len(k)) + f'value: {v}')
            
            for y in range(len(reglist)):
                for x in range(len(reglist[y])):
                    print(reglist[y][x] + ' ' * (22 - len(reglist[y][x])), end='')
                    if x < 3: print(' | ', end='')
                print('')

            time.sleep(self.tick)

        print('\nCPU halted, press enter to continue')
        input()

    def calc_alu_flags(self, hexnum, binnum, msbcarryout, msbcarryin):
        fl = self.cpu['regs']['FL'] # FLAGS register
        binfl = list(self.hex_to_bin(fl))

        if binnum[0] == '1':          binfl[7] = '1' # Negative
        if hexnum == '00':            binfl[6] = '1' # Zero
        if msbcarryout != msbcarryin: binfl[5] = '1' # Overflow
        if msbcarryout:               binfl[4] = '1' # Carry

        binfl = ''.join(binfl)
        newfl = self.bin_to_hex(binfl)
        self.cpu['regs']['FL'] = newfl

    def get_alu_flags(self):
        fl = self.cpu['regs']['FL'] # FLAGS register
        binfl = self.hex_to_bin(fl)

        negative = True if binfl[7] == '1' else False
        zero     = True if binfl[6] == '1' else False
        overflow = True if binfl[5] == '1' else False
        carry    = True if binfl[4] == '1' else False
        positive = not negative and not zero
        notzero  = not zero

        flags = {
            'negative': negative,
            'zero':     zero,
            'positive': positive,
            'overflow': overflow,
            'notzero':  notzero,
            'carry':    carry,
        }

        return flags

    def inc_and_upd_flag(self, REG):
        hex_value, bin_value, carryout, msbcarryin = self.alu_inc(self.cpu['regs'][REG])
        self.calc_alu_flags(hex_value, bin_value, False, False)
        self.cpu['regs'][REG] = hex_value

    def dec_and_upd_flag(self, REG):
        hex_value, bin_value, carryout, msbcarryin = self.alu_dec(self.cpu['regs'][REG])
        self.calc_alu_flags(hex_value, bin_value, False, False)
        self.cpu['regs'][REG] = hex_value

    def super_inc_and_upd_flag(self, REGH, REGL):
        hex_value, bin_value, carryout, msbcarryin = self.alu_inc(self.cpu['regs'][REGL])
        self.cpu['regs'][REGL] = hex_value
        if carryout:
            hex_value, bin_value, carryout, msbcarryin = self.alu_inc(self.cpu['regs'][REGH])
            self.cpu['regs'][REGH] = hex_value

    def super_dec_and_upd_flag(self, REGH, REGL):
        hex_value, bin_value, carryout, msbcarryin = self.alu_dec(self.cpu['regs'][REGL])
        self.cpu['regs'][REGL] = hex_value
        if carryout:
            hex_value, bin_value, carryout, msbcarryin = self.alu_dec(self.cpu['regs'][REGH])
            self.cpu['regs'][REGH] = hex_value

    def pc_inc(self):
        next_addr = (self.cpu['pc_addr'] + 1) % 256
        if next_addr == 0:
            self.cpu['pc_page'] = (self.cpu['pc_page'] + 1) % 256
        self.cpu['pc_addr'] = next_addr

    def pc_jmp(self):
        self.cpu['pc_addr'] = int('0x' + self.cpu['regs']['RA'], 16)
        self.cpu['pc_page'] = int('0x' + self.cpu['regs']['RP'], 16)

    def disk_pc_read(self):
        return self.disk[self.cpu['pc_addr'] + (self.cpu['pc_page'] * 256)]
    
    def diskptr_read(self, addr, page):
        _addr = int('0x' + addr, 16)
        _page = int('0x' + page, 16)
        return self.disk[_addr + (_page * 256)]

    def diskptr_write(self, addr, page, value):
        _addr = int('0x' + addr, 16)
        _page = int('0x' + page, 16)
        self.disk[_addr + (_page * 256)] = value

    def op_not(self, hexnum): # Recebe aquele hex sem 0x da minha cpu
        binnum = self.hex_to_bin(hexnum)
        result = ''

        for char in binnum:
            result += '0' if char == '1' else '1'

        hex_result = self.bin_to_hex(result)
        return hex_result, result

    def op_and(self, hexnumA, hexnumB):
        binumA = self.hex_to_bin(hexnumA)
        binumB = self.hex_to_bin(hexnumB)
        result = ''

        for i in range(len(binumA)):
            result += '1' if binumA[i] == '1' and binumB[i] == '1' else '0'

        hex_result = self.bin_to_hex(result)
        return hex_result, result

    def op_or(self, hexnumA, hexnumB):
        binumA = self.hex_to_bin(hexnumA)
        binumB = self.hex_to_bin(hexnumB)
        result = ''

        for i in range(len(binumA)):
            result += '1' if binumA[i] == '1' or binumB[i] == '1' else '0'

        hex_result = self.bin_to_hex(result)
        return hex_result, result

    def op_xor(self, hexnumA, hexnumB):
        binumA = self.hex_to_bin(hexnumA)
        binumB = self.hex_to_bin(hexnumB)
        result = ''

        for i in range(len(binumA)):
            result += '1' if binumA[i] != binumB[i] else '0'

        hex_result = self.bin_to_hex(result)
        return hex_result, result

    def op_leftshift(self, hexnum):
        binnum = self.hex_to_bin(hexnum)
        result = binnum[1:] + '0'

        hex_result = self.bin_to_hex(result)
        return hex_result, result

    def op_rightshift(self, hexnum):
        binnum = self.hex_to_bin(hexnum)
        result = '0' + binnum[:len(binnum) - 1]

        hex_result = self.bin_to_hex(result)
        return hex_result, result

    def alu_sum(self, hexnumA, hexnumB, carryin):
        binumA = self.hex_to_bin(hexnumA)
        binumB = self.hex_to_bin(hexnumB)
        result = ''
        carry = False
        msbcarryin = False

        numlen = len(binumA)
        maxidx = numlen - 1

        for i in range(numlen):
            k = maxidx - i
            a = binumA[k]
            b = binumB[k]

            if k == 0:
                msbcarryin = carry
            
            if carryin and k == maxidx:
                carry = True

            xor_ab = False
            all_true = False

            if (a == '1' and not b == '1') or (not a == '1' and b == '1'):
                xor_ab = True
            if a == '1' and b == '1':
                all_true = True

            if carry:
                if all_true:
                    carry = True
                    result += '1'
                elif xor_ab:
                    carry = True
                    result += '0'
                else:
                    carry = False
                    result += '1'
            else:
                if all_true:
                    carry = True
                    result += '0'
                elif xor_ab:
                    carry = False
                    result += '1'
                else:
                    carry = False
                    result += '0'

        temp = ''
        for i in range(numlen): # Desinverte o resultado final
            k = maxidx - i
            temp += result[k]
        result = temp
        
        return self.bin_to_hex(result), result, carry, msbcarryin

    def alu_sub(self, hexnumA, hexnumB):
        return self.alu_sum(hexnumA, self.op_not(hexnumB)[0], True)

    def alu_inc(self, hexnumA):
        return self.alu_sum(hexnumA, '01', False)

    def alu_dec(self, hexnumA):
        return self.alu_sum(hexnumA, self.op_not('01')[0], True)

    def hex_to_bin(self, hexnum): # Usa o sem 0x e retorna o bin sem 0b
        return bin(int('0x' + hexnum, 16))[2:].zfill(8)

    def bin_to_hex(self, binnum): # Usa o sem 0b e retorna o sem 0x
        return hex(int('0b' + binnum, 2))[2:].zfill(2)

mnemonicos_reg = {
    '0': 'ACC',
    '1': 'BASE',
    '2': 'COUNT',
    '3': 'RP',
    '4': 'RA',
    '5': 'SP',
    '6': 'SA',
    '7': 'P1H',
    '8': 'P1L',
    '9': 'P2H',
    'A': 'P2L',
    'B': 'H1',
    'C': 'H2',
    'D': 'H3',
    'E': 'H4',
    'F': 'FL',
}
