from __future__ import with_statement

import sys

# Handle infinite recursion gracefully
# CPython default is 1000 - but Firefox can't handle that deep
sys.setrecursionlimit(500)

from System import EventHandler, Math
from System.Windows import Application
from System.Windows.Browser import HtmlPage, HtmlEventArgs
from System.Windows.Controls import StackPanel, ComboBoxItem, UserControl
from System.Windows.Markup import XamlReader

from consoletextbox import ConsoleTextBox
from context import context
from printer import StatefulPrinter
from utils import invoke, _debug


root = Application.Current.LoadRootVisual(StackPanel(), "app.xaml")
topCombobox = root.topComboBox
bottomCombobox = root.bottomComboBox
console_output = root.consoleOutput
prompt_panel = root.prompt
scroller = root.scroller
textbox_parent = root.consoleParent


def content_resized(sender, event):
    root.Width = width = max(Application.Current.Host.Content.ActualWidth - 25, 700)
    root.Height = height = max(Application.Current.Host.Content.ActualHeight - 25, 700)

    root.document.Width = int(width * 0.53)
    root.container.Height = height - 100
    root.scroller.Width = int(width * 0.44)

Application.Current.Host.Content.Resized += content_resized
content_resized(None, None)
    
# nicely format unhandled exceptions
def excepthook(sender, e):
    error = Application.Current.Environment.GetEngine('py').FormatException(e.ExceptionObject)
    HtmlPage.Document.debugging.innerHTML += error.replace('\n', '<br />')

Application.Current.UnhandledException += excepthook

@invoke
def focus_text_box(sender, event):
    #_debug('focus\n')
    HtmlPage.Plugin.Focus()
    console_textbox.Focus()


printer = StatefulPrinter(console_output, scroller)

console_textbox = ConsoleTextBox(scroller.Width - 75, printer, context)
textbox_parent.Child = console_textbox
console_textbox.reset()

console_output.GotFocus += focus_text_box
scroller.GotFocus += focus_text_box
root.container.GotFocus += focus_text_box


sys.stdout = console_textbox
sys.stderr = console_textbox

with open('list.txt') as handle:
    items = handle.readlines()

for combobox in topCombobox, bottomCombobox:
    for item in items:
        boxitem = ComboBoxItem()
        boxitem.Content = item
        boxitem.Height = 25
        combobox.Items.Add(boxitem)
    
def onChangeTop(sender, event):
    index = topCombobox.SelectedIndex
    bottomCombobox.SelectionChanged -= onChangeBottom
    bottomCombobox.SelectedIndex = index
    bottomCombobox.SelectionChanged += onChangeBottom
    changeDocument(index)
    
def onChangeBottom(sender, event):
    index = bottomCombobox.SelectedIndex
    topCombobox.SelectionChanged -= onChangeTop
    topCombobox.SelectedIndex = index
    topCombobox.SelectionChanged += onChangeTop
    changeDocument(index)

def changeDocument(index):
    page = ''
    if index > 0:
        page = 'page%s' % (index + 1)
    HtmlPage.Window.CurrentBookmark = page
    with open('docs/item%s.xaml' % (index+1)) as handle:
        xaml = handle.read().decode('utf-8')
    document = XamlReader.Load(xaml)
    root.document.Child.Content = document
    root.document.Child.ScrollToVerticalOffset(0)
    focus_text_box(None, None)

topCombobox.SelectionChanged += onChangeTop
bottomCombobox.SelectionChanged += onChangeBottom

page = 0
bookmark = HtmlPage.Window.CurrentBookmark.lower()
if bookmark.startswith('page'):
    try:
        page = int(bookmark[4:])
    except ValueError:
        pass
    else:
        page = min((page - 1), len(combobox.Items) - 1)
        page = max(page, 0)

def first(sender, event):
    topCombobox.SelectedIndex = 0
def last(sender, event):
    topCombobox.SelectedIndex = len(combobox.Items) - 1
def next(sender, event):
    current = combobox.SelectedIndex
    topCombobox.SelectedIndex = min(current + 1, len(combobox.Items) - 1)
def prev(sender, event):
    current = combobox.SelectedIndex
    topCombobox.SelectedIndex = max(current - 1, 0)
    
    
root.topFirst.Click += first
root.bottomFirst.Click += first
root.topLast.Click += last
root.bottomLast.Click += last
root.topNext.Click += next
root.bottomNext.Click += next
root.topPrev.Click += prev
root.bottomPrev.Click += prev
        
topCombobox.SelectedIndex = page
focus_text_box(None, None)


class MouseHandler(object):
    def __init__(self):
        self.position = None
    
    def on_mouse_move(self, sender, event):
        self.position = event.GetPosition(None)
    
    def on_mouse_wheel(self, sender, event):
        mouseDelta = 0
        e = event.EventObject
        if e.GetProperty("detail"):
            mouseDelta = -e.GetProperty("detail")
        elif e.GetProperty("wheelDelta"):
            mouseDelta = e.GetProperty("wheelDelta")
        mouseDelta = Math.Sign(mouseDelta)
    

handler = MouseHandler()
root.MouseMove += handler.on_mouse_move
on_mouse_move = EventHandler[HtmlEventArgs](handler.on_mouse_move)
    
HtmlPage.Window.AttachEvent("DOMMouseScroll", on_mouse_move)
HtmlPage.Window.AttachEvent("onmousewheel", OnMouseWheel)
HtmlPage.Document.AttachEvent("onmousewheel", on_mouse_move)

_debug('Started')
