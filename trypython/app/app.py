from __future__ import with_statement

import sys

# Handle infinite recursion gracefully
# CPython default is 1000 - but Firefox can't handle that deep
sys.setrecursionlimit(500)

from System.Windows import Application
from System.Windows.Browser import HtmlPage
from System.Windows.Controls import StackPanel, ComboBoxItem, UserControl
from System.Windows.Markup import XamlReader


Application.Current.LoadRootVisual(StackPanel(), "app.xaml")
root = Application.Current.RootVisual
combobox = root.comboBox

def content_resized(sender, event):
    root.Width = width = max(Application.Current.Host.Content.ActualWidth - 25, 700)
    root.Height = height = max(Application.Current.Host.Content.ActualHeight - 25, 700)

    root.document.Width = int(width * 0.53)
    root.document.Height = height - 90
    root.scroller.Width = int(width * 0.44)
    root.scroller.Height = height - 90

Application.Current.Host.Content.Resized += content_resized
content_resized(None, None)
    
# nicely format unhandled exceptions
def excepthook(sender, e):
    error = Application.Current.Environment.GetEngine('py').FormatException(e.ExceptionObject)
    HtmlPage.Document.debugging.innerHTML += error.replace('\n', '<br />')

Application.Current.UnhandledException += excepthook

# sets up console
# must be done after loading app.xaml
import console

with open('list.txt') as handle:
    items = handle.readlines()

for item in items:
    boxitem = ComboBoxItem()
    boxitem.Content = item
    boxitem.Height = 25
    combobox.Items.Add(boxitem)
    
def onChange(sender, event):
    index = combobox.SelectedIndex
    HtmlPage.Window.CurrentBookmark = 'page%s' % (index + 1)
    with open('docs/item%s.xaml' % (index+1)) as handle:
        xaml = handle.read()
    document = XamlReader.Load(xaml)
    root.document.Content = document
    root.document.ScrollToVerticalOffset(0)
    console.focus_text_box(None, None)

combobox.SelectionChanged += onChange

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
        
combobox.SelectedIndex = page
console.focus_text_box(None, None)