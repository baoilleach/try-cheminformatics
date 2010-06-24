from __future__ import with_statement

import re
import sys
import webel

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
from utils import always_invoke, _debug, SetInvokeRoot, load_document

import storage
import storage_backend
from storage import original_open as open
storage.backend = storage_backend
storage.replace_builtins()

# create the example files
if not storage_backend.CheckForFile('myfile.txt'):
    h = storage.open('myfile.txt', 'w')
    h.write("""This is a text file.
    You can read it.
    It exists.
    """)
    h.close()
if not storage_backend.CheckForFile('workfile'):
    h = storage.open('workfile', 'w')
    h.write('This is the entire file.\n')
    h.close()
if not storage_backend.CheckForFile('workfile2'):
    h = storage.open('workfile2', 'w')
    h.write('This is the first line of the file.\nSecond line of the file\n')
    h.close()
if not storage_backend.CheckForFile('example.sdf'):
    h = storage.open('example.sdf', 'w')
    h.write("""2-Methyl-1,4-benzoquinone
 OpenBabel11110909233D
CORINA 2.61 0041  25.10.2001
 15 15  0  0  0  0  0  0  0  0999 V2000
    0.0021   -0.0041    0.0020 O   0  0  0  0  0
   -0.0691    5.2414    0.0323 O   0  0  0  0  0
   -0.0144    1.2102    0.0087 C   0  0  0  0  0
   -1.3034    1.9312    0.0310 C   0  0  0  0  0
    1.2546    1.9661    0.0006 C   0  0  0  0  0
   -1.3215    3.2712    0.0389 C   0  0  0  0  0
    1.2365    3.3061    0.0085 C   0  0  0  0  0
   -0.0526    4.0271    0.0252 C   0  0  0  0  0
   -2.5980    1.1600    0.0445 C   0  0  0  0  0
    2.1971    1.4389   -0.0112 H   0  0  0  0  0
   -2.2641    3.7984    0.0511 H   0  0  0  0  0
    2.1643    3.8588   -0.0015 H   0  0  0  0  0
   -2.3843    0.0912    0.0355 H   0  0  0  0  0
   -3.1608    1.4105    0.9438 H   0  0  0  0  0
   -3.1853    1.4206   -0.8360 H   0  0  0  0  0
  1  3  2  0  0  0
  2  8  2  0  0  0
  3  5  1  0  0  0
  3  4  1  0  0  0
  4  6  2  0  0  0
  4  9  1  0  0  0
  5  7  2  0  0  0
  5 10  1  0  0  0
  6  8  1  0  0  0
  6 11  1  0  0  0
  7  8  1  0  0  0
  7 12  1  0  0  0
  9 13  1  0  0  0
  9 14  1  0  0  0
  9 15  1  0  0  0
M  END
>  <NSC>
1

>  <logP>
0.6407

$$$$
2,2'-Benzothiazyl disulfide
 OpenBabel11110909233D
CORINA 2.61 0041  25.10.2001
 28 31  0  0  0  0  0  0  0  0999 V2000
   -0.0165    1.3666    0.0096 C   0  0  0  0  0
    8.2041    6.9305    2.5032 C   0  0  0  0  0
    0.0021   -0.0041    0.0020 C   0  0  0  0  0
    1.1892    2.1056    0.0020 C   0  0  0  0  0
    2.5286    4.0208   -0.0013 C   0  0  0  0  0
    4.7319    5.7338    2.3165 C   0  0  0  0  0
    7.0224    6.1538    2.5156 C   0  0  0  0  0
    9.4205    6.3592    2.7733 C   0  0  0  0  0
    1.1946   -0.7124   -0.0132 C   0  0  0  0  0
    2.3840    1.3506   -0.0135 C   0  0  0  0  0
    7.1801    4.7823    2.8185 C   0  0  0  0  0
    9.5376    5.0085    3.0668 C   0  0  0  0  0
    2.3930   -0.0213   -0.0210 C   0  0  0  0  0
    8.4019    4.2188    3.0869 C   0  0  0  0  0
    5.7567    6.5587    2.2741 N   0  0  0  0  0
    5.5106    4.1804    2.7344 S   0  0  0  0  0
    3.0264    6.0746    2.0342 S   0  0  0  0  0
    2.9255    5.7375    0.0045 S   0  0  0  0  0
    3.6321    2.6151   -0.0192 S   0  0  0  0  0
    1.3439    3.4473    0.0074 N   0  0  0  0  0
   -0.9624    1.8878    0.0169 H   0  0  0  0  0
    8.1482    7.9844    2.2740 H   0  0  0  0  0
   -0.9329   -0.5446    0.0084 H   0  0  0  0  0
   10.3079    6.9745    2.7570 H   0  0  0  0  0
    1.1876   -1.7924   -0.0186 H   0  0  0  0  0
   10.5055    4.5777    3.2764 H   0  0  0  0  0
    3.3299   -0.5584   -0.0325 H   0  0  0  0  0
    8.4764    3.1655    3.3136 H   0  0  0  0  0
  1  3  2  0  0  0
  1  4  1  0  0  0
  1 21  1  0  0  0
  2  8  2  0  0  0
  2  7  1  0  0  0
  2 22  1  0  0  0
  3  9  1  0  0  0
  3 23  1  0  0  0
  4 10  2  0  0  0
  4 20  1  0  0  0
  5 18  1  0  0  0
  5 20  2  0  0  0
  5 19  1  0  0  0
  6 17  1  0  0  0
  6 15  2  0  0  0
  6 16  1  0  0  0
  7 15  1  0  0  0
  7 11  2  0  0  0
  8 12  1  0  0  0
  8 24  1  0  0  0
  9 13  2  0  0  0
  9 25  1  0  0  0
 10 19  1  0  0  0
 10 13  1  0  0  0
 11 16  1  0  0  0
 11 14  1  0  0  0
 12 14  2  0  0  0
 12 26  1  0  0  0
 13 27  1  0  0  0
 14 28  1  0  0  0
 17 18  1  0  0  0
M  END
>  <NSC>
2

>  <logP>
5.7054

$$$$
""")
    h.close()

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
    documentContainer.Content.Width = root.document.Width - 50

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

title = 'Try Python: %s'

@always_invoke
def change_title():
    if topComboBoxPart.SelectedIndex == 0:
        fragment = 'Interactive Cheminformatics Tutorial'
    else:
        fragment = topComboBoxPart.SelectedItem.Content
        if topComboBoxPage.SelectedIndex != 0:
            fragment = topComboBoxPage.SelectedItem.Content
    HtmlPage.Document.SetProperty('title', title % fragment)
    
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
        document = load_document(path, page, console_textbox)
        _xaml_cache[path] = document
        if page < 1:
            add_stackpanel(document, get_list(loc + 'list.txt'))
    
    HtmlPage.Window.CurrentBookmark = fragment
    
    documentContainer.Content = document 
    document.Width = documentContainer.Width - 30
    
    @always_invoke
    def scroll_and_focus():
        documentContainer.ScrollToVerticalOffset(0)
        focus_text_box()
    scroll_and_focus()
    change_title()

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
    part = topComboBoxPart.SelectedIndex
    page = topComboBoxPage.SelectedIndex
    
    unhook_events()
    bottomComboBoxPage.SelectedIndex = page
    change_document(part, page)
    hook_events()


def on_change_bottom_page(sender, event):
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
