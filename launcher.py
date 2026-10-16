import os
import curses

running = True
screen_buffer: list[str] = ['> ']
file = 'Not selected'
tick = 10

def cmdhandler(cmd: str, stdscr): # Lembrar q apos isso ja apeenda o '> '
    global running, screen_buffer, file
    cmd_arr = cmd.split()
    string = '' if not len(cmd_arr) else cmd_arr[0]

    if string == 'exit':
        running = False
    elif string == 'help':
        screen_buffer.append('Command list:')
        screen_buffer.append('help - show this message')
        screen_buffer.append('exit - stop program')
        screen_buffer.append('load - select .hex file')
        screen_buffer.append('init - start vm')
        screen_buffer.append('comp - compile a .sol file')
        screen_buffer.append('tick - frequence of cpu vm')
    elif string == 'load':
        if len(cmd_arr) == 2:
            path = cmd_arr[1]

            if os.path.exists(path) and os.path.isfile(path):
                if path[len(path) - 4:] == '.hex':
                    file = cmd_arr[1]
                else:
                    screen_buffer.append('Invalid file format')
            else:
                screen_buffer.append('Path not exists')
        else:
            screen_buffer.append('load usage: load file-path')
    elif string == 'init':
        pass
    elif string == '':
        pass # Pra n falar a mensagem chata ali so de enviar vazio
    else:
        screen_buffer.append('Command not found, type help for more info')

def main(stdscr):
    global screen_buffer, file

    while running:
        stdscr.clear()
        stdscr.addstr(0, 0, f'Sol R1 launcher | File selected: {file} | Clock freq in ms: {tick}')

        max_y, max_x = stdscr.getmaxyx()
        curr = len(screen_buffer) - 1
        # Vou usar isso acima pra saber qual parte do buffer eu to

        for i in range(len(screen_buffer)):
            stdscr.addstr(i + 1, 0, ' ' * (max_x - 1))
            stdscr.addstr(i + 1, 0, screen_buffer[i])

        # Processar o char aqui
        char = stdscr.getch()
        if char in (10, 13): # ENTER
            cmdhandler(screen_buffer[curr][2:], stdscr)
            screen_buffer.append('> ')
            if len(screen_buffer) == max_y - 1:
                screen_buffer = screen_buffer[1:]
        
        if char in (8, 127, curses.KEY_BACKSPACE):
            if len(screen_buffer[curr]) > 2:
                screen_buffer[curr] = screen_buffer[curr][:len(screen_buffer[curr]) - 1]
        
        if 32 <= char <= 126: # Visiveis
            screen_buffer[curr] += chr(char)
        
        stdscr.refresh()

if __name__ == '__main__':
    curses.wrapper(main)