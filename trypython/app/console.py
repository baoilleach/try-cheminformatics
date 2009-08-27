
import sys

from System import Uri
from System.Windows import Application
from System.Windows.Browser import HtmlPage
from System.Windows.Input import Key

from code import InteractiveConsole

__version__ = '0.1.0'

doc = "Try Python: version %s" % __version__
banner = ("Python %s on Silverlight\nPython in the Browser %s by Michael Foord\n" 
          "Type reset() to clear the console and gohome() to exit.\n" % (sys.version, __version__))
home = 'http://code.google.com/p/trypython/'

ps1 = '>>> '
ps2 = '... '

def _debug(data):
    HtmlPage.Document.debugging.innerHTML += '<br />%r' % (data,)

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
        global newline_terminated
        newline_terminated = data.endswith('\n')
        root.Dispatcher.BeginInvoke(lambda: _print(data))

newline_terminated = True

root = Application.Current.RootVisual
consoleOut = root.consoleOut
consoleIn = root.consoleIn

def _print(data):
    consoleOut.Text += data
    consoleOut.SelectionStart = len(consoleOut.Text)

class HandleEnter(object):
    
    more = False
    
    def handle_key(self, sender, event):
        contents = consoleOut.Text
        start = sender.SelectionStart
        end = start + sender.SelectionLength
        key = event.Key

        pos = contents.rfind('\n') + 5
        if pos > len(contents):
            # Input is screwed - this fixes it
            pos = len(contents)
        
        _debug((start, end, pos, key))
        
        if (start < pos) or (end < pos):
            event.Handled = True
            return
        if key == Key.Delete and end <= pos:
            event.Handled = True
            return
        if key != Key.Enter:
            return
        
        line = contents[pos:]
        
        console.write('\n')
        self.more = console.push(line)

        if self.more:
            prompt = ps2
        else:
            prompt = ps1
            if not newline_terminated:
                console.write('\n')

        root.Dispatcher.BeginInvoke(lambda: _print(prompt))

        if self.more:
            prompt = ps2
        else:
            prompt = ps1
            if not newline_terminated:
                console.write('\n')

        root.Dispatcher.BeginInvoke(lambda: _print(prompt))

handler = HandleEnter()
root.consoleOut.KeyDown += handler.handle_key

console = None
def reset():
    global console
    console = Console(context.copy())
    def SetBanner():
        consoleOut.Text = banner
        consoleOut.SelectionStart = len(consoleOut.Text)
                  
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
