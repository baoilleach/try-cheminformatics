from __future__ import with_statement

import clr
import sys
clr.AddReferenceToFile('System.Windows.Controls.dll')
clr.AddReferenceToFile('System.Windows.Controls.Toolkit.dll')

from System import EventHandler, Math
from System.Windows import Application
from System.Windows import Point
from System.Windows.Browser import HtmlPage, HtmlEventArgs
from System.Windows.Controls import StackPanel
from System.Windows.Markup import XamlReader

from consoletextbox import ConsoleTextBox
from context import context, title
from mousehandler import MouseHandler
from navigationcontroller import NavigationController
from printer import StatefulPrinter
from utils import invoke, _debug, SetInvokeRoot


root = Application.Current.LoadRootVisual(StackPanel(), "app.xaml")
SetInvokeRoot(root)

console_output = root.consoleOutput
prompt_panel = root.promptPanel
scroller = root.scroller
about = root.about
textbox_parent = root.consoleParent
tab_control = root.tabControl
documentation = root.documentation


def content_resized(sender, event):
    root.Width = width = max(Application.Current.Host.Content.ActualWidth - 25, 800)
    root.Height = height = max(Application.Current.Host.Content.ActualHeight - 25, 500)

    root.document.Width = int(width * 0.53)
    root.container.Height = height - 120
    root.rightSide.Width = int(width * 0.44)
    # XXXX Why do we need to specify this precisely?
    scroller.Width = root.rightSide.Width - 30

Application.Current.Host.Content.Resized += content_resized
content_resized(None, None)
    
# nicely format unhandled exceptions
def excepthook(sender, e):
    error = Application.Current.Environment.GetEngine('py').FormatException(e.ExceptionObject)
    HtmlPage.Document.debugging.innerHTML += error.replace('\n', '<br />')

Application.Current.UnhandledException += excepthook

@invoke
def focus_text_box(sender=None, event=None):
    #_debug('focus\n')
    HtmlPage.Plugin.Focus()
    console_textbox.Focus()


printer = StatefulPrinter(console_output, scroller)

console_textbox = ConsoleTextBox(scroller.Width - 75, printer, context, root)
textbox_parent.Child = console_textbox
console_textbox.reset()

console_output.GotFocus += focus_text_box
scroller.GotFocus += focus_text_box
root.container.GotFocus += focus_text_box

root.title.Text = title
root.title2.Text = title

sys.stdout = console_textbox
sys.stderr = console_textbox

# setup navigationbars
controller = NavigationController(root, focus_text_box)
controller.setup_parts()

# setup mouse wheel handling
scrollers = [root.documentScroller, scroller]
handler = MouseHandler(scrollers)
root.MouseMove += handler.on_mouse_move
on_mouse_wheel = EventHandler[HtmlEventArgs](handler.on_mouse_wheel)

HtmlPage.Window.AttachEvent("DOMMouseScroll", on_mouse_wheel)
HtmlPage.Window.AttachEvent("onmousewheel", on_mouse_wheel)
HtmlPage.Document.AttachEvent("onmousewheel", on_mouse_wheel)


# setup tabcontrol with console, about and documentation
def on_tabpage_changed(sender, event):
    # all stored as module level globals... hmm...
    scrollers.pop()
    if sender.SelectedIndex == 0:
        scrollers.append(scroller)
    if sender.SelectedIndex == 1:
        scrollers.append(about)
    if sender.SelectedIndex == 2:
        scrollers.append(documentation)
        
tab_control.SelectionChanged += on_tabpage_changed
changing_scrollers = [about, documentation, scroller]

with open('docs.xaml') as handle:
    xaml = handle.read().decode('utf-8')
doc_page = XamlReader.Load(xaml)
documentation.Content = doc_page
    
# Handle infinite recursion gracefully
# CPython default is 1000 - but Firefox can't handle that deep
# It also needs to be done after GUI init or it gets reset somewhere along
# the way...
sys.setrecursionlimit(500)

focus_text_box()
