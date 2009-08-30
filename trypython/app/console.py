import sys

import clr
clr.AddReference('IronPython')
clr.AddReference('Microsoft.Scripting')

from System import Uri
from System.Threading import Thread
from System.Windows import Application
from System.Windows.Browser import HtmlPage
from System.Windows.Controls import TextBox, TextBlock
from System.Windows.Input import Key

from System.Windows.Media import FontFamily
from System.Windows import TextWrapping, Thickness

from consoletextbox import ConsoleTextBox, get_console_block

from IronPython.Hosting import Python
from Microsoft.Scripting import ScriptCodeParseResult, SourceCodeKind

import traceback

from consolehistory import ConsoleHistory

__version__ = '0.1.0'

python_version = '.'.join(str(n) for n in sys.version_info[:3])
doc = "Try Python: version %s" % __version__
banner = ("Python %s on Silverlight\nPython in the Browser %s by Michael Foord\n" 
          "Type reset to clear the console and gohome to exit.\n" % (python_version, __version__))
home = 'http://code.google.com/p/trypython/'

ps1 = '>>> '
ps2 = '... '

_main_id = Thread.CurrentThread.ManagedThreadId

def invoke(function):
    """This decorator wraps functions to invoke them onto the GUI if they are 
    called from a background thread."""
    def inner(*args, **kwargs):
        if Thread.CurrentThread.ManagedThreadId != _main_id:
            return root.Dispatcher.BeginInvoke(lambda: function(*args, **kwargs))
        return function(*args, **kwargs)
    return inner


@invoke
def _debug(data):
    """Comment / uncomment to output debug info"""
    #HtmlPage.Document.debugging.innerHTML += data.replace('\n', '<br />')

    
@invoke
def scroll():
    if scroller.ScrollableHeight > 0:
        scroller.ScrollToVerticalOffset(scroller.ScrollableHeight + scroller.ActualHeight)


@invoke
def focus_text_box(sender, event):
    #_debug('focus\n')
    HtmlPage.Plugin.Focus()
    console_textbox.Focus()
    
    
class StatefulPrinter(object):
    def __init__(self, parent):
        self.block = None
        self.parent = parent
    
    @invoke
    def write(self, data):
        if self.block is None:
            self.block = get_console_block()
            self.parent.Children.Add(self.block)
            
        block = self.block
        if data.endswith('\n'):
            data = data[:-1]
            self.block = None
        
        block.Text += data
        _debug(repr(data) +'\n')
    
    def print_new(self, data):
        if self.block is not None:
            self.block = None
        if not data.endswith('\n'):
            data += '\n'
        self.write(data)


def get_magic_function(function, string):
    class MagicFunction(object):
        def __call__(self):
            function()
            return string
        def __repr__(self):
            function()
            return string
    return MagicFunction()
    
    
# Magic flag from the codeop module
PyCF_DONT_IMPLY_DEDENT = 0x200          # Matches pythonrun.h

class Console(object):
    def __init__(self, context):
        self.original_context = context
        
        def reset():
            self._reset_needed = True
        self.original_context['reset'] = get_magic_function(reset, 'resetting')
        self.original_context['gohome'] = get_magic_function(lambda: HtmlPage.Window.Navigate(Uri(home)), 'Leaving...')
        
        self.context = None
        self.engine = Python.CreateEngine()
        self.scope = self.engine.CreateScope()
        self.history = None
        self._reset_needed = False
    
        
    def reset(self):
        _debug('reset\n')
        console_output.Children.Clear()
        self._reset_needed = False
        self.context = self.original_context.copy()
        self.history = ConsoleHistory()
        print_new(banner)
    
        
    def write(self, data):
        _print(data)

    
    def is_complete(self, text):
        # Mac Safari uses '\r' for newlines in Silverlight TextBox??
        text = text.rstrip(' ').replace('\r\n', '\n').replace('\r', '\n')
        source = self.engine.CreateScriptSourceFromString(text, '<stdin>', SourceCodeKind.InteractiveCode)
        
        result = source.GetCodeProperties()
        if result == ScriptCodeParseResult.IncompleteToken:
            return False
        elif result == ScriptCodeParseResult.IncompleteStatement:
            if not text.endswith('\n'):
                return False
        return True
    
    
    def on_first_line(self, text):
        first_line_end = text.find('\n')
        if first_line_end == -1:
            return True
        return console_textbox.SelectionStart <= first_line_end
    
    
    def on_last_line(self, text):
        last_line_end = text.rfind('\n')
        if last_line_end == -1:
            return True
        return console_textbox.SelectionStart > last_line_end
        
    
    def handle_key(self, sender, event):
        contents = console_textbox.Text.replace('\r\n', '\n').replace('\r', '\n')
        key = event.Key
        start = console_textbox.SelectionStart
        end = start + console_textbox.SelectionLength

        if key != Key.Enter:
            if key == key.Up:
                if self.on_first_line(contents):
                    event.Handled = True
                    previous = self.history.back(contents)
                    if previous is not None:
                        console_textbox.Text = previous
                        console_textbox.SelectionStart = len(previous)
                    return
                
            elif key == key.Down:
                if self.on_last_line(contents):
                    event.Handled = True
                    next = self.history.forward(contents)
                    if next is not None:
                        console_textbox.Text = next
                        console_textbox.SelectionStart = len(next)
                    return
            
            elif key == key.Tab:
                event.Handled = True
                console_textbox.Text = console_textbox.Text[:start] + '    ' + console_textbox.Text[end:]
                console_textbox.SelectionStart = start + 4
                return
                
            TextBox.OnKeyDown(console_textbox, event)
            return
    
        def empty_or_comment_only():
            if not contents.strip():
                return True
            numlines = len(contents.splitlines())
            if numlines >= 2:
                return False
            return contents.strip().startswith('#')
        
        if empty_or_comment_only():
            # needed or we get a SyntaxError
            event.Handled = True
            console_textbox.Text = ''
            print_lines(contents)
            return
        
        complete = self.is_complete(contents)
        if complete:
            print_lines(contents)
            console_textbox.Text = ''
            event.Handled = True
            self.history.append(contents)
            try:
                code = compile(contents + '\n', '<stdin>', 'single', PyCF_DONT_IMPLY_DEDENT)
                exec code in self.context
            except:
                exc_type, value, tb = sys.exc_info()
                if value is None:
                    # String exceptions
                    # workaround for IronPython bug
                    exc_type = Exception
                    value = Exception('StringException')
                    
                tblist = traceback.extract_tb(tb)
                message = traceback.format_list(tblist)
                del message[:1]
                if message:
                    message.insert(0, "Traceback (most recent call last):\n")
                message.extend(traceback.format_exception_only(exc_type, value))
                print_new(''.join(message))
        
            if self._reset_needed:
                self.reset()
            else:
                scroll()

root = Application.Current.RootVisual
console_output = root.consoleOutput
prompt_panel = root.prompt
scroller = root.scroller
textbox_parent = root.consoleParent
console_textbox = ConsoleTextBox(scroller.Width - 75)
textbox_parent.Child = console_textbox

printer = StatefulPrinter(console_output)
_print = printer.write
print_new = printer.print_new

console_output.GotFocus += focus_text_box
scroller.GotFocus += focus_text_box
root.container.GotFocus += focus_text_box


def print_lines(data):
    lines = data.replace('\r\n', '\n').replace('\r', '\n').split('\n')
    lines[0] = ps1 + lines[0]
    lines[1:] = [ps2 + line for line in lines[1:]]
    print_new('\n'.join(lines))

context = {
    "__name__": "__console__", 
    "__doc__": doc,
    "__version__": __version__,
}

console = Console(context)
console_textbox.KeyDown += console.handle_key
console.reset()


_debug('Started\n')


sys.stdout = console
sys.stderr = console

