
import sys

from System import Uri
from System.Windows import Application, Thickness, TextWrapping
from System.Windows.Browser import HtmlPage
from System.Windows.Input import Key
from System.Windows.Controls import TextBox
from System.Windows.Media import FontFamily

from code import InteractiveConsole

__version__ = '0.1.0'

doc = "Try Python: version %s" % __version__
banner = ("Python %s on Silverlight\nPython in the Browser %s by Michael Foord\n" 
          "Type reset() to clear the console and gohome() to exit.\n" % (sys.version, __version__))
home = 'http://code.google.com/p/trypython/'

ps1 = '>>> '
ps2 = '... '

def _debug(data):
    """Uncomment to output debug info"""
    #HtmlPage.Document.debugging.innerHTML += '<br />%r' % (data,)

# nicely format unhandled exceptions
def excepthook(sender, e):
    print Application.Current.Environment.GetEngine('py').FormatException(e.ExceptionObject)

Application.Current.UnhandledException += excepthook

# Handle infinite recursion gracefully
# CPython default is 1000 - but Firefox can't handle that deep
sys.setrecursionlimit(500)


class Console(InteractiveConsole):
    def write(self, data):
        # Invoke it so that we can print 'safely' from another thread
        # It also makes print asynchronous!
        self.newline_terminated = data.endswith('\n')
        root.Dispatcher.BeginInvoke(lambda: _print(data))

    more = False    
    newline_terminated = True
    
    def handle_key(self, sender, event):
        contents = console_textbox.Text
        start = sender.SelectionStart
        end = start + sender.SelectionLength
        key = event.Key

        pos = contents.rfind('\n') + 5
        if pos > len(contents):
            # Input is screwed - this fixes it
            pos = len(contents)
        
        _debug((start, end, pos, repr(key.value__), key in cursor_keys))
        
        if ((start < pos) or (end < pos)) and (key not in cursor_keys):
            event.Handled = True
            _debug('Skipped')
            return

        if key != Key.Enter:
            if (key in (Key.Delete, Key.Back)) and end <= pos:
                event.Handled = True
                return
            _debug('Delegated')
            TextBox.OnKeyDown(console_textbox, event)
            return
        
        event.Handled = True
        line = contents[pos:]
        
        console.write('\n')
        self.more = console.push(line)

        if self.more:
            prompt = ps2
        else:
            prompt = ps1
            if not self.newline_terminated:
                console.write('\n')

        root.Dispatcher.BeginInvoke(lambda: _print(prompt))

        if self.more:
            prompt = ps2
        else:
            prompt = ps1
            if not self.newline_terminated:
                console.write('\n')


root = Application.Current.RootVisual
textbox_parent = root.consoleParent

class ConsoleTextBox(TextBox):
    def __init__(self):
        self.Width = 450
        self.FontSize = 15
        self.Margin = Thickness(5, 5, 5, 5)
        self.TextWrapping = TextWrapping.Wrap
        self.FontFamily = FontFamily("Consolas, Global Monospace")

    def OnKeyDown(self, event):
        # needed so that we get KeyDown 
        # for del and backspace events etc
        pass
        
console_textbox = ConsoleTextBox()
textbox_parent.Content = console_textbox

def _print(data):
    console_textbox.Text += data
    console_textbox.SelectionStart = len(console_textbox.Text)

    
cursor_keys = (Key.Up, Key.Down, Key.Left, Key.Right)

console = None
def reset():
    global console
    console = Console(context.copy())
    console_textbox.KeyDown += console.handle_key
    def SetBanner():
        console_textbox.Text = banner
        console_textbox.SelectionStart = len(console_textbox.Text)
                  
    root.Dispatcher.BeginInvoke(SetBanner)


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

reset()
sys.stdout = console
sys.stderr = console
console.write(ps1)

_debug('Started')
