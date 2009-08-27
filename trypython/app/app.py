from __future__ import with_statement

from System.Windows import Application
from System.Windows.Controls import StackPanel, ComboBoxItem, UserControl
from System.Windows.Markup import XamlReader


Application.Current.LoadRootVisual(StackPanel(), "app.xaml")
root = Application.Current.RootVisual
combobox = root.comboBox

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
    with open('docs/item%s.xaml' % (index+1)) as handle:
        xaml = handle.read()
    document = XamlReader.Load(xaml)
    root.document.Content = document

combobox.SelectionChanged += onChange
combobox.SelectedIndex = 0