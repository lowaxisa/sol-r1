sprint = None

def init(ctx):
    global sprint
    sprint = ctx['sprint']
    ctx['hello'] = execute
    ctx['help_list'].append('hello - show msg from hello')
    msg()

def execute(cmd_arr: list): msg()

def msg():
    sprint('Hello, i am the module hello.py!')