from __future__ import with_statement

import clr
import re
import sys
clr.AddReferenceToFile('System.Windows.Controls.dll')
clr.AddReferenceToFile('System.Windows.Controls.Toolkit.dll')

from System import EventHandler, Math, Uri
from System.Windows import Application, Thickness
from System.Windows import Point
from System.Windows.Browser import HtmlPage, HtmlEventArgs
from System.Windows.Controls import (
    HyperlinkButton, ComboBoxItem, Orientation,
    StackPanel, TextBlock
)
from System.Windows.Markup import XamlReader
from System.Windows.Media import FontFamily

from consoletextbox import ConsoleTextBox
from context import context, title
from mousehandler import MouseHandler
from printer import StatefulPrinter
from utils import always_invoke, _debug, SetInvokeRoot

import utils
# Comment / uncomment this line to output debug info
#utils.debug = True

root = Application.Current.LoadRootVisual(StackPanel(), "app.xaml")
SetInvokeRoot(root)

console_output = root.consoleOutput
prompt_panel = root.promptPanel
scroller = root.scroller
about = root.about
textbox_parent = root.consoleParent
tab_control = root.tabControl
documentation = root.documentation
documentContainer = root.documentScroller


def content_resized(sender=None, event=None):
    root.Width = width = max(Application.Current.Host.Content.ActualWidth - 25, 800)
    root.Height = height = max(Application.Current.Host.Content.ActualHeight - 25, 500)

    root.document.Width = int(width * 0.53)
    root.container.Height = height - 120
    root.rightSide.Width = int(width * 0.44)
    # XXXX Why do we need to specify this precisely?
    scroller.Width = root.rightSide.Width - 30
    documentContainer.Width = root.document.Width - 20

Application.Current.Host.Content.Resized += content_resized
    
# nicely format unhandled exceptions
def excepthook(sender, e):
    error = Application.Current.Environment.GetEngine('py').FormatException(e.ExceptionObject)
    HtmlPage.Document.debugging.innerHTML += error.replace('\n', '<br />')

Application.Current.UnhandledException += excepthook

@always_invoke
def focus_text_box(sender=None, event=None):
    #_debug('focus\n')
    HtmlPage.Plugin.Focus()
    console_textbox.Focus()


printer = StatefulPrinter(console_output, scroller, root.prompt)

console_textbox = ConsoleTextBox(printer, context, root)
textbox_parent.Child = console_textbox
console_textbox.reset()

console_output.GotFocus += focus_text_box
scroller.GotFocus += focus_text_box

root.title.Text = title
root.title2.Text = title

sys.stdout = console_textbox
sys.stderr = console_textbox

# setup mouse wheel handling
scrollers = [root.documentScroller, scroller]
handler = MouseHandler(root, scrollers)
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
        focus_text_box()
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


###########################################
# setup navigationbars
# can't be done in a class or event unhooking
# doesn't seem to work :-(

_xaml_cache = {}

topComboBoxPage = root.topComboBoxPage
bottomComboBoxPage = root.bottomComboBoxPage
topComboBoxPart = root.topComboBoxPart
bottomComboBoxPart = root.bottomComboBoxPart

def _get_text_block(text):
    block = TextBlock()
    block.FontSize = 15
    block.FontFamily = FontFamily("Verdana,Tahoma,Geneva,Lucida Grande,Trebuchet MS,Helvetica,Arial,Serif")
    block.Text = text
    return block

def add_stackpanel(document, items):
    panel = StackPanel()
    document.Children.Add(panel)
    panel.Margin = Thickness(10)
    for i, item in enumerate(items):
        item_panel = StackPanel()
        item_panel.Margin = Thickness(2)
        item_panel.Orientation = Orientation.Horizontal
        panel.Children.Add(item_panel)
        
        text = _get_text_block(u'\u2022\u00a0')
        item_panel.Children.Add(text)
        
        def goto_page(s, e, page=i+1):
            _debug('goto', page)
            if topComboBoxPart.SelectedIndex == 0:
                topComboBoxPart.SelectedIndex = page
            else:
                topComboBoxPage.SelectedIndex = page
        
        button = HyperlinkButton()
        item_panel.Children.Add(button)
        button.Content = _get_text_block(item)
        button.Click += goto_page


def setup_parts():
    items = get_list('docs/list.txt')

    topCombobox = topComboBoxPart
    bottomComboBox = bottomComboBoxPart
    
    items = ['Index'] + items
    for combobox in topCombobox, bottomComboBox:
        for item in items:
            boxitem = ComboBoxItem()
            boxitem.Content = item
            boxitem.Height = 25
            combobox.Items.Add(boxitem)
    
    topCombobox.SelectionChanged += on_change_top_part
    bottomComboBox.SelectionChanged += on_change_bottom_part
    
    topCombobox.SelectedIndex = bottomComboBox.SelectedIndex = 0
    
    
def unhook_events():
    bottomComboBoxPart.SelectionChanged -= on_change_bottom_part
    topComboBoxPart.SelectionChanged -= on_change_top_part
    
    topComboBoxPage.SelectionChanged -= on_change_top_page
    bottomComboBoxPage.SelectionChanged -= on_change_bottom_page


def hook_events():
    bottomComboBoxPart.SelectionChanged += on_change_bottom_part
    topComboBoxPart.SelectionChanged += on_change_top_part
    
    topComboBoxPage.SelectionChanged += on_change_top_page
    bottomComboBoxPage.SelectionChanged += on_change_bottom_page
    

def change_document(part, page):
    fragment = ''
    item = 'index.xaml'
    loc = 'docs/'
    if part > 0:
        # page can be -1
        if page > 0:
            item = 'item%s.xaml' % page
            fragment = 'part%s-page%s' % (part, page)
        else:
            fragment = 'part%s' % part
        loc += 'part%s/' % part
        
    
    path = loc + item
    
    if path in _xaml_cache:
        document = _xaml_cache[path]
    else:
        with open(path) as handle:
            xaml = handle.read().decode('utf-8')
        document = XamlReader.Load(xaml)
        _xaml_cache[path] = document
        
        if page < 1:
            add_stackpanel(document, get_list(loc + 'list.txt'))
    
    HtmlPage.Window.CurrentBookmark = fragment
    
    documentContainer.Content = document 
    document.Width = documentContainer.Width - 30
    documentContainer.ScrollToVerticalOffset(0)
    focus_text_box()


def on_change_top_part(sender, event):
    index = topComboBoxPart.SelectedIndex
    unhook_events()
    bottomComboBoxPart.SelectedIndex = index
    change_pages()
    change_document(index, 0)
    hook_events()
    
    
def on_change_bottom_part(sender, event):
    index = bottomComboBoxPart.SelectedIndex
    unhook_events()
    topComboBoxPart.SelectedIndex = index
    change_pages()
    change_document(index, 0)
    hook_events()


def get_list(path):
    with open(path) as handle:
        items = handle.readlines()
    return items


def change_pages():
    unhook_events()
    part = topComboBoxPart.SelectedIndex
    
    unhook_events()
    topComboBoxPage.Items.Clear()
    bottomComboBoxPage.Items.Clear()
    if part == 0:
        return
    
    items = get_list('docs/part%s/list.txt' % part)

    topCombobox = topComboBoxPage
    bottomComboBox = bottomComboBoxPage
    
    items = ['Index'] + items
    for combobox in topCombobox, bottomComboBox:
        for item in items:
            boxitem = ComboBoxItem()
            boxitem.Content = item
            boxitem.Height = 25
            combobox.Items.Add(boxitem)
    
    topComboBoxPage.SelectedIndex = 0
    bottomComboBoxPage.SelectedIndex = 0
    hook_events()
    

def on_change_top_page(sender, event):
    _debug('change_top')
    part = topComboBoxPart.SelectedIndex
    page = topComboBoxPage.SelectedIndex
    
    unhook_events()
    bottomComboBoxPage.SelectedIndex = page
    change_document(part, page)
    hook_events()


def on_change_bottom_page(sender, event):
    _debug('change_bottom')
    part = bottomComboBoxPart.SelectedIndex
    page = bottomComboBoxPage.SelectedIndex
    
    unhook_events()
    topComboBoxPage.SelectedIndex = page
    change_document(part, page)
    hook_events()


def next(sender, event):
    part = topComboBoxPart.SelectedIndex
    page = topComboBoxPage.SelectedIndex
    
    if page < len(topComboBoxPage.Items) - 1:
        topComboBoxPage.SelectedIndex += 1
    elif part < len(topComboBoxPart.Items) - 1:
        topComboBoxPart.SelectedIndex += 1


def prev(sender, event):
    part = topComboBoxPart.SelectedIndex
    page = topComboBoxPage.SelectedIndex
    
    if page > 0:
        topComboBoxPage.SelectedIndex -= 1
    elif part > 0:
        topComboBoxPart.SelectedIndex -= 1
        if part > 1:
            index = len(get_list('docs/part%s/list.txt' % part))
            topComboBoxPage.SelectedIndex = index


def first(sender, event):
    if topComboBoxPart.SelectedIndex > 0:
        topComboBoxPage.SelectedIndex = 0


def last(sender, event):
    if topComboBoxPart.SelectedIndex > 0:
        topComboBoxPage.SelectedIndex = len(topComboBoxPage.Items) - 1

def set_page(part, page):
    topComboBoxPart.SelectedIndex = part
    if page is not None:
        topComboBoxPage.SelectedIndex = page
    
root.topFirst.Click += first
root.bottomFirst.Click += first
root.topLast.Click += last
root.bottomLast.Click += last
root.topNext.Click += next
root.bottomNext.Click += next
root.topPrev.Click += prev
root.bottomPrev.Click += prev

###########################################
# needed for one of the tutorial examples
import fibo


page = 0
part = 0
bookmark = HtmlPage.Window.CurrentBookmark.lower()
page_re = r'page(\d+)'
part_re = r'part(\d+)'
match = re.match(part_re, bookmark)
if match:
    part = int(match.groups()[0])
match = re.search(page_re, bookmark)
if match:
    page = int(match.groups()[0])


# Handle infinite recursion gracefully
# CPython default is 1000 - but Firefox can't handle that deep
# It also needs to be done after GUI init or it gets reset somewhere along
# the way...
sys.setrecursionlimit(500)

setup_parts()
content_resized()
console_textbox.Width = scroller.Width - 75
if part > 0:
    try:
        set_page(part, page)
    except ValueError:
        HtmlPage.Window.CurrentBookmark = ''
        set_page(0, None)

focus_text_box()
