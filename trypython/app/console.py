import sys

import clr
clr.AddReference('IronPython')
clr.AddReference('Microsoft.Scripting')

from System import Uri
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
          "Type reset() to clear the console and gohome() to exit.\n" % (python_version, __version__))
home = 'http://code.google.com/p/trypython/'

ps1 = '>>> '
ps2 = '... '


def invoke(function):
    """This decorator wraps functions to invoke them onto the GUI.
    This makes the functions safe to call from a background thread."""
    def inner(*args, **kwargs):
        return root.Dispatcher.BeginInvoke(lambda: function(*args, **kwargs))
    return inner


@invoke
def _debug(data):
    """Comment / uncomment to output debug info"""
    HtmlPage.Document.debugging.innerHTML += data.replace('\n', '<br />')

    
@invoke
def scroll():
    if scroller.ScrollableHeight > 0:
        scroller.ScrollToVerticalOffset(scroller.ScrollableHeight + scroller.ActualHeight)


@invoke
def focus_text_box(sender, event):
    _debug('focus\n')
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
    
    def print_new(self, data):
        if self.block is not None:
            self.block = None
        if not data.endswith('\n'):
            data += '\n'
        self.write(data)



class Console(object):
    def __init__(self, context):
        self.context = context
        self.scope = None
        self.engine = Python.CreateEngine()
        self.history = None
        
    def reset(self):
        self.scope = self.engine.CreateScope()
        for name, value in self.context.items():
            self.scope.SetVariable(name, value)
        self.scope.SetVariable('__console', self)
        set_output_code = "import sys\nsys.stdout = __console\nsys.stderr = __console\n"
        source = self.engine.CreateScriptSourceFromString(set_output_code, SourceCodeKind.Statements)
        source.Execute(self.scope)
        
        self.history = ConsoleHistory()
    
    
    def write(self, data):
        _print(data)

    def is_complete(self, text):
        # Mac Safari uses '\r' for newlines in Silverlight TextBox??
        text = text.rstrip(' ').replace('\r\n', '\n').replace('\r', '\n')
        source = self.engine.CreateScriptSourceFromString(text, '<stdin>', SourceCodeKind.InteractiveCode)
        
        result = source.GetCodeProperties()
        if result == ScriptCodeParseResult.IncompleteToken:
            return False, source
        if result == ScriptCodeParseResult.IncompleteStatement:
            if not text.endswith('\n'):
                return False, source
        return True, source
    
    def on_first_line(self, text):
        # XXXX do we have a problem where '\r\n' has been replaced by '\n'?
        first_line_end = text.find('\n')
        if first_line_end == -1:
            return True
        return console_textbox.SelectionStart <= first_line_end
    
    def on_last_line(self, text):
        # XXXX same problem as on_first_line
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
                    _debug('Prev: %r' % previous)
                    if previous is not None:
                        console_textbox.Text = previous
                        console_textbox.SelectionStart = len(previous)
                    return
                
            elif key == key.Down:
                if self.on_last_line(contents):
                    event.Handled = True
                    next = self.history.forward(contents)
                    _debug('Next: %r' % next)
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
        
        if not contents.strip():
            # needed or we get a SyntaxError
            event.Handled = True
            console_textbox.Text = ''
            print_new(ps1)
            return
        
        complete, source = self.is_complete(contents)
        if complete:
            print_lines(contents)
            console_textbox.Text = ''
            event.Handled = True
            self.history.append(contents)
            try:
                source.Execute(self.scope)
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



def print_lines(data):
    lines = data.replace('\r\n', '\n').replace('\r', '\n').split('\n')
    lines[0] = ps1 + lines[0]
    lines[1:] = [ps2 + line for line in lines[1:]]
    print_new('\n'.join(lines))

def reset():
    console.reset()
    console_output.Children.Clear()
    _print(banner)


def gohome():
    HtmlPage.Window.Navigate(Uri(home))
    return 'Leaving...'


context = {
    "__name__": "__console__", 
    "__doc__": doc,
    "__version__": __version__,
    "reset": reset,
    "gohome": gohome
}



console = Console(context)
console_textbox.KeyDown += console.handle_key
reset()


_debug('Started\n')

class Writer(object):
    def write(self, data):
        _debug(data)

writer = Writer()

sys.stdout = writer
sys.stderr = writer
