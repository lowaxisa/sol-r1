target = 'hello'
sprint = None

def context(cmd_dic: dict, help_list: list):
    help_list.append('hello - show msg from hello')

def execute(cmd_arr: list): msg()

def msg(passed_sprint: callable=sprint):
    global sprint
    if passed_sprint != None:
        sprint = passed_sprint
    sprint('Hello, i am the module hello.py!')