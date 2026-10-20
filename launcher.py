import os
import curses
import sys
from compiler.compile import comp
from solvm import sol
import importlib.util

# Sim eu cansei de comentar toda hora em ingles
# A ideia eh:
# Criar um dicionario de comandos e seu ponteiro de funcao
# Adicionar as queridas setinhas pra cima baixo e lados alem do && nos comandos
# Adicionar suporte a comandos diretos pelo cmd real (isso vai acelerar dms o debug)
# Adicionar suporte a modulos que sao um dicionario em .py que apontam pra funcoes e tem tipos e etc, por exemplo pra ter saida de video no simulador de cpu
# Isso vai dar trabalho mas eh ez

# Variables
running = True
screen_buffer: list[str] = ['> ']
file = 'Not selected'
tick = 0.1
arrowx = 0 # Seta no screen_buffer -1
history = 0 # Comando antigo sendo pego

def cmdhandler(cmd: str, stdscr): # Lembrar q apos isso ja apeenda o '> '
    cmd_to_run = cmd.split('&&')

    for cmd_part in cmd_to_run:
        cmd_arr = cmd_part.split()
        string = '' if not len(cmd_arr) else cmd_arr[0]
        cmd_find = False

        for cmdstr in cmd_list:
            if cmdstr == string:
                cmd_list[cmdstr](cmd_arr)
                cmd_find = True
                break

        if not cmd_find:
            if string == '':
                pass # Pra n falar a mensagem chata ali so de enviar vazio
            else:
                sprint('Command not found, type help for more info')

stdscrptr = []
def main(stdscr):
    global screen_buffer, file, arrowx, history
    arrowx = 2
    curses.curs_set(0)
    stdscrptr.append(stdscr)

    if len(sys.argv) > 1:
        string_argv = ' '.join(sys.argv[1:])
        cmdhandler(string_argv, stdscr)
        screen_buffer.append('> ')

    while running:
        stdscr.clear()
        stdscr.addstr(0, 0, f'Sol R1 launcher | File selected: {file} | Clock freq in seconds: {tick}')

        max_y, max_x = stdscr.getmaxyx()
        curr = len(screen_buffer) - 1
        # Vou usar isso acima pra saber qual parte do buffer eu to

        for i in range(len(screen_buffer)):
            if i < len(screen_buffer) - 1:
                stdscr.addstr(i + 1, 0, ' ' * (max_x - 1))
                stdscr.addstr(i + 1, 0, screen_buffer[i])
            else:
                stdscr.addstr(i + 1, 0, ' ' * (max_x - 1))
                stdscr.addstr(i + 1, 0, screen_buffer[i][:arrowx] + '|' + screen_buffer[i][arrowx:])

        # Processar o char aqui
        char = stdscr.getch()
        if char in (10, 13): # ENTER
            cmdhandler(screen_buffer[curr][2:], stdscr)
            screen_buffer.append('> ')
            if len(screen_buffer) == max_y - 1:
                screen_buffer = screen_buffer[1:]
            arrowx = 2
            history = len(screen_buffer) - 1
        
        if char in (8, 127, curses.KEY_BACKSPACE):
            if arrowx > 2:
                screen_buffer[curr] = screen_buffer[curr][:arrowx - 1] + screen_buffer[curr][arrowx:]
                arrowx -= 1

        if char == curses.KEY_LEFT:
            if arrowx > 2:
                arrowx -= 1

        if char == curses.KEY_RIGHT:
            if arrowx < len(screen_buffer[curr]):
                arrowx += 1

        if char == curses.KEY_UP:
            for i in range(history):
                inv_i = history - i - 1
                if screen_buffer[inv_i][:2] == '> ':
                    history = inv_i
                    break
            screen_buffer[-1] = '> ' + screen_buffer[history][2:]
            arrowx = len(screen_buffer[history])

        if char == curses.KEY_DOWN:
            screen_buffer[-1] = '> '
            history = len(screen_buffer) - 1
        
        if 32 <= char <= 126: # Visiveis
            screen_buffer[curr] = screen_buffer[curr][:arrowx] + chr(char) + screen_buffer[curr][arrowx:]
            arrowx += 1

        stdscr.refresh()

# Helpers
def sprint(string):
    global screen_buffer
    max_y, max_x = stdscrptr[0].getmaxyx()
    screen_buffer.append(string)
    if len(screen_buffer) == max_y - 1:
        screen_buffer = screen_buffer[1:]
        

# Commands
def cmd_exit(cmd_arr):
    global running
    running = False

def cmd_help(cmd_arr):
    sprint('Command list:')
    sprint('help - show this message')
    sprint('exit - stop program')
    sprint('load - select .hex file')
    sprint('init - start vm')
    sprint('comp - compile a .sol file')
    sprint('soap - clear screen')
    sprint('tick - frequence of cpu vm')

def cmd_load(cmd_arr):
    global file
    if len(cmd_arr) == 2:
        path = cmd_arr[1]

        if os.path.exists(path) and os.path.isfile(path):
            if path[len(path) - 4:] == '.hex':
                file = cmd_arr[1]
            else:
                sprint('Invalid file format')
        else:
            sprint('Path not exists')
    else:
        sprint('load usage: load file-path')

def cmd_init(cmd_arr):
    if file != 'Not selected':
        vm = sol(file, tick)
        if vm.init():
            vm.run()

def cmd_comp(cmd_arr):
    if len(cmd_arr) == 3:
        comp('./build', cmd_arr[1], cmd_arr[2], [screen_buffer])

def cmd_soap(cmd_arr):
    screen_buffer.clear()

def cmd_tick(cmd_arr):
    global tick
    if len(cmd_arr) == 2:
        tick = float(cmd_arr[1])

# Command dictonary
cmd_list: dict = {
    'exit': cmd_exit,
    'help': cmd_help,
    'load': cmd_load,
    'init': cmd_init,
    'comp': cmd_comp,
    'soap': cmd_soap,
    'tick': cmd_tick,
}

if __name__ == '__main__':
    curses.wrapper(main)