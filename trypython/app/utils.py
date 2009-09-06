
from System.Threading import Thread
from System.Windows import Application
from System.Windows.Browser import HtmlPage


_main_id = Thread.CurrentThread.ManagedThreadId

root = None

def SetInvokeRoot(element):
    global root
    root = element

def invoke(function):
    """This decorator wraps functions to invoke them onto the GUI if they are 
    called from a background thread. We *shouldn't* invoke if called from
    the main thread or messages can end up out of order."""
    def inner(*args, **kwargs):
        if Thread.CurrentThread.ManagedThreadId != _main_id:
            return root.Dispatcher.BeginInvoke(lambda: function(*args, **kwargs))
        return function(*args, **kwargs)
    return inner

def always_invoke(function):
    def inner(*args, **kwargs):
        return root.Dispatcher.BeginInvoke(lambda: function(*args, **kwargs))
    return inner
    

line = 0

@invoke
def _debug(*args):
    global line
    line += 1
    def _str(arg):
        if isinstance(arg, str):
            return arg
        return str(arg)
    
    data = ' '.join(_str(arg) for arg in args)
    if not data.endswith('\n'):
        data += '\n'
    current = HtmlPage.Document.debugging.innerHTML
    lineno = '%s. ' % line
    # Comment / uncomment this line to output debug info
    #HtmlPage.Document.debugging.innerHTML = lineno + data.replace('\n', '<br />') + current

    
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
        self.__doc__ = function.__doc__
        
    def __call__(self):
        self.function()
        return self.string
        
    def __repr__(self):
        self.function()
        return self.string


def blow_up():
    raise Exception('boom')
