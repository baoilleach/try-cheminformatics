import sys

from System import Uri
from System.Windows import Application
from System.Windows.Browser import HtmlPage
from System.Windows.Controls import TextBox
from System.Windows.Input import Key

from consoletextbox import ConsoleTextBox

from code import InteractiveConsole

__version__ = '0.1.0'

python_version = '.'.join(str(n) for n in sys.version_info[:3])
doc = "Try Python: version %s" % __version__
banner = ("Python %s on Silverlight\nPython in the Browser %s by Michael Foord\n" 
          "Type reset() to clear the console and gohome() to exit.\n" % (python_version, __version__))
home = 'http://code.google.com/p/trypython/'

ps1 = '>>> '
ps2 = '... '

cursor_keys = (Key.Up, Key.Down, Key.Left, Key.Right)

def _debug(data):
    """Comment / uncomment to output debug info"""
    #HtmlPage.Document.debugging.innerHTML += '<br />%r' % (data,)


def _print(data):
    console_textbox.Text += data
    console_textbox.SelectionStart = len(console_textbox.Text)


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
        start = console_textbox.SelectionStart
        end = start + console_textbox.SelectionLength
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
            
            #if key == key.Tab:
                #_debug('Tab')
                #event.Handled = True
                #console_textbox.Text = console_textbox.Text[:sender.SelectionStart] + '    ' + console_textbox.Text[sender.SelectionStart:]
                #return
                
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
console_textbox = ConsoleTextBox()
textbox_parent.Content = console_textbox


console = None
def reset():
    global console
    if console is not None:
        # unhook previous handler
        console_textbox.KeyDown -= console.handle_key
        
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
