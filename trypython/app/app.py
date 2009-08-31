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
topCombobox = root.topComboBox
bottomCombobox = root.bottomComboBox

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

# sets up console
# must be done after loading app.xaml
import console

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
    console.focus_text_box(None, None)

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
console.focus_text_box(None, None)