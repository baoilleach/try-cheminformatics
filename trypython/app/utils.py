
from System.Threading import Thread
from System.Windows import Application

_main_id = Thread.CurrentThread.ManagedThreadId

def invoke(function):
    """This decorator wraps functions to invoke them onto the GUI if they are 
    called from a background thread."""
    def inner(*args, **kwargs):
        if Thread.CurrentThread.ManagedThreadId != _main_id:
            root = Application.Current.RootVisual
            return root.Dispatcher.BeginInvoke(lambda: function(*args, **kwargs))
        return function(*args, **kwargs)
    return inner


def empty_or_comment_only(contents):
    if not contents.strip():
        return True
    numlines = len(contents.splitlines())
    if numlines >= 2:
        return False
    return contents.strip().startswith('#')

def get_indent(line):
    spaces = ''
    for char in line:
        if char == ' ':
            spaces += ' '
        else:
            break
    return spaces

def is_terminator(line):
    line = line.lstrip()
    terminators = ['pass', 'break', 'continue', 'return']
    for entry in terminators:
        if line.startswith(entry):
            return True
    return False


class magic_function(object):
    def __init__(self, function, string):
        self.function = function
        self.string = string
        
    def __call__(self):
        self.function()
        return self.string
        
    def __repr__(self):
        self.function()
        return self.string