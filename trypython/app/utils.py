from __future__ import with_statement

from System.IO import Path
from System.Threading import Thread
from System.Windows import Application
from System.Windows.Browser import HtmlPage
from System.Windows.Markup import XamlReader

from storage import original_open as open

debug = False

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
    if not debug:
        return
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

    HtmlPage.Document.debugging.innerHTML = lineno + data.replace('\n', '<br />') + current

    
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


def blow_up():
    raise Exception('boom')


_code_cache = {}

def get_code(path, page, index):
    directory = Path.GetDirectoryName(path)
    code_directory = Path.Combine(directory, 'code%s' % page)
    code_file = Path.Combine(code_directory, 'example%s.txt' % index)
    if code_file in _code_cache:
        return _code_cache[code_file]
    
    handle = open(code_file)
    code = handle.read().decode('utf-8')
    code = code.replace('\r\n', '\n').replace('\r', '\n')
    code_lines = code.splitlines() 
    handle.close()
    _code_cache[code_file] = code_lines
    return code_lines


def load_document(path, page, console):
    with open(path) as handle:
        xaml = handle.read().decode('utf-8')
    document = XamlReader.Load(xaml)
    for index, button in enumerate(find_buttons(document)):
        def handler(sender, event, index=index):
            code = get_code(path, page, index)
            console.handle_lines(code)
        button.Click += handler
    return document


def find_buttons(tree):
    if tree.__class__.__name__ == 'Button':
        yield tree
    #if hasattr(tree, 'Content'):
        #return buttons + find_buttons(tree.Content)
    #if hasattr(tree, 'Child'):
        #return buttons + find_buttons(tree.Child)
    #if hasattr(tree, 'Items'):
        #for item in tree.Items:
            #buttons += find_buttons(item, buttons)
        #return buttons
    if hasattr(tree, 'Children'):
        for item in tree.Children:
            for button in find_buttons(item):
                yield button
    