# Copyright (c) 2007-8 Michael Foord.
# All Rights Reserved
#

import sys
import clr
clr.AddReference("OnKeyPress, Version=0.0.0.0, Culture=neutral, PublicKeyToken=null")

from OnKeyPress import OnKeyPress

from System import Uri
from System.Windows import Application
from System.Windows.Browser import HtmlPage
from System.Windows.Controls import Canvas

from code import InteractiveConsole

__version__ = '0.2.0'
doc = "Python in the browser: version %s" % __version__
banner = ("Python %s on Silverlight\nPython in the Browser %s by Michael Foord\n" 
          "Type reset() to clear the console and gohome() to exit.\n" % (sys.version, __version__))
home = 'http://code.google.com/p/pythoninthebrowser/'

ps1 = '>>> '
ps2 = '... '
root = Canvas()


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

def _print(data):
    HtmlPage.Document.interpreter.value += data
    height = HtmlPage.Document.interpreter.GetProperty('scrollHeight')
    if height:
        HtmlPage.Document.interpreter.SetProperty('scrollTop', height)


class HandleKeyPress(OnKeyPress):
    
    more = False
    
    def _method(self, start, end, key):
        contents = HtmlPage.Document.interpreter.value or ''
        pos = contents.rfind('\n') + 5
        if pos > len(contents):
            # Input is screwed - this fixes it
            pos = len(contents)
        
        #HtmlPage.Document.debugging.innerHTML = 'Start: ' + str(start) + ' End: ' + str(end) + ' Pos: ' + str(pos) + '<p>'
        if (start < pos) or (end < pos):
            #HtmlPage.Document.debugging.innerHTML += '<br /> Key=%s Ord=%s' % (key, ord(key))
            return 'false'
        if ord(key) == 8 and end <= pos:
            return 'false'
        if key not in '\r\n': # IE sends \r - go figure...
            return 'true'
        
        #HtmlPage.Document.debugging.innerHTML += ' Enter... '
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
        return 'false'


onkeypress = HandleKeyPress()

HtmlPage.RegisterScriptableObject("onkeypress", onkeypress)


console = None
def reset():
    global console
    console = Console(context.copy())
    def SetBanner():
        HtmlPage.Document.interpreter.value = banner
                  
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

HtmlPage.Document.interpreter.SetProperty('disabled', False)
HtmlPage.Document.SilverlightControlHost.SetStyleAttribute('visible', 'false')
Application.Current.RootVisual = root

# Setup examples
from System import EventHandler

code1 = """>>> 
>>> dictionary = {"Key 1":"value 1", "key 2":"value 2", "key 3":"value 3", "key 4":"value 4"} 
>>> """
code1_html = """<pre style='color:#000000;background:#ffffff;'>dictionary <span style='color:#808030; '>=</span> <span style='color:#800080; '>{</span><span style='color:#0000e6; '>"Key 1"</span><span style='color:#808030; '>:</span><span style='color:#0000e6; '>"value 1"</span><span style='color:#808030; '>,</span> <span style='color:#0000e6; '>"key 2"</span><span style='color:#808030; '>:</span><span style='color:#0000e6; '>"value 2"</span><span style='color:#808030; '>,</span> <span style='color:#0000e6; '>"key 3"</span><span style='color:#808030; '>:</span><span style='color:#0000e6; '>"value 3"</span><span style='color:#808030; '>,</span> <span style='color:#0000e6; '>"key 4"</span><span style='color:#808030; '>:</span><span style='color:#0000e6; '>"value 4"</span><span style='color:#800080; '>}</span> 

<span style='color:#800000; font-weight:bold; '>print</span> dictionary<span style='color:#808030; '>.</span>items<span style='color:#808030; '>(</span><span style='color:#808030; '>)</span>
<span style='color:#800000; font-weight:bold; '>print</span> <span style='color:#808030; '>[</span>k <span style='color:#800000; font-weight:bold; '>for</span> k<span style='color:#808030; '>,</span> v <span style='color:#800000; font-weight:bold; '>in</span> dictionary<span style='color:#808030; '>.</span>items<span style='color:#808030; '>(</span><span style='color:#808030; '>)</span><span style='color:#808030; '>]</span>
<span style='color:#800000; font-weight:bold; '>print</span> <span style='color:#808030; '>[</span>v <span style='color:#800000; font-weight:bold; '>for</span> k<span style='color:#808030; '>,</span> v <span style='color:#800000; font-weight:bold; '>in</span> dictionary<span style='color:#808030; '>.</span>items<span style='color:#808030; '>(</span><span style='color:#808030; '>)</span><span style='color:#808030; '>]</span> 
<span style='color:#800000; font-weight:bold; '>print</span> <span style='color:#808030; '>[</span><span style='color:#0000e6; '>"%s=%s"</span> <span style='color:#808030; '>%</span> <span style='color:#808030; '>(</span>k<span style='color:#808030; '>,</span> v<span style='color:#808030; '>)</span> <span style='color:#800000; font-weight:bold; '>for</span> k<span style='color:#808030; '>,</span> v <span style='color:#800000; font-weight:bold; '>in</span> dictionary<span style='color:#808030; '>.</span>items<span style='color:#808030; '>(</span><span style='color:#808030; '>)</span><span style='color:#808030; '>]</span>
</pre>"""

code2 = """>>> 
>>> def make_adder(first):
...     def adder(second):
...         return first + second
...      return adder
... 
>>> """

code2_html = """<pre style='color:#000000;background:#ffffff;'><span style='color:#800000; font-weight:bold; '>def</span> make_adder<span style='color:#808030; '>(</span>first<span style='color:#808030; '>)</span><span style='color:#808030; '>:</span>
    <span style='color:#800000; font-weight:bold; '>def</span> adder<span style='color:#808030; '>(</span>second<span style='color:#808030; '>)</span><span style='color:#808030; '>:</span><span style='color:#808030; '>:</span>
        <span style='color:#800000; font-weight:bold; '>return</span> first <span style='color:#808030; '>+</span> second
    <span style='color:#800000; font-weight:bold; '>return</span> adder

add2 <span style='color:#808030; '>=</span> make_adder<span style='color:#808030; '>(</span><span style='color:#008c00; '>2</span><span style='color:#808030; '>)</span>
<span style='color:#e34adc; '>type</span><span style='color:#808030; '>(</span>add2<span style='color:#808030; '>)</span>
add2<span style='color:#808030; '>(</span><span style='color:#008c00; '>3</span><span style='color:#808030; '>)</span>
</pre>"""

def restore(*_):
    reset()
    console.write(ps1)
    HtmlPage.Document.example_output.SetStyleAttribute('visible', 'false')
    HtmlPage.Document.example_output.innerHTML = ''

def example1(*_):
    global console
    new_locals = context.copy()
    dictionary = {"Key 1":"value 1", "key 2":"value 2", "key 3":"value 3", "key 4":"value 4"} 
    new_locals['dictionary'] = dictionary
    console = Console(new_locals)
    
    HtmlPage.Document.interpreter.value = banner + code1
    HtmlPage.Document.example_output.SetStyleAttribute('visible', 'true')
    HtmlPage.Document.example_output.innerHTML = '<p>Type the following:</p>' + code1_html
                  

def example2(*_):
    global console
    new_locals = context.copy()
    
    def make_adder(first):
        def adder(second):
            return first + second
        return adder
        
    new_locals['make_adder'] = make_adder
    console = Console(new_locals)
    
    HtmlPage.Document.interpreter.value = banner + code2
    HtmlPage.Document.example_output.SetStyleAttribute('visible', 'true')
    HtmlPage.Document.example_output.innerHTML = '<p>Type the following:</p>' + code2_html
    
    
if hasattr(HtmlPage.Document, 'examples'):
    HtmlPage.Document.restore.AttachEvent('onclick', EventHandler(restore))
    HtmlPage.Document.example1.AttachEvent('onclick', EventHandler(example1))
    HtmlPage.Document.example2.AttachEvent('onclick', EventHandler(example2))
    