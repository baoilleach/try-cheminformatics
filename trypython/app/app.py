from System.Windows import Application
from System.Windows.Controls import StackPanel, ComboBoxItem, UserControl
from System.Windows.Markup import XamlReader

Application.Current.LoadRootVisual(StackPanel(), "app.xaml")
root = Application.Current.RootVisual
combobox = root.comboBox

handle = open('list.txt')
items = handle.readlines()
handle.close()

for item in items:
    boxitem = ComboBoxItem()
    boxitem.Content = item
    boxitem.Height = 25
    combobox.Items.Add(boxitem)
    
def onChange(sender, event):
    index = combobox.SelectedIndex
    handle = open('docs/item%s.xaml' % (index+1))
    xaml = handle.read()
    handle.close()
    document = XamlReader.Load(xaml)
    root.document.Child = document

combobox.SelectionChanged += onChange
combobox.SelectedIndex = 0